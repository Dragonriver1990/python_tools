#!/usr/bin/env python
# encoding:utf-8

import os
import logging
import logging.config


log_path = os.path.dirname(os.path.abspath(__file__))
conf_file = "%s/logging.conf" % log_path
logging.config.fileConfig(conf_file, defaults={"logpath": log_path})



def log_handler():
    """获取日志handler"""
    return logging.getLogger("mc_service")


def runtime_log():
    return logging.getLogger("mc_runtime")


def table_log():
    return logging.getLogger("table")


def adapter_log():
    return logging.getLogger('adapter')


def __trace_log_handler():
    return logging.getLogger("mc_trace")


if __name__ == "__main__":
    logger = log_handler()
    logger.info("logger level info")
    logger.error("logger level error")
