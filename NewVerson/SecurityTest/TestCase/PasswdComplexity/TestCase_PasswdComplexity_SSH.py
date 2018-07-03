#-*- coding: utf-8 -*-

import sys
import os
import traceback
import datetime
import json
import re


from sys import path
reload(sys)
sys.setdefaultencoding('utf-8')

'''
""" 相关安全要求说明 """
《01 产品网络安全红线落地解读及指导V2_1.xls》 8.1.1 系统自身操作维护类口令满足“口令安全要求”。
'''
'''
""" 脚本功能 """
检查操作系统的账号密码安全
'''
'''
""" 脚本配置执行说明 """
配置1：/SecurityTest/Config/config.xlsx，“vmInfo”页
'''

'''
""" 可以在此处下方添加自己的代码（函数） """
'''
try:
    g_Log = None
    g_Global = None
    g_caseName = None

    curFile = os.path.abspath(sys._getframe(0).f_code.co_filename)
    g_caseName = curFile.replace("\\","/")
    g_curDir = os.path.split(g_caseName)[0]
    path.append( g_caseName.split("TestCase")[0]+"PublicLib" )

    import GlobalValue as g_Global
    g_Global.init()
    g_Global.setValue("startTime",str(datetime.datetime.now()))

    import Log
    import ExcelOperate
    import ContainerOperate
    import LinuxOperate
    import LocalOperate
    g_Log = Log.Log()
    g_Local = LocalOperate.Local()

    ##### 获取环境配置信息
    excelName = g_caseName.split("TestCase")[0]+"Config/config.xlsx"
    excel1 = ExcelOperate.Excel(excelName=excelName,sheetName="vmInfo")
    g_vmInfo = excel1.read()
    del g_vmInfo[0]
    g_ResultFile = g_caseName.replace("TestCase","Report").replace(".py","")+"-"+g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")+".xls"
except:
    errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
    print errmsg
    exit(0)

def scan_in_ENV():  #[[vmIP,subject,subjectInfo,config,errlog,result]]
    errInfo = []
    for vm in g_vmInfo:
        try:
            vmIP = vm[0]
            vmName = vm[1]
            vmUser = vm[2]
            vmUserPasswd = vm[3]
            vmSuRoot = vm[4]
            vmRootPasswd = vm[5]

            tLinux = LinuxOperate.Linux(ip=vmIP,name=vmName,user=vmUser,password=vmUserPasswd,suRoot=vmSuRoot,rootPassword=vmRootPasswd)
            if tLinux.loginReady()==False:
                errInfo.append( [vmIP,u"VM",u"{name}".format(name=vmName),u"",u"服务器登录失败，请修复服务器后重新扫描","Error",u""] )
                continue
            errInfo_vm = check_in_VM(tLinux)
            errInfo = errInfo+errInfo_vm

            tDocker = ContainerOperate.Container(ip=vmIP,user=vmUser,password=vmUserPasswd,suRoot=vmSuRoot,rootPassword=vmRootPasswd)
            containerInfo = tDocker.Container_Mount_link()
            errInfo_Docker = check_in_Docker(tLinux,containerInfo)
            errInfo = errInfo+errInfo_Docker

            tDocker.logout()
            tLinux.logout()
        except:
            g_Log.writeLog("traceback")
    return errInfo  #[[vmIP,subject,subjectInfo,config,errlog,result]]

def check_in_VM(linuxSSH):  #测试虚机中系统账号的口令安全，格式[[vmIP,subject,subjectInfo,config,errlog,result,redline]]
    errInfo = []
    errInfo1 = check_pwquality(linuxSSH)
    errInfo = errInfo + errInfo1
    errInfo2 = check_userPassword(linuxSSH)
    errInfo = errInfo + errInfo2
    return errInfo


