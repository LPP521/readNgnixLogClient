#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @version : 1.0
# @Time    : 2018/1/14 15:16
# @Author  : chenjh
# @File    : myRedis
# @Software: PyCharm
# @note    :
# http://blog.csdn.net/moxiaomomo/article/details/27085415

import redis,sys
from Config.conf import getConf

class myRedis(object):

    def __init__(self, host='127.0.0.1', port=6379):
        try:
            host = getConf('redis_host')
            port = getConf('redis_port')
            password = getConf('redis_password')
            if password != '':
                pool = redis.ConnectionPool(host = host,password = password,port = port,db=0)
            else:
                pool = redis.ConnectionPool(host = host,port = port,db=0)
            self.conn = redis.StrictRedis(connection_pool = pool)
        except Exception as e:
            print e
            sys.exit(0)

    def lpush(self,queue_name,value):
        return self.conn.lpush(queue_name, value)

    def add(self, key, value):
        result = self.conn.set(key, value)
        return result

    def get(self, key):
        result = self.conn.get(key)
        return result

    def mod(self, key, value):
        result = self.conn.get(key)
        if result:
            result2 = self.conn.set(key, value)
            print(result2)
        else:
            print("key " + key + "is not found")

    def rem(self,key):
        result = self.conn.delete(key)
        if result != 0:
            print('删除成功')

my_redis = myRedis()