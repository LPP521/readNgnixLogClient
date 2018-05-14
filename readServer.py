#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @version : 1.0
# @Time    : 2018/1/14 14:55
# @Author  : chenjh
# @File    : readServer.py
# @Software: PyCharm
# @note    : 读取ngnix文件服务
'''
http://blog.csdn.net/hackstoic/article/details/49804655
http://blog.csdn.net/my2010sam/article/details/38022041
'''

from Model.myRedis import my_redis
import re, time, os, socket
from Config.conf import getConf
import urllib
import threading, json
import platform

class TNginxLog(object):

    def __init__(self, file_name):
        self.re = self._get_re()  # 正则
        self.queue_name = getConf('queue_name')
        self.log_path = getConf('log_path')
        self.month_eng = getConf('month_eng')
        self.filter_url = getConf('filter_url')
        self.client_version = getConf('client_version')

        self.file_name = file_name
        self.file_path = self.log_path + file_name
        self.ip = self._get_ip()
        self.file_line_redis_prefix = str(self.ip).replace('.','_')  #读取前缀
        # 当天生成备份中路径
        date = self.get_now_date()
        self.bakfile_path  = self.log_path + "bak/"+time.strftime('%Y/%m/%d/', date)
        self.now_date = time.strftime('%Y%m%d', date)
        self.my_redis = my_redis

    def _get_ip(self) :
        if platform.system() == "Windows":
            str_replace_ip = socket.gethostbyname(socket.gethostname())
        else:
            import psutil
            info = psutil.net_if_addrs()
            str_replace_ip = ""
            for k,v in info.items():
                if str_replace_ip <> "" :
                     break
                for item in v:
                    if item[0] == 2  and item[1][0:7] == '192.168':
                          str_replace_ip = item[1]
                          break
        return str_replace_ip

    def _get_re(self):
        '''
        对单条日志进行获取-正则匹配
        '''
        ip = r"?P<ip>[.\d+]*"
        user_id = r"?P<user_id>[1-9].*"
        param = r"?P<param>\S+"
        date = r"?P<date>\d+"
        month = r"?P<month>\w+"
        year = r"?P<year>\d+"
        log_time = r"?P<time>\S+"
        method = r"?P<method>\S+"
        request = r"?P<request>\S+"
        status = r"?P<status>2[0-9]{2}"
        userAgent = r"?P<userAgent>.*"
        domain = r"?P<domain>\S+"
        return re.compile(r"(%s)\ (%s)\ (%s)\ \"-\"\ \[(%s)/(%s)/(%s)\:(%s)\ [\S]+\]\ \"(%s)\s(%s)?.*?\ (%s)\ \"(%s)\"\ \"-\"\ \"(%s)\"  " \
                      %(ip, user_id, param, date, month, year, log_time, method, request, status, userAgent,domain), re.VERBOSE)

    def _get_insert_redis_data(self, new_list = []):
        data = {}
        if new_list != []:
            datatime = new_list[5] + "-" + self.month_eng[new_list[4]] + "-" + new_list[3] + " " + new_list[6]
            url = new_list[11] + new_list[8]
            paramValue = urllib.unquote(new_list[2]).decode('utf-8', 'replace')
            data['ip'] = new_list[0]
            data['param'] = paramValue
            data['user_id'] = new_list[1]
            data['datatime'] = datatime
            data['method'] = new_list[7]
            data['status'] = new_list[9]
            data['userAgent'] = new_list[10]
            data['url'] = url
            data['domain'] = new_list[11]
            data['read_version_id'] = self.client_version
            data['read_ip'] = self.ip
        return data

    def read_redis_int(self,arg):
        tmp = self.my_redis.get(arg)
        if tmp is None:
            return 0
        else:
            return int(tmp)

    def read_in_block(self, file_path):
        '''
        行读取文件信息
        '''
        iline = self.read_redis_int(self.get_redis_prefix('line'));   # 读取行数
        place = self.read_redis_int(self.get_redis_prefix('place'));

        self.print_log('-' * 20 + 'read inline_' + str(iline) + '_place_' + str(place) + '-' * 20)
        with open(file_path, "r") as f:
            if place != 0:
                f.seek(place,0)
            while True:
                block = f.readline()
                place = f.tell()
                if block:
                    iline = iline + 1
                    m = re.findall(self.re, block)
                    if m:
                        if m[0][1] and m[0][1].isdigit() and m[0][1] != '0':
                            new_list = list(m[0])
                            is_break = 0
                            for i in self.filter_url:
                                if i in new_list[8]:
                                    is_break = 1
                                    break
                            if is_break == 1:
                                continue
                            data = self._get_insert_redis_data(new_list)
                            if data:
                                data_json = json.dumps(data)
                                self.my_redis.lpush(self.queue_name,data_json)
                            del new_list, data
                            self. my_redis.add(self.get_redis_prefix('line'), iline)
                            self.my_redis.add(self.get_redis_prefix('place'), place)
                        else:
                            pass
                    else:
                        pass
                else:
                    self.my_redis.add(self.get_redis_prefix('line'),iline)
                    self.my_redis.add(self.get_redis_prefix('place'),place)
                    return  # 如果读取到文件末尾，则退出e

    def get_now_date(self):
        ltime = time.time()
        return time.localtime(ltime)

    def get_redis_prefix(self, arg):
        return self.now_date + "_" + self.file_line_redis_prefix + self.file_name + '_' + arg

    def process_nginxLog(self):
        place_filesize = self.read_redis_int(self.get_redis_prefix('place'))
        filesize = os.path.getsize(self.file_path)
        if filesize != place_filesize and filesize != 0:
            self.print_log("in procese file")
            self.read_in_block(self.file_path)
            self.print_log("out procese file")

    def process_bakfile(self):
        if self.read_redis_int(self.get_redis_prefix("bak_finish")) == 1:
            self.print_log("bak_finish")
            return
        cur_bakfile_path = self.log_path + "bak/"+time.strftime('%Y/%m/%d/', self.get_now_date())
        if self.bakfile_path <> cur_bakfile_path:
            if os.path.exists(self.bakfile_path):  #备份文件已生成
                time.sleep(10)
                file_path = self.bakfile_path + self.file_name
                if os.path.exists(file_path):
                    if os.path.getsize(file_path) != 0:
                        self.print_log("in bak")
                        self.my_redis.add(self.get_redis_prefix('bak_finish'), 0)
                        self.read_in_block(file_path)
                        self.my_redis.add(self.get_redis_prefix('bak_finish'), 1)
                        self.now_date = time.strftime('%Y%m%d', self.get_now_date())  #获取当前日期
                        self.bakfile_path = cur_bakfile_path
                        self.print_log("out bak")
    def run(self):
        while 1:
            try:
                self.process_nginxLog()
                self.process_bakfile()
                time.sleep(10)
                self.print_log('read over')
            except Exception, e:
                self.print_log(e)
                time.sleep(20)

    def print_log(self,arg):
        print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),self.file_name,arg

class Read_log_Thread(threading.Thread):

    def __init__(self,NginxLog):
        super(Read_log_Thread, self).__init__()  #注意：一定要显式的调用父类的初始化函数。
        self.NginxLog = NginxLog

    def run(self):  #定义每个线程要运行的函数
        self.NginxLog.run()
            
if __name__ == '__main__':

    check_file_name = getConf('ngnix_file')
    log_path = getConf('log_path')
    thread_list = []    #线程存放列表

    for file_name in check_file_name:
        file_path = log_path + file_name
        if os.path.exists(file_path):
            NginxLog = TNginxLog(file_name)
            t = Read_log_Thread(NginxLog)
            t.setDaemon(True)
            thread_list.append(t)

    for t in thread_list:
        t.start()

    for t in thread_list:
        t.join()