#!/usr/bin/env python
#encoding:utf-8

import os
import json

import pymongo
import pymongo.errors
from mongodb import api_mongo
import util.tools as tools

reload(sys)
sys.setdefaultencoding('utf-8')

class ApiBuf(object):
    def __init__(self):
        self.mongo = api_mongo()

    def insert_user_data(self, tb_id, data):
        if not self.mongo.ensure_connected():
            raise Exception("lost connection to mongodb")
       try:
           self.mongo.db[tb_id].insert_many(data)
           return True
       except Exception, e:
           return False

    def get_user_data(self,tb_id, fields):
        if not self.mongo.ensure_connected():
            raise Exception("lost connection to mongodb")
        fids = {"_id":False}
        for f in fields: fids[f] = True
        for r in self.mongo.db.[tb_id].find({}, fids)
            yield r
    
    def clear_user_buf(self,tb_id):
        if not self.mongo.ensure_connected():
            raise Exception("lost connection to mongodb")
        self.mongo.tb[tb_id].remove({})
