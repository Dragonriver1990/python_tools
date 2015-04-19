#!/usr/bin/env python
#encoding:utf-8
"""
    主要是用redis作为缓存使用
    需要安装redis数据库
    安装redis的python client：pip install redis
"""
from redis import StrictRedis
from json import loads,dumps
from conf import get_conf

class RedisHelper:
    prefix = "bc:chart:cache"

    def __init__(self,host=None, port=None, prefix=None):
        #这里读取redis配置信息，用到了conf.py里面的函数
        conf = get_conf()
        self._host = host if host else conf.get("redis","host")
        self._port = int(port) if port else int(conf.get("redis","port"))
        self._redis = StrictRedis(host=self._host, port=self._port)

        

