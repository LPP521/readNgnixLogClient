#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @version : 1.0
# @Time    : 2018/1/14 15:16
# @Author  : chenjh
# @File    : myRedis
# @Software: PyCharm
# @note    :

from rediscluster import StrictRedisCluster
import sys

class myRedisCluster(object):
    conn = ''
    redis_nodes = [
            {'host': '192.168.128.128', 'port': 6379},
        ]

    def __init__(self):
        try:
            self.conn = StrictRedisCluster(startup_nodes =self.redis_nodes)
        except Exception as e:
            print e
            sys.exit(1)

    def add(self, key, value):
        self.conn.set(key, value)

    def get(self, key):
        self.conn.get(key)

    def rem(self,key):
        result = self.conn.delete(key)
        if result != 0:
            return 1
        else:
            return 0

my_redis_cluster = myRedisCluster()