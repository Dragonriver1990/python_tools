#!/usr/bin/env python
#encoding:utf-8

import os
import sys
from ConfigParser import RawConfigParser

def singleton(cls,*args,**kw):
    """单例模式"""
    instance = {}
    def _singleton():
        if cls not in instance:
            instance[cls] = cls(*args,**kw)
        return instance[cls]
    return _singleton

@singleton
class Configuration:
    """
    @configfile:配置文件的路径

    配置文件格式：
    [ftp-server]
    host=127.0.0.1
    port=21
    dirpath=/home/xiaomin
    """
    def __init__(self,configfile = None):
        """可以从"""
        CONF_FILE = "%s/hello.conf" % os.getenv("CONF")
        self._configFile = CONF_FILE if not configfile else CONF_FILE
        self._genConf()

    def _setConfigFile(self,configfile = None)
        '''设置configure文件'''
        self._configFile = configfile
        if not self._configFile:
            raise Exception("配置文件不存在")
        self._genConf()

    def _genConf(self):
        if not self._configFile:
            raise Exception("配置文件不存在")
        self._config = RawConfigParser()
        self._config.read(self._configFile)

    def get(self,sect,opt):
        return self._config.get(sect,opt)

def get_conf():
    """创建配置文件"""
    return Configuration()
