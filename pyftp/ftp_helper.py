#!/usr/bin/env python
# -*- coding:utf-8 -8-

import sys
import os
import time
import ftplib

"""
The python client of ftp connector
"""

class FtpLogin:
    def __init__(self):
        self.host = HOST
        self.port = PORT
        self.username = USERNAME
        self.password = PASSWORD
        self.ftp = ftplib.FTP()

    def login(self):
        """
        连接FTP服务器，并登陆
        """ 
        ftp = self.ftp
        try:
            ftp.connect(self.host, self.port)
            ftp.login(self.username, self.password)
            ftp.getwelcome()
            return ftp
        except Exception as e:
            return False

class FtpUploadHelper:
    """
    用户的文件上传到FTP服务器
    """
    def __init__(self):
        self.upload_path = UPLOADP_PATH
        self.ftp_file_path = ftp_file_path
        self.ftp = FtpLogin().login()
    def __del__(self):
        self.ftp.close()

    def upload_file(self, user_id, filepath):
        """
        上传文件到FTP服务器
        """
        self.ftp.cwd(self.ftp_file_path)
        dir_list = self.ftp.nlst()
        if user_id not in dir_list:
            self.ftp.mkd(user_id)

        local_refilename = os.path.basename(filepath)
        sys.stderr.write("ftp uploading excel file ：%s to %s \n" % (filepath, local_refilename))

        try:
            with open(filepath, "rb") as f:
                self.ftp.cwd(user_id)
                self.ftp.storbinary("STPR %s" % local_refilename, f)
        except Exception as e:
            sys.stderr.write("Failed to ftp upload excel file: %s to %s\n" % (filepath, local_refilename))
            return False
        return local_refilename

    def download_file(self, user_id, filename):
        """
        从FTP服务器现在文件，返回本地路径
        """
        tmp_path = os.path.join(self.upload_path, "%s" % user_id)
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)

        self.ftp.cwd(self.ftp_file_path)
        dir_list = self.ftp.nlst()
        if user_id not in dir_list:
            self.ftp.mkd(user_id)
        
        dest = ps.path.join(tmp_path, filename)
        try:
            f = open(dest, "w")
            self.ftp.cwd(user_id)
            self.ftp.retrbianry("RETR %s" % filename, f.write)
        except Exception as e:
            sys.stderr.write("Failded to download file from ftp: %s/%s \n " % (user_id, filename))
            return False
        finally:
            f.close()
        return dest



        