def check_in_Docker(linuxSSH,containerInfo):  #测试容器中系统账号的口令安全，格式[[vmIP,subject,subjectInfo,config,errlog,result,redline]]
    errInfo = []
    output1 = linuxSSH.sendCommand("/usr/sbin/ifconfig eth0")
    ip1 = re.findall("inet\s+(\d+\.\d+\.\d+\.\d+)",output1[0])
    ip_linux = ip1[0]
    for container in containerInfo:
        try:
            image = container[0].split("/")[-1].split(":")[0]
            id = container[1]
            cmd = "/usr/sbin/ifconfig eth0"
            output2 = linuxSSH.sendRootCommand("docker exec -u 0 {id} {cmd}".format(id=id,cmd=cmd),timeout=10)
            if output2!=False:
                if "exec failed" in output2[1]:
                    errInfo.append( [linuxSSH.ip,u"Docker",u"{image}".format(image=image),u"",u"容器登录失败，请修复容器后重新扫描","Error",u""] )
                    continue
            ip2 = re.findall("inet\s+(\d+\.\d+\.\d+\.\d+)",output2[0])
            if ip2!=False and ip2[0]!="":
                ip_container = ip2[0]
            if ip_container == ip_linux:
                continue

            cmd = "netstat -tunlp |grep :22"
            out2 = linuxSSH.sendRootCommand("docker exec -u 0 {id} {cmd}".format(id=id,cmd=cmd),timeout=10)
            if out2!=False and out2[0]!="":
                errInfo.append( [linuxSSH.ip,u"Docker",u"{image}".format(image=image),u"{conf}".format(conf=out2[0]),u"容器中打开了22端口，可能支持ssh登陆，存在安全风险".format(user=user,ip=ip_container),"Fail",u""] )

            cmd = "netstat -tunlp |grep :2375"
            out2 = linuxSSH.sendRootCommand("docker exec -u 0 {id} {cmd}".format(id=id,cmd=cmd),timeout=10)
            if out2!=False and out2[0]!="":
                errInfo.append( [linuxSSH.ip,u"Docker",u"{image}".format(image=image),u"{conf}".format(conf=out2[0]),u"容器中打开了2375默认远程访问端口，存在安全风险".format(user=user,ip=ip_container),"Fail",u""] )

            cmd = "cat /etc/passwd |egrep \"[0-9]{4}|^root\""
            output = linuxSSH.sendRootCommand("docker exec -u 0 {id} {cmd}".format(id=id,cmd=cmd),timeout=10)
            for userInfo in output[0].split("\n"):
                user = userInfo.split(":")[0]
                out1 = linuxSSH.sendRootCommand("ssh {user}@{ip}".format(user=user,ip=ip_container),timeout=10)
                if out1!=False:
                    if "Connection refused" not in out1[1] and "timed out" not in out1[1] :
                        errInfo.append( [linuxSSH.ip,u"Docker",u"{image}".format(image=image),u"",u"\"ssh {user}@{ip}\"命令下发成功({ip}是容器IP)，容器支持ssh登陆，存在安全风险".format(user=user,ip=ip_container),"Fail",u"以往都不支持SSH登陆，需要考虑风险"] )

                cmd = "egrep -n \"^{user}:\" /etc/shadow"
                out3 = linuxSSH.sendRootCommand("docker exec -u 0 {id} {cmd}".format(id=id,cmd=cmd),timeout=10)
                if out3==False or out3[0]=="":
                    continue
                config = "/etc/shadow:"+out3[0]
                encryptPass = config.split(":")[-8]
                if encryptPass!="!!" and encryptPass!="*":
                    errInfo.append( [linuxSSH.ip,u"Docker",u"{image}".format(image=image),u"",u"容器中/etc/shadow中账号\"{user}\"的口令，需要人工查看加密是否安全".format(user=user),"Check",u"红线要求"] )
        except:
            g_Log.writeLog("traceback")

    return errInfo

