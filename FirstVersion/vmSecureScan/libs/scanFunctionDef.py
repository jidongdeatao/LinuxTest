#-*- coding: GBK -*-
import time
import commands
import sys
import os
import re
import csv
import paramiko

class scanFunctionDef:
    filename = None
    localTime = None
    runPath = ""
    resultPath = ""

def set_csvFilename(filename):
    scanFunctionDef.filename = filename
def get_csvFilename():
    return scanFunctionDef.filename

def set_localTime():
    scanFunctionDef.localTime = time.strftime('%Y-%m-%d_%H%M%S')
def get_localTime():
    return scanFunctionDef.localTime

def set_runPath(path):
    scanFunctionDef.runPath = path
def get_runPath():
    return scanFunctionDef.runPath

def get_resultPath():
    return scanFunctionDef.resultPath

#从csv中获取配置信息
def getSystemInfo():
    systemInfo = []
    filename = get_csvFilename()
    csvReader = csv.reader( open(filename,'rb') )
    try:
        for ip,systemname,user,password,root,rootpassword in csvReader:
            systemInfo.append( [ip,systemname,user,password,root,rootpassword] )
    except:
        print "No information in csv or the information in csv is not correct."
        return False
    return systemInfo

#输出结果文件的路径及格式
def resultFile(ip,sysName,shName):
    path = get_runPath()
    time = get_localTime()
    sign1 = sysName+"-"+ip
    sign2 = shName[0:-3]
    
    resultPath = path+"/result-"+time
    pathExist1 = os.path.exists(resultPath)
    if not pathExist1:
        t1 = os.mkdir(resultPath)
    
    scanFunctionDef.resultPath = resultPath
    resultPath = resultPath + "/" + sign1
    pathExist1 = os.path.exists(resultPath)
    if not pathExist1:
        t1 = os.mkdir(resultPath)
    
    fileName = resultPath + "/" + sign2 + ".txt"
    fileExists = os.path.exists(fileName)
    #print fileName
    if not fileExists:
        fileName = unicode(fileName,"GB2312")
        #fileName = fileName.encode(encoding='utf-8').decode(encoding='GB2312')
        file = open( fileName, 'w')
        file.write("")
        file.close()
    return fileName

#从script文件夹中获取要执行的Linux脚本
def getScript():
    workPath = get_runPath()
    path = workPath+'/config/script'
    shlist = os.listdir(path)
    length = len(shlist)
    i = 0
    while i < length:
        if ".sh" not in shlist[i]:
            del shlist[i]
            continue
        shlist[i] = path + "/" + shlist[i]
        i = i+1
    return shlist

def runAll():
    #先获取配置信息
    vmInfo = getSystemInfo()
    #检测配置信息是否正确
    i = 0
    while i < len(vmInfo)-1:
        x = vmInfo[i]
        ip = x[0]
        user = x[2]
        passwd = x[3]
        rootPasswd = x[5]
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(ip,username=user,password=passwd)
        except:
            print " "*4+"// Cannot login {ip} by \"{user}/{passwd}\". ".format(ip=ip,user=user,passwd=passwd)
            del vmInfo[i]
            continue
        stdin,stdout,stderr = ssh.exec_command( "echo -e {passwd}|su root -c 'whoami'".format(passwd=rootPasswd) )
        curUser = stdout.read()
        if "root" not in curUser:
            print " "*4+"// su root in {ip} with password '{passwd}' failed!".format(ip=ip,passwd=rootPasswd)
            del vmInfo[i]
            continue
        i = i+1
        
    #获取要执行的Linux脚本
    shScripts = getScript()
    for sct in shScripts:
        shName = sct.split("/")[-1]
        if ".sh" not in sct:
            continue
        print " "*4+"Run {shName}".format(shName=shName)
        #对脚本中特殊字符进行python格式转义
        file = open(sct)
        info = file.read()
        #if '\n' in info:
            #info = info.replace('\n', '')
        if '\\' in info:
            info = info.replace('\\', '\\\\')
        if '$' in info:
            info = info.replace('$', '\$')
        if '"' in info:
            info = info.replace('"', '\\"')
        if '`' in info:
            info = info.replace('`', '\\`')
    #执行脚本部分，先拿出一条脚本到不同虚机节点执行，再切换下一条脚本    
        for x in vmInfo:
            ip = x[0]
            sysName = x[1]
            user = x[2]
            passwd = x[3]
            rootPasswd = x[5]
            print " "*8+"Run scan script for {ip}".format(user=user,ip=ip)
            ssh=paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip,username=user,password=passwd)
            
            stdin,stdout,stderr = ssh.exec_command( "rm -rf /tmp/{shName}".format(shName=shName) )
            stdout.read()
            stdin,stdout,stderr = ssh.exec_command( "touch /tmp/{shName}".format(shName=shName) )
            stdout.read()
            
            stdin,stdout,stderr = ssh.exec_command( "echo -e {passwd}|su root -c 'chmod 700 /tmp/{shName}'".format(passwd=rootPasswd,shName=shName) )
            stdout.read()
            stdin,stdout,stderr = ssh.exec_command( "echo \"{cmd}\">>/tmp/{shName}".format(cmd=info,shName=shName) )
            stdout.read()
            
            stdin,stdout,stderr = ssh.exec_command( "echo -e {passwd}|su root -c '/usr/bin/sh /tmp/{shName}'".format(passwd=rootPasswd,shName=shName) )
            shResult = stdout.read()
            shError = stderr.read()
            if "terminated by" in shError:
                stdin,stdout,stderr = ssh.exec_command( "echo -e {passwd}|su root -c '/usr/bin/sh /tmp/{shName}'".format(passwd=rootPasswd,shName=shName) )
                shResult = stdout.read()
                shError = stderr.read()
            if "terminated by" in shError:
                stdin,stdout,stderr = ssh.exec_command( "echo -e {passwd}|su root -c '/usr/bin/sh /tmp/{shName}'".format(passwd=rootPasswd,shName=shName) )
                shResult = stdout.read()
                shError = stderr.read()
            shResult = shResult.split("\n")
            ssh.close()
            
            ssh=paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip,username=user,password=passwd)
            stdin,stdout,stderr = ssh.exec_command( "rm -rf /tmp/{shName}".format(shName=shName) )
            
            result = resultFile(ip,sysName,shName)
            file = open( result,'w' )
            for line in shResult:
                if "fileaccess" in shName and "lrwxrwxrwx" in line:
                    continue
                if shName in line:
                    continue
                if len(line)>180000:
                    continue
                file.write(line+"\n")
            ssh.close()
    
