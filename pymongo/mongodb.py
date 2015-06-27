#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import util.config
from pymongo import MongoClient

reload(sys)
sys.setdefaultencoding('utf-8')


def default_mongo():
    conf = util.config.get_section('mongo')
    return MongoHelper({
        'mongo_host': conf.get('host'),
        'mongo_port': int(conf.get('port')),
        'mongo_db': conf.get('mongo_db')
        })

def api_mongo():
    conf = util.config.get_section('api_buf')
    return MongoHelper({
        'mongo_host': conf.get('mongo_host')
        'mongo_port': conf.get('mongo_port')
        'mongo_db': conf.get('mongo_db')
        })

    
class MongoHelper:
    def __init__(self, config):
        self.host = config['mongo_host']
        self.port = config.get('mongo_port', 27017)
        self.database = config.get('mongo_db')
        self.db = None
        self._connect()

    def _connect(self):
        if self.db:
            return True
        try:
            self.db = MongoClient(self.host, self.port)[self.database]
        except Exception as e:
            return False
        return True
    
    def ensure_connected(self):
        if not (self.db or self._connect()):
            return False
        return True

