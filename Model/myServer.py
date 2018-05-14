#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @version : 1.0
# @Time    : 2018/1/16 14:14
# @Author  : chenjh
# @File    : myServer.py
# @Software: PyCharm
# @note    :
#ps -eo lstart 启动时间
#ps -eo etime 运行多长时间.
#ps -eo pid,lstart,etime | grep PID
#ps -eo pid,rsz,lstart,etime | grep 30743
#

import os,re

class myServer(object):

    use_info = {}

    def __init__(self):
        pass

    # 内存信息
    def memory_stat(self):
        mem = {}
        use_mem = {}
        f = open("/proc/meminfo")
        lines = f.readlines()
        f.close()
        for line in lines:
            if len(line) < 2: continue
            name = line.split(':')[0]
            var = line.split(':')[1].split()[0]
            mem[name] = long(var) * 1024.0
        mem['MemUsed'] = mem['MemTotal'] - mem['MemFree'] - mem['Buffers'] - mem['Cached']
        use_mem['MemTotal'] = mem['MemTotal']
        use_mem['MemUsed'] = mem['MemUsed']
        use_mem['MemFree'] = mem['MemFree']
        return use_mem

    # cpu 信息
    def cpu_stat(self):
        cpu = []
        cpuinfo = {}
        f = open("/proc/cpuinfo")
        lines = f.readlines()
        f.close()
        for line in lines:
            if line == '\n':
                cpu.append(cpuinfo)
                cpuinfo = {}
            if len(line) < 2: continue
            name = line.split(':')[0].rstrip()
            var = line.split(':')[1]
            cpuinfo[name] = var
        return cpu

    #负载信息 / loadavg
    def load_stat(self):
        loadavg = {}
        f = open("/proc/loadavg")
        con = f.read().split()
        f.close()
        loadavg['lavg_1']=con[0]
        loadavg['lavg_5']=con[1]
        loadavg['lavg_15']=con[2]
        loadavg['nr']=con[3]
        loadavg['last_pid']=con[4]
        return loadavg

    #运转时间 / Uptime
    def uptime_stat(self):
        uptime = {}
        f = open("/proc/uptime")
        con = f.read().split()
        f.close()
        all_sec = float(con[0])
        MINUTE,HOUR,DAY = 60,3600,86400
        uptime['day'] = int(all_sec / DAY )
        uptime['hour'] = int((all_sec % DAY) / HOUR)
        uptime['minute'] = int((all_sec % HOUR) / MINUTE)
        uptime['second'] = int(all_sec % MINUTE)
        uptime['Free rate'] = float(con[1]) / float(con[0])
        return uptime

    #获取网卡流量信息 /proc/net/dev
    # 返回dict,单位byte
    def net_stat(self):
        net = []
        f = open("/proc/net/dev")
        lines = f.readlines()
        f.close()
        for line in lines[2:]:
            con = line.split()
            intf = dict(
                zip(
                    ( 'interface','ReceiveBytes','ReceivePackets',
                      'ReceiveErrs','ReceiveDrop','ReceiveFifo',
                      'ReceiveFrames','ReceiveCompressed','ReceiveMulticast',
                      'TransmitBytes','TransmitPackets','TransmitErrs',
                      'TransmitDrop', 'TransmitFifo','TransmitFrames',
                      'TransmitCompressed','TransmitMulticast' ),
                    ( con[0].rstrip(":"),int(con[1]),int(con[2]),
                      int(con[3]),int(con[4]),int(con[5]),
                      int(con[6]),int(con[7]),int(con[8]),
                      int(con[9]),int(con[10]),int(con[11]),
                      int(con[12]),int(con[13]),int(con[14]),
                      int(con[15]),int(con[16]), )
                )
            )
            net.append(intf)
        return net

    def disk_stat(self):
        '''
        磁盘空间使用
        :return:
        '''
        import os
        hd={}
        disk = os.statvfs("/")
        hd['available'] = disk.f_bsize * disk.f_bavail
        hd['capacity'] = disk.f_bsize * disk.f_blocks
        hd['used'] = disk.f_bsize * disk.f_bfree
        return hd

    def readServer_info(self):
        '''
        读写服务信息
        return: 状态字典
        '''
        readServer_info = {}
        readServer_info['pid'] = 0
        readServer_info['run_time'] = 0
        readServer_info['mem_total'] = 0
        pid = os.popen('ps -ef |grep -v grep |grep readServer.py|cut -c 9-15').read()
        if pid:
            str_temp = os.popen('ps -eo pid,rsz,lstart,etime | grep '+pid).read()
            mode = re.compile(r'\d+')
            info = mode.findall(str_temp) #['30743  9304 Wed Jan 17 06:37:59 2018    08:47:12']
            if info[1]:
                readServer_info['pid'] = info[0]
                readServer_info['run_time'] = str_temp[-9:].replace('\n','')
                readServer_info['mem_total'] = info[1]+'KB'

        return readServer_info

    def server_info(self):
        '''
        服务器信息
        :return:
        '''
        server_info = {}
        server_info['read_server'] = self.readServer_info()
        server_info['memory'] = self.memory_stat()
        server_info['disk'] = self.disk_stat()
        server_info['load'] = self.load_stat()
        server_info['uptime'] = self.uptime_stat()
        server_info['read_server'] = self.readServer_info()
        return server_info

my_server = myServer()