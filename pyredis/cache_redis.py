#!/usr/bin/env python
# -*-coding:utf-8-*-
"""
    主要是用redis作为缓存使用
    需要安装redis数据库
    安装redis的python client：pip install redis
"""
from redis import StrictRedis
from json import loads, dumps


class RedisHelper:
    prefix = "bc:chart:cache"

    def __init__(self, host=None, port=None, prefix=None):
        # 这里读取redis配置信息，用到了conf.py里面的函数
        self._host = host
        self._port = int(port)
        self._redis = StrictRedis(host=self._host, port=self._port)

    def gen_key(self, chart_id):
        return "%s:%s" % (self.prefix, chart_id)

    def put(self, chart_id, data, expire=2000):
        key = self.gen_key(chart_id)
        self._redis.set(key, dumps(data))
        self._redis.expire(key, expire)
        return True

    def delete(self, chart_id):
        key = self.gen_key(chart_id)
        self._redis.delete(key)

    def deleteN(self, chart_id):
        key = self.gen_key(chart_id)
        keys = self._redis.keys("%s*" % key)
        for k in keys:
            self._redis.delete(k)

    def get(self, chart_id):
        key = self.gen_key(chart_id)
        data = self._redis.get(key)
        return {} if not data else loads(data)

    def hset(self, key, field, value):
        self._redis.hset(key, field, value)

    def hmget(self, key, fields):
        return self._redis.hmget(key, fields)

    def flush(self):
        keys = self._redis.keys("%s*" % self.prefix)
        pipe = self._redis.pipeline()
        for key in keys:
            pipe.delete(key)
        pipe.execute()

    # the type of value is list
    def list_push(self, key, data):
        return self._redis.rpush(key, dumps(data))
    # pop the head element of the list

    def list_pop(self, key):
        return self._redis.lpop(key)

    # pop all elements of the list
    def list_all_pop(self, key):
        while True:
            if self.list_size(key) == 0:
                self._redis.delete(key)
                break
            res = self._redis.lpop(key)
            if res:
                yield loads(res)

    # the length of list
    def list_size(self, key):
        return self._redis.llen(key)

    @property
    def redis(self):
        return self._redis


class ChartCacheHelper:
    """
        图表数据缓存
    """
    prefix = "bc:chart:cache"

    def __init__(self):
        self.crh = RedisHelper(prefix=ChartCacheHelper.prefix)

    def put(self, chart_id, data):
        self.crh.put(chart_id, data)

    def get(self, chart_id):
        return self.rh.get(chart_id)

    def delete(self, chart_id):
        self.rh.delete(chart_id)

    def deleteN(self, chart_id):
        self.rh.deleteN(chart_id)

    def flush(self):
        self.rh.flush()
