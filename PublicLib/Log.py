#-*- coding: utf-8 -*-

import os
import sys
import traceback
import datetime
reload(sys)
sys.setdefaultencoding('utf-8')

import LocalOperate
import GlobalValue as g_Global
g_Local = None
class Log:
    def __init__(self,logPath=None):
        global g_Local
        g_Local = LocalOperate.Local()
        self.file = self.logFile()

        if not self.tryOpen():
            print "打开日志文件失败：{file}".format(file=self.file)
        g_Global.setValue("logFile",self.file)

    def logFile(self):
        curFile = os.path.abspath(sys._getframe(0).f_code.co_filename)
        logPath = curFile.split("PublicLib")[0]+"Log"
        if g_Global.getValue("startTime") is None:
            g_Global.setValue("startTime",str(datetime.datetime.now()))
        file = "{logPath}/Log-{time}.log".format(logPath=logPath,time=g_Global.getValue("startTime").replace(":",""))
        file = file.replace("\\","/")
        return file

    def writeLog(self,log,post=None,printlog=True):
        log = str(log)
        f = open(self.file,"a")
        time = str(datetime.datetime.now())
        try:
            raise
        except:
            f1 = sys.exc_info()[2].tb_frame.f_back
            post1 = f1.f_code.co_filename +":" + str(f1.f_lineno) +":"
            post1 = post1.replace("\\","/")
        if post==None:
            post = post1

        #post = sys._getframe(0).f_code.co_filename +":" + str(sys._getframe(0).f_lineno) +":"
        f.write("["+time+"]  "+ post)
        if log=="traceback":
            f.write("\n")
            errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
            f.write(errmsg)
        else:
            if log[-1:]=="\n":
                log = log[:-1]
            if "\n" in log:
                f.write("\n")

            try:
                f.write(log.decode('utf-8').encode('GBK')+"\n")
                f.write("\n")
                f.close()
            except:
                doNothing = True
            try:
                f.write(log.decode('GBK').encode('utf-8')+"\n")
                f.write("\n")
                f.close()
            except:
                doNothing = True
            try:
                f.write(u"{log}".format(log=log)+"\n")
                f.write("\n")
                f.close()
            except:
                doNothing = True

        if printlog != True:
            return 1

        if log=="traceback": #系统报错
            #traceback.print_exc(file=f)
            g_last_errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
            print g_last_errmsg
        else:
            print "["+time+"] ",post
            try:
                print log.decode('utf-8').encode('GBK')
            except:
                try:
                    print log.decode('GBK').encode('utf-8')
                except:
                    print log

        return 1

    def printLog(self,log):
        time = datetime.datetime.now()
        print "["+time+"]  "
        if log=="traceback": #系统报错
            print "["+time+"] ",''.join(traceback.format_exception(*sys.exc_info()))
        else:
            print "["+time+"] ",log

    def tryOpen(self):
        try:
            f = open(self.file,"a")
            f.close()
        except:
            errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
            print errmsg
            return 0
        return 1




