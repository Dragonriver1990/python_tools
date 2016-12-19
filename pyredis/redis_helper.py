#!/usr/bin/env python
# -*-coding:utf-8-*-

"""
    High quality code of Redis Python Client
"""

import json
import threading
import redis
import time
from other_tools.new_conf import get_section
from redis.client import Redis
from redis.sentinel import Sentinel
from logging import getLogger

if redis.__version__ != "2.10.5":
    raise Exception("Redis version must be 2.10.5, others have some bug")

redis_conf = get_section("redis")


def trace_time(func):
    """
    Decorator for execution time of function
    """

    def _with_time(*args, **kwargs):
        time_start = time.time()
        result = func(*args, **kwargs)
        time_end = time.time()
        if (time_end - time_start) > 0.5:
            getLogger("performance").error("[REDIS] func [func] cost [%f], args: %s",
                                           func.__name__, time_end - time_start, args[1:])
        return result
    return _with_time


class RedisHelper(object):
    """
    The redis python client support two mode:
    1、A single database instance mode
    2、sentinel mode

    好吧，英文写注释太费劲了，还是中文吧
    哨兵模式：多实例分为主从机器：master/slave
    写操作要在master上执行
    读操作要在slave上执行
    """
    MODE_WRITE = 0
    MODE_READ = 1

    _lock = threading.Lock()
    # 类变量
    redis_client_obj = dict()

    def __init__(self):
        if self.__class__.redis_client_obj:
            return

        # 获得锁，采用非阻塞模式，防止死锁挂起
        # 主要是防止在获得锁的过程中死锁
        locked = False
        retry = 0
        while not locked and retry < 10:
            locked = self.__class__._lock.acquire(False)
            time.sleep(0.01)
            retry += 1
        if not locked:
            raise Exception("programing error or system error in acquire lock")

        try:
            self.__class__.init_redis_client()
        finally:
            self.__class__._lock.release()

    @classmethod
    def parse_config(cls):
        cluster = redis_conf.get("cluster")
        return [tuple(redis_info.split(":"))for redis_info in cluster.split(",")]

    @classmethod
    def init_redis_client(cls):

        # 防止多线程竞争，获取到锁后依然可能已经初始化了
        if cls.redis_objs:
            return

        cls.instance_name = redis_conf.get('sentinel', "")
        cls.socket_timeout = redis_conf.get("socket_timeout", 5)
        cls.connect_timeout = redis_conf.get("connect_timeout", 0.1)

        # Redis服务单实例模式
        if not cls.instance_name:
            redis_info = redis_conf.get("host")
            cls.redis_client_obj[cls.MODE_WRITE] = Redis(
                host=redis_info.split(":")[0],
                port=redis_info.split(":")[1],
                socket_timeout=cls.socket_timeout,
                socket_connect_timeout=cls.connect_timeout,
                retry_on_timeout=1
            )
            cls.redis_client_obj[cls.MODE_READ] = cls.redis_client_obj[cls.MODE_WRITE]
        # 哨兵模式
        else:
            sentinel = Sentinel(
                sentinels=cls.parse_config(),
                socket_timeout=cls.socket_timeout,
                socket_connect_timeout=cls.connect_timeout,
                retry_on_timeout=1
            )
            cls.redis_client_obj[cls.MODE_READ] = sentinel.slave_for(service_name=cls.instance_name)
            cls.redis_client_obj[cls.MODE_WRITE] = sentinel.master_for(service_name=cls.instance_name)

    def get_client(self, mode, timeout=None):

        if timeout is not None:

            # 如果指定了超时，就临时生成一个符合这个超时的连接，使用短连接
            if not self.__class__.instance_name:
                host = redis_conf["host"]
                return Redis(
                    host=host.split(':')[0],
                    port=host.split(':')[1],
                    socket_timeout=self.socket_timeout+2,
                    socket_connect_timeout=self.connect_timeout,
                    retry_on_timeout=1,
                    socket_keepalive=False
                )

            curr_sentinel = Sentinel(
                self.parse_config(),
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.connect_timeout,
            )

            if mode == self.MODE_WRITE:
                return curr_sentinel.master_for(
                    self.instance_name,
                    socket_timeout=timeout+2,
                    socket_connect_timeout=self.connect_timeout,
                    socket_keepalive=False,  # 短连接
                    retry_on_timeout=True
                )
            else:
                return curr_sentinel.slave_for(
                    self.instance_name,
                    socket_timeout=timeout+2,
                    socket_connect_timeout=self.connect_timeout,
                    socket_keepalive=False,
                    retry_on_timeout=True
                )
        else:
            return self.__class__.redis_objs[mode]

    # 普通key/value
    @trace_time
    def set(self, key, data, expire=None):
        c = self.get_client(self.MODE_WRITE)
        c.set(key, data)
        if expire is not None:
            c.expire(key, expire)
        return True

    # key/json
    @trace_time
    def set_json(self, key, data, expire=None):
        c = self.get_client(self.MODE_WRITE)
        c.set(key, json.dumps(data))
        if expire is not None:
            c.expire(key, expire)
        return True

    @trace_time
    def get(self, key, expire=None):
        """
        获取指定的key
        :param key:
        :param expire: 如果不为None，则按照指定的缓存时间为key设置缓存时间
        :return:
        """
        master = self.get_client(self.MODE_WRITE)
        slave = self.get_client(self.MODE_READ)
        data = slave.get(key)

        # 为了强一致性，如果从节点没有，主节点再读一下
        if not data:
            data = master.get(key)

        if expire and data:
            master.expire(key, expire)

        return data

    @trace_time
    def get_json(self, key, expire=None):
        data = self.get(key, expire)
        return {} if not data else json.loads(data)

    @trace_time
    def incr(self, key, num=1):
        c = self.get_client(self.MODE_WRITE)
        return c.incr(key, num)

    @trace_time
    def delete(self, key):
        c = self.get_client(self.MODE_WRITE)
        return c.delete(key)

    @trace_time
    def deleteN(self, key):
        master = self.get_client(self.MODE_WRITE)
        keys = self.keys("%s*" % key)
        for k in keys:
            master.delete(k)
        return True

    @trace_time
    def keys(self, key, cursor=0, count=100):
        res = []
        is_first = True
        slave = self.get_client(self.MODE_READ)
        while is_first or cursor > 0:
            is_first = False
            cursor, scan_keys = slave.scan(cursor, key, count)
            if scan_keys:
                res = res + scan_keys
        return list(set(res))

    @trace_time
    def scan(self, cursor, match, count):
        slave = self.get_client(self.MODE_READ)
        return slave.scan(cursor, match, count)

    @trace_time
    def exists(self, key):
        c = self.get_client(self.MODE_READ)
        return c.exists(key)

    @trace_time
    def hset(self, key, field, value):
        c = self.get_client(self.MODE_WRITE)
        return c.hset(key, field, value)

    @trace_time
    def hget(self, key, field):
        c = self.get_client(self.MODE_READ)
        return c.hget(key, field)

    @trace_time
    def hgetall(self, key):
        c = self.get_client(self.MODE_READ)
        return c.hgetall(key)

    @trace_time
    def hincrby(self, key, field, step):
        c = self.get_client(self.MODE_WRITE)
        return c.hincrby(key, field, step)

    @trace_time
    def hmset(self, name, mapping):
        c = self.get_client(self.MODE_WRITE)
        return c.hmset(name, mapping)

    @trace_time
    def eval(self, script, numkeys, *keys_and_args):
        c = self.get_client(self.MODE_WRITE)
        return c.eval(script, numkeys, *keys_and_args)

    @trace_time
    def hmget(self, key, fields):
        c = self.get_client(self.MODE_READ)
        return c.hmget(key, fields)

    @trace_time
    def flush(self, key):
        c = self.get_client(self.MODE_WRITE)
        keys = self.keys("%s*" % key)
        pipe = c.pipeline()
        for key in keys:
            pipe.delete(key)
        pipe.execute()
        return True

    @trace_time
    def set_ttl(self, key, expire=21600):
        c = self.get_client(self.MODE_WRITE)
        return c.expire(key, expire)

    @trace_time
    def pub(self, channel, msg):
        c = self.get_client(self.MODE_WRITE)
        c.pubsub()
        return c.publish(channel, msg)

    @trace_time
    def expire(self, key, expire):
        c = self.get_client(self.MODE_WRITE)
        return c.expire(key, expire)

    @trace_time
    def zrange(self, key, lowest, highest, withscores):
        c = self.get_client(self.MODE_READ)
        return c.zrange(key, lowest, highest, withscores)

    @trace_time
    def zscore(self, key, member):
        c = self.get_client(self.MODE_READ)
        return c.zscore(key, member)

    @trace_time
    def zadd(self, key, score, member):
        c = self.get_client(self.MODE_WRITE)
        return c.zadd(key, score, member)

    @trace_time
    def zrem(self, key, member):
        c = self.get_client(self.MODE_WRITE)
        return c.zrem(key, member)

    @trace_time
    def rpush(self, key, value):
        c = self.get_client(self.MODE_WRITE)
        return c.rpush(key, value)

    @trace_time
    def hdel(self, key, field):
        c = self.get_client(self.MODE_WRITE)
        return c.hdel(key, field)

    @trace_time
    def blpop(self, key, timeout):
        c = self.get_client(self.MODE_WRITE, timeout+2)
        return c.blpop(key, timeout)

    @trace_time
    def lpop(self, key):
        c = self.get_client(self.MODE_WRITE)
        return c.lpop(key)

    @trace_time
    def llen(self, key):
        c = self.get_client(self.MODE_READ)
        return c.llen(key)

    @trace_time
    def setnx(self, key, value):
        c = self.get_client(self.MODE_WRITE)
        return c.setnx(key, value)

    @trace_time
    def decr(self, key):
        c = self.get_client(self.MODE_WRITE)
        return c.decr(key)

    @trace_time
    def sadd(self, key, *values):
        c = self.get_client(self.MODE_WRITE)
        return c.sadd(key, *values)

    @trace_time
    def smembers(self, key):
        c = self.get_client(self.MODE_READ)
        return c.smembers(key)

    @trace_time
    def ttl(self, key):
        c = self.get_client(self.MODE_READ)
        return c.ttl(key)

    @trace_time
    def register_script(self, script):
        c = self.get_client(self.MODE_WRITE)
        return c.register_script(script)

