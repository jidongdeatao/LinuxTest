#-*- coding: utf-8 -*-

import sys
import datetime
import os
reload(sys)
sys.setdefaultencoding('utf-8')

class Local:
    def __init__(self):
        self.beginTime = None


    def timenow(self):
        return datetime.datetime.now()


    def unicode(self,string):
        tmpString = string
        try:
            result = tmpString.decode('utf-8').encode('GBK')
        except:
            try:
                result = tmpString.decode('GBK')
            except:
                try:
                    result = u"{log}".format(log=tmpString)
                except:
                    result = str(tmpString)
        return result
'''
    ##解压zip源码包
    def unzipFiles(self,dir):
        #dir = os.path.dirname(file)
        unzipPath = tempDir
        if ".zip" in file:
            try:
                if not os.path.isdir(unzipPath):
                    os.makedirs(unzipPath)
                f = zipfile.ZipFile(file)
                f.extractall(unzipPath)
                f.close()
            except:
                g_Log.writeLog("traceback")
                if os.path.isdir(unzipPath):
                    shutil.rmtree(unzipPath)
                return False

    for dirpath,dirnames,filenames in os.walk(unzipPath):
        for zip in filenames:
            if ".zip" not in zip:
                continue
            tmpfile = os.path.join(dirpath,zip).replace("\\","/")
            try:
                os.mkdir(tmpfile+"-bak")
                f = zipfile.ZipFile(tmpfile)
                f.extractall(tmpfile+"-bak")
                f.close()
                os.remove(tmpfile)
                shutil.copytree(tmpfile+"-bak",tmpfile)
                shutil.rmtree(tmpfile+"-bak")
            except:
                writeLog("traceback")
                if os.path.isdir(tmpfile+"-bak"):
                    shutil.rmtree(tmpfile+"-bak")
    return unzipPath
'''
