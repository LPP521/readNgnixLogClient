#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @version : 1.0
# @Time    : 2018/1/14 11:42
# @Author  : chenjh
# @File    : client.py
# @Software: PyCharm
# @note    : 监控服务

from Config.conf import getConf
from gevent import socket
import time,json,sys,os
from Model.myServer import my_server
from Model.myRedis import my_redis

host = getConf('socket_host')
port = getConf('socket_port')
read_server_sh_path = getConf('read_server_sh_path')

client_version = getConf('client_version')
check_file_name = getConf('ngnix_file')


def _get_file_line_redis_prefix(str_replace_ip="",file_name=''):
    str_replace_ip = str(str_replace_ip).replace('.','_')
    today = time.strftime('%Y%m%d', time.localtime(time.time()))
    redis_key = today + '_' + str_replace_ip + file_name + '_line'
    one_file_run_logs = my_redis.get(redis_key)
    if one_file_run_logs == None :
        iline = 0
    else:
        iline = int(one_file_run_logs)
    return iline

def __get_day_run_logs(ip):
    logs_total = 0
    for file_name in check_file_name:
        logs_total = logs_total + _get_file_line_redis_prefix(ip,file_name)
    return logs_total

#--客户端状态数据---上传服务器监控数据---
def __get_send_status_data():
    addr = my_socket.getsockname()
    data = my_server.server_info()
    info = {}
    info['ip'] = addr[0]
    info['monit_version_id'] = client_version
    info['read_run_logs'] = __get_day_run_logs(info['ip'])
    data['server'] = info;
    send_data = {'ip':addr[0], 'code':2999, 'data':data, 'msg':''}
    json_data_temp = json.dumps(send_data)
    return json_data_temp

def print_log(arg):
    print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),arg

def doConnect():
    try:
        print_log('--do test connect--')
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.connect((host, port))
        if my_socket:
            return my_socket
        else:
            print 'none'
            return ''
    except socket.error, e:
        print_log("---creating socket error: " + str(e))
        return ''


if __name__ == '__main__':

    my_socket = doConnect()

    if my_socket == '':
        print_log('socket is error')
        sys.exit(0)

    while True:
        try:
            data = my_socket.recv(1024)
            if data:
                data = json.loads(data)
                if data.has_key('code') and data['code'] == 1999:
                    status = os.system('sh '+ read_server_sh_path)
                    my_socket.sendall(__get_send_status_data())
                elif data.has_key('code') and data['code'] == 1001: # 关闭
                    status = os.system('sh ' + read_server_sh_path + ' stop')
                    print status>>8
                elif data.has_key('code') and data['code'] == 1002: # 更新
                    status = os.system('sh ' + read_server_sh_path + ' update')
                    print status>>8
                elif data.has_key('code') and data['code'] == 1003: # 重启
                    status = os.system('sh ' + read_server_sh_path + ' restart')
                    print status>>8
                elif data.has_key('code') and data['code'] == 1004: # 关闭所有
                    status = os.system('sh ' + read_server_sh_path + ' stop')
                    print status>>8
                    os._exit(0)  # 直接终止进程
                else:
                    print 'error'
            else:
                while 1:
                    print_log('else sleep 10 to test connect')
                    time.sleep(10)
                    my_socket = doConnect()
                    if my_socket:
                        break
        except socket.error, e:
            my_socket.close()
            print_log("error: " + str(e))
            while 1:
                    print_log('error sleep 10 to test connect')
                    time.sleep(10)
                    my_socket = doConnect()
                    if my_socket:
                        break