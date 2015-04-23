#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from hashlib import md5
from random import randint


class Md5Helper():
    """
        Md5 key generator helper
    """
    
    @staticmethod
    def key_gen(ori_str):
        """生成key,主要用于生成唯一id"""
        return "%s" % (md5("%s_%s_%s" % (ori_str, time.time(), randint(0, 100000))).hexdigest())

    @staticmethod
    def ori_str_gen(ori_str):
        """生成key,主要用于生成密码"""
        return md5(md5(ori_str).hexdigest()).hexdigest()