def check_userPassword(ssh):  #检查具体用户的密码安全[[vmIP,subject,subjectInfo,config,errlog,result,redline]]
    errInfo = []
    output = ssh.sendRootCommand("cat /etc/passwd |egrep \"[0-9]{4}\"")
    if output==False or output[0]=="":
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"",u"/etc/passwd中没有找到自定义账号","Fail",u""] )
        return errInfo
    users = []
    for info in output[0].split("\n"):
        users.append(info.split(":")[0])

    for user in users:
        output = ssh.sendRootCommand("egrep -n \"^{user}:\" /etc/shadow".format(user=user))
        if output==False or output[0]=="":
            errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"",u"/etc/shadow中没有找到账号\"{user}\"的口令配置".format(user=user),"Fail",u""] )
        else:
            config = "/etc/shadow:"+output[0]
            expireDays = config.split(":")[-4]
            encryptPass = config.split(":")[-8]
            if encryptPass!="!!" and encryptPass!="*":
                errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=config),u"/etc/shadow中账号\"{user}\"的口令，需要人工查看加密是否安全".format(user=user),"Check",u"红线要求"] )
                if expireDays=="":
                    errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=config),u"/etc/shadow中没有配置\"{user}\"的口令的最长有效期限".format(user=user),"Fail",u"红线要求"] )
                elif int(expireDays)>90:
                    errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=config),u"/etc/shadow中配置\"{user}\"的口令的最长有效期限，值太大，建议设置为90".format(user=user),"Fail",u"红线要求"] )
                else:
                    errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=config),u"/etc/shadow中配置\"{user}\"的口令的最长有效期限符合安全规范".format(user=user),"Pass",u"红线要求"] )

    output = ssh.sendRootCommand("cat /etc/shadow |egrep \"^root\"")
    config = "/etc/shadow:"+output[0]
    errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=config),u"/etc/shadow中账号\"{user}\"的口令，需要人工查看加密是否安全".format(user="root"),"Check",u"红线要求"] )

    return errInfo

