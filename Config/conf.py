#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@version: 1.0
@author: chenjh
@file: conf.py
@time: 2017-08-28 16:54
@note:配置信息
"""

CONFIG = {}
debug = False
CONFIG['month_eng'] ={'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
CONFIG['heart_beat_time'] = 2 #  心跳时间 秒
CONFIG['filter_url'] = [r'/Common/checkSensitive',r'keep_session']
if  debug :  #调试模式
    CONFIG['redis_host'] = '127.0.0.1'
    CONFIG['redis_port'] = 6379
    CONFIG['redis_password'] = '123456'
    CONFIG['log_path'] = "Z:\\big_data\\client\\NgnixLog\\"
    CONFIG['ngnix_file'] = [
        'access_id.258.com.log'
    ]
    CONFIG['queue_name']="dsj"
    CONFIG['socket_host'] = '192.168.128.128'
    CONFIG['socket_port'] = 9501
    CONFIG['read_server_sh_path'] = '/home/chenjinhe/big_data/client/Tool/run.sh'
    CONFIG['client_version'] = '1.1'
else:  #真实环境
    CONFIG['redis_host'] = '192.168.0.110'
    CONFIG['redis_port'] = 6392
    CONFIG['redis_password'] = 'mZ7TailMgwrj'
    CONFIG['log_path'] = "/data0/logs/"
    CONFIG['ngnix_file'] = [
        'access_id.258.com.log',
        'access_id_231.mozhan.com.log',
        'access_id.swws.com.log',
        'access_id_yy.258.com.log'  # 扩客系统
    ]
    CONFIG['queue_name']="dsj"
    CONFIG['socket_host'] = '192.168.0.205'
    CONFIG['socket_port'] = 9501
    CONFIG['read_server_sh_path'] = '/data0/web/loganalysis.258.com/run.sh'
    CONFIG['client_version'] = '1.1'
    

def getConf(name):
    return CONFIG[name]
