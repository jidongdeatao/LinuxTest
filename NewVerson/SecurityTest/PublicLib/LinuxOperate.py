#-*- coding: utf-8 -*-

import sys
import paramiko
import os
import traceback
import re
reload(sys)
sys.setdefaultencoding('utf8')

import LocalOperate
import Log
import GlobalValue as g_Global
g_Local = None
g_Log = None

class Linux:
    def __init__(self,ip="",name="",user="",password="",suRoot="",rootPassword="",pkey="",pkey_password=""):
        global g_Local,g_Log
        g_Local = LocalOperate.Local()
        g_Log = Log.Log()
        if rootPassword  != "":
            rootPassword = rootPassword.replace("\$","$").replace("\#","#").replace("\!","!").replace("\*","*").replace("\?","?")
            rootPassword = rootPassword.replace("$","\$").replace("#","\#").replace("!","\!").replace("*","\*").replace("?","\?")
        self.ip = ip
        self.name = name
        self.user = user
        self.password = password
        self.suRoot = suRoot
        self.rootPassword = rootPassword
        self.pkey = pkey.replace("\\","/")
        self.pkey_password = pkey_password
        self.ssh = self.login()


    def login(self):
        try:
            password = self.password
            if self.pkey != "":
                password = "私钥:\"{keyFile}\"".format(keyFile=self.pkey)
            g_Log.writeLog(u"用户 {user}/{password} 登陆{ip}".format(user=self.user,password=password,ip=self.ip))

            ssh=paramiko.SSHClient()
            ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
            if self.pkey != "":
                if self.pkey_password != "":
                    private_key = paramiko.RSAKey.from_private_key_file(self.pkey,password=self.pkey_password)
                else:
                    private_key = paramiko.RSAKey.from_private_key_file(self.pkey)
                ssh.connect(self.ip,username=self.user,pkey=private_key)
            else:
                ssh.connect(self.ip,username=self.user,password=self.password)
            g_Log.writeLog(u"用户登陆成功")
        except:
            g_Log.writeLog("traceback")
            return 0
        return ssh

    def sendCommand(self,cmd,timeout=None):
        try:
            g_Log.writeLog(u"在{ip}上执行{user}用户命令：".format(ip=self.ip,user=self.user)+cmd)
            stdin,stdout,stderr = self.ssh.exec_command( cmd,timeout=timeout )
            output = (stdout.read().strip(),stderr.read().replace("Password: ",""))
        except:
            errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
            g_Log.writeLog("traceback")
            if "timeout" in errmsg and timeout is not None:
                output = ("","Operation timed out after {time} seconds.".format(time=timeout))
                return output
            return 0
        return output

    def logout(self):
        try:
            g_Log.writeLog(u"用户{user}/{password}注销登陆{ip}".format(user=self.user,password=self.password,ip=self.ip))
            self.ssh.close()
            g_Log.writeLog(u"用户注销成功")
        except:
            g_Log.writeLog("traceback")
            return 0

    def checkSuRoot(self):
        try:
            if self.suRoot == "":
                g_Log.writeLog(u"没有定义切换root的命令！")
                return 0
            g_Log.writeLog(u"在{ip}上从用户{user}切换到用户root".format(ip=self.ip,user=self.user))
            if self.rootPassword == "":
                stdin,stdout,stderr = self.ssh.exec_command( "{type} -c '{cmd}'".format(type=self.suRoot,cmd="whoami") ,timeout=30)
            else:
                stdin,stdout,stderr = self.ssh.exec_command( "echo -e {passwd}|{type} -c '{cmd}'".format(passwd=self.rootPassword,type=self.suRoot,cmd="whoami")  ,timeout=30)
        except:
            g_Log.writeLog("traceback")
            return 0

        output = (stdout.read(),stderr.read().replace("Password: ",""))
        if "root" not in output[0]:
            g_Log.writeLog(u"用户{user}切换root失败,请检查账号密码{root}/{rootPassword}".format(user=self.user,root=self.suRoot,rootPassword=self.rootPassword))
            g_Log.writeLog(output[1])
            return 0
        return 1

    def sendRootCommand(self,cmd,timeout=None):
        try:
            cmd = cmd.replace("\'","\"").replace("'","\"")
            g_Log.writeLog(u"在{ip}上执行root用户命令：".format(ip=self.ip)+cmd)
            if self.suRoot == "":
                stdin,stdout,stderr = self.ssh.exec_command( cmd,timeout=timeout )
            elif self.rootPassword == "":
                stdin,stdout,stderr = self.ssh.exec_command( "{type} -c '{cmd}'".format(type=self.suRoot,cmd=cmd),timeout=timeout )
            else:
                stdin,stdout,stderr = self.ssh.exec_command( "echo -e {passwd}|{type} -c '{cmd}'".format(passwd=self.rootPassword,type=self.suRoot,cmd=cmd),timeout=timeout )
            output = (stdout.read().strip(),stderr.read().strip().replace("Password: ",""))
            if output[1] != "" and len(output[1])>9:
                g_Log.writeLog(u"执行命令异常："+output[1])
        except:
            errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
            g_Log.writeLog("traceback")
            if "timeout" in errmsg and timeout is not None:
                output = ("","Operation timed out after {time} seconds.".format(time=timeout))
                return output
            return 0
        return output

    def uploadFileByRead(self,localFile=None,destFile=None):
        try:
            g_Log.writeLog(u"向{ip}上传文件{file}：".format(ip=self.ip,file=localFile))
            localFile=localFile.replace("\\","/")
            destFile=destFile.replace("\\","/")
            if not os.path.exists(localFile):
                g_Log.writeLog(u"源文件不存在：{file}".format(file=localFile))
                return  0
            destDir = os.path.dirname(destFile)
            output = self.sendRootCommand( "if [ -d \"{file}\" ]; then echo \"true\"; else echo \"false\"; fi".format(file=destDir) )
            if "true" not in output[0]:
                g_Log.writeLog(u"目的目录不存在：{file}".format(file=destDir))
                return  0
            output = self.sendRootCommand( "ls -l {file}".format(file=destFile) )
            if "No such file or directory" not in output[1] or "total" in output[0]:
                g_Log.writeLog(u"目的文件已经存在：{file}".format(file=destFile))
                return  0

            file = open(localFile)
            info = file.read()
            if '\\' in info:
                info = info.replace('\\', '\\\\')
            if '$' in info:
                info = info.replace('$', '\$')
            if '"' in info:
                info = info.replace('"', '\\"')
            if '`' in info:
                info = info.replace('`', '\\`')

            output = self.sendCommand( "echo \"{cmd}\">{shName}".format(cmd=info,shName=destFile) )
            if output[1] != "" and len(output[1])>9 :
                g_Log.writeLog(u"上传文件异常："+output[1])
                return 0
            output = self.sendRootCommand("ls -l {shName}".format(shName=destFile))
            if output[1] != "" and len(output[1])>9 :
                g_Log.writeLog(u"上传文件异常："+output[1])
                return 0
        except:
            g_Log.writeLog("traceback")
            return 0

        return output

    def findFile(self,type=None,dir=None):
        type = "list"

    def deleteFile(self,file):
        try:
            g_Log.writeLog(u"在{ip}上删除文件{file}".format(ip=self.ip,file=file))
            output1 = self.sendRootCommand( "rm -rf {file}".format(file=file) )
            output2 = self.sendRootCommand( "ls -l {file}".format(file=file) )
            if output2[0] != "":
                g_Log.writeLog(u"文件删除失败："+output1[1])
                return 0
        except:
            g_Log.writeLog("traceback")
            return 0
        return 1

    def getIdleDisc(self):
        try:
            output = self.sendRootCommand( "df -h" )
            if output==False or output[0] == "":
                g_Log.writeLog(u"磁盘信息获取失败")
                return 0
            discInfo = output[0].split("\n")
            idleDisc = ""
            discSize = 0  #单位为M
            for d in discInfo:
                x1 = re.findall(" ([0-9\.]+)G\s+[0-9]+% (/\w+)\s*$",d)
                x2 = re.findall(" ([0-9\.]+)M\s+[0-9]+% (/\w+)\s*$",d)
                if x1==[] and x2==[]:
                    continue
                if x1==[]: #查找到的单位为M
                    dInfo = x2[0]
                    tempSize = float(dInfo[0])
                if x2==[]: #查找到的单位为G，要转换为M
                    dInfo = x1[0]
                    tempSize = float(dInfo[0])*1000
                if tempSize > discSize:
                    discSize = tempSize
                    idleDisc = dInfo[1]

            if discSize == 0 or idleDisc == "":
                g_Log.writeLog(u"没有获取到空闲的磁盘信息")
                return 0
            else:
                g_Log.writeLog(u"获取到空闲的磁盘为{disc}，大小为{size}".format(disc=idleDisc,size=idleDisc))
            return [idleDisc,discSize]
        except:
            g_Log.writeLog("traceback")
            return 0
        return 1