def check_pwquality(ssh):  #检查密码复杂度配置[[vmIP,subject,subjectInfo,config,errlog,result,redline]]
    errInfo = []
    output = ssh.sendRootCommand("egrep -n '^password\s+include\s+[a-zA-Z0-9_\.\-]+$' /etc/pam.d/login")
    if output==False or output[0]=="" or "No such file or directory" in output[1]:
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"",u"/etc/pam.d/login中没有配置密码复杂度策略(以password开头的配置)","Fail",u"红线要求"] )
        return errInfo
    else:
        config = "/etc/pam.d/login:"+output[0]
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=config),u"/etc/pam.d/login中配置了密码复杂度策略","Pass",u"红线要求"] )

    x0 = re.findall("password\s+include\s+([a-zA-Z0-9_\.\-]+)$",config)
    pwqualityFile = "/etc/pam.d/"+x0[0].strip()
    output = ssh.sendRootCommand("ls -l {file}".format(file=pwqualityFile))
    if output==False or output[0]=="" or "No such file or directory" in output[1]:
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"",u"/etc/pam.d/login中配置了密码复杂度策略的文件{file}不存在".format(file=pwqualityFile),"Fail",u"红线要求"] )
        return errInfo

    output = ssh.sendRootCommand("egrep -n '^password\s+\w+\s+pam_pwquality.so\s' {file}".format(file=pwqualityFile))
    if output==False or output[0]=="":
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"",u"{file}中没有配置口令复杂度(带有pam_pwquality.so的配置)".format(file=pwqualityFile),"Fail",u"红线要求"] )
    else:
        config = pwqualityFile+":"+output[0].split("\n")[-1]
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=config),u"{file}中配置了口令复杂度".format(file=pwqualityFile),"Pass",u"红线要求"] )
    pwquality = pwqualityFile+":"+output[0].split("\n")[-1]

    x1 = re.findall("minlen=([0-9]+)",pwquality)  #检查口令最小长度配置
    if x1==False or x1[0]=="":
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=pwquality),u"{file}中没有配置口令最小长度要求(minlen值)".format(file=pwqualityFile),"Fail",u"红线要求"] )
    elif int(x1[0])<8:
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=pwquality),u"{file}中没有配置口令最小长度小于8(minlen值)".format(file=pwqualityFile),"Fail",u"红线要求"] )
    else:
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=pwquality),u"{file}中配置的口令最小长度要求(minlen值)符合安全规范".format(file=pwqualityFile),"Pass",u"红线要求"] )

    x1 = re.findall("minclass=([0-9]+)",pwquality)  #检查口令最少字符种类配置
    if x1==False or x1[0]=="":
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=pwquality),u"{file}中没有配置口令最少字符种类(minclass值)".format(file=pwqualityFile),"Fail",u"红线要求"] )
    elif int(x1[0])<3:
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=pwquality),u"{file}中没有配置口令最少字符种类小于3(minclass值)".format(file=pwqualityFile),"Fail",u"红线要求"] )
    else:
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=pwquality),u"{file}中配置的口令最少字符种类要求(minclass值)符合安全规范".format(file=pwqualityFile),"Pass",u"红线要求"] )

    x1 = re.findall("retry=([0-9]+)",pwquality)  #检查最大输入错误口令次数
    if x1==False or x1[0]=="":
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=pwquality),u"{file}中没有配置输入错误口令次数限制(retry值)".format(file=pwqualityFile),"Fail",u"红线要求"] )
    else:
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=pwquality),u"{file}中配置了输入错误口令次数限制(retry值)".format(file=pwqualityFile),"Pass",u"红线要求"] )

    output = ssh.sendRootCommand("egrep -n '^password\s+\w+\s+\w+.so\s.*remember=[0-9]+' {file}".format(file=pwqualityFile)) #检查前N次口令不能重复使用
    if output==False or output[0]=="":
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"",u"{file}中没有配置前N次口令不能重复使用(remember值)".format(file=pwqualityFile),"Fail",u"红线要求"] )
    else:
        config = pwqualityFile+":"+output[0]
        x2 = re.findall("remember=([0-9]+)",config)
        if int(x2[0])>12:
            errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=config),u"{file}中配置前N次口令不能重复使用(remember值)，值太大（建议配置为5）".format(file=pwqualityFile),"Fail",u"红线要求"] )
        else:
            errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=config),u"{file}中配置前N次口令不能重复使用(remember值)符合安全规范".format(file=pwqualityFile),"Pass",u"红线要求"] )

    output = ssh.sendRootCommand("egrep -n '^auth\s+required\s+\w+.so\s.*deny=[0-9]+.*' {file}".format(file=pwqualityFile)) #检查登录失败尝试N次后锁定
    if output==False or output[0]=="":
        errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"",u"{file}中没有配置登录失败尝试N次后锁定机制(deny值)".format(file=pwqualityFile),"Fail",u"红线要求"] )
    else:
        config = pwqualityFile+":"+output[0]
        x3 = re.findall("deny=([0-9]+)",config)
        if int(x3[0])>3:
            errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=config),u"{file}中配置登录失败尝试N次后锁定(deny值)，值太大（建议配置为3）".format(file=pwqualityFile),"Fail",u"红线要求"] )
        else:
            errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=config),u"{file}中配置登录失败尝试N次后锁定(deny值)符合安全规范".format(file=pwqualityFile),"Pass",u"红线要求"] )
        x4 = re.findall("unlock_time=([0-9]+)",config)
        if x4==False or x4[0]=="":
            errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=config),u"{file}中没有配置登录失败尝试N次锁定后的解锁机制(unlock_time值)，值太大（建议配置为3）".format(file=pwqualityFile),"Fail",u"红线要求"] )
        else:
            errInfo.append( [ssh.ip,u"VM",u"{vmName}".format(vmName=ssh.name),u"{conf}".format(conf=config),u"{file}中配置了登录失败尝试N次锁定后的解锁机制(unlock_time值)符合安全规范".format(file=pwqualityFile),"Pass",u"红线要求"] )

    return errInfo






'''
""" 以下定义的函数，请在特定位置添加自己的代码 """
'''
# 执行前的准备操作
def prepare():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
    except:
        #errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
        g_Log.writeLog("traceback")
        return 0
    return 1

# 执行用例
def run():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
        excelResult = ExcelOperate.Excel(excelName=g_ResultFile,sheetID=0)
        excelResult.new()
        excelResult.write([[u"主机IP",u"扫描主体",u"扫描主体信息",u"检查的配置项，记录的格式为 文件名:行号:内容",u"检查结果信息",u"测试结果",u"备注"]],redLine=3)
        errInfo = scan_in_ENV()  #[[vmIP,subject,subjectInfo,config,errlog,result,redline]]
        excelResult.write(errInfo)
    except:
        g_Log.writeLog("traceback")
        return 0
    return 1

# 执行后清理环境
def clearup():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''

    except:
        #errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
        g_Log.writeLog("traceback")
        return 0
    return 1


res = prepare()
if not res:
    print "错误信息：执行用例prepare模块失败，结束用例{name}的执行".format(name=g_caseName)
else:
    run()
    clearup()

