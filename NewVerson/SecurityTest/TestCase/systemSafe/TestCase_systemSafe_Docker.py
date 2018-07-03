#-*- coding: utf-8 -*-
__author__ = 'jWX350731'
import sys
import os
import traceback
import datetime
import re
import zipfile
import shutil


from sys import path
# 系统默认Unicode解码，需要换成utf-8形式
reload(sys)
sys.setdefaultencoding('utf-8')


'''
""" 相关安全要求说明 """
《01 产品网络安全红线落地解读及指导V2_1.xls》：
        6.1.2 使用操作系统的非管理员权限帐号来运行数据库
《中央软件院网络安全测试基线V2.0.xlsx》 中关于系统中中无用账号及不安全密码、文件权限、调试工具、无属主文件、进程安全等要求
'''
'''
""" 脚本功能 """
扫描系统中的无用账号及不安全密码、文件权限、调试工具、无属主文件、进程安全等问题点，扫描策略见本脚本所在目录下的systemSafePolicy.xlsx
'''
'''
""" 脚本配置执行说明 """
配置1：/SecurityTest/Config/config.xlsx，“vmInfo”页
配置2：本脚本所在目录下的systemSafePolicy.xlsx，“policy”页。
配置3：本脚本所在目录下的systemSafePolicy.xlsx，“config”页。每一行配置都有说明，请仔细阅读。
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
    excel0 = ExcelOperate.Excel(excelName=excelName,sheetName="vmInfo")
    g_vmInfo = excel0.read()
    del g_vmInfo[0]
    systemSafePolicyExcel = g_curDir + "/systemSafePolicy.xlsx"
    excel1 = ExcelOperate.Excel(excelName=systemSafePolicyExcel,sheetName="policy")
    g_systemSafePolicy = excel1.read()
    del g_systemSafePolicy[0]
    excel2 = ExcelOperate.Excel(excelName=systemSafePolicyExcel,sheetName="config")
    g_config = excel2.read()
    del g_config[0]
    g_ResultFile = g_caseName.replace("TestCase","Report").replace(".py","")+"-"+g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")+".xls"
except:
    errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
    print errmsg
    exit(0)

def getsystemSafePolicy(): #获取所有支持系统扫描的策略信息
    global g_systemSafePolicy
    policy = []
    for p in g_systemSafePolicy:
        supportSys = p[3].lower()
        if p[0].lower() == "true" and "os" in supportSys.lower():
            policy.append(p)
    g_systemSafePolicy = policy
    return 1

def scan_in_MV():
    reportPath = g_caseName.replace("TestCase","Report").replace(".py","")+"-"+g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")
    if not os.path.exists(reportPath):
        os.makedirs(reportPath)
    shutil.copy(g_curDir+"/systemSafePolicy.xlsx",reportPath+"/systemSafePolicy.xlsx")
    for vm in g_vmInfo:
        try:
            vmIP = vm[0]
            vmName = vm[1]
            vmUser = vm[2]
            vmUserPasswd = vm[3]
            vmSuRoot = vm[4]
            vmRootPasswd = vm[5]
            tDocker = ContainerOperate.Container(ip=vmIP,user=vmUser,password=vmUserPasswd,suRoot=vmSuRoot,rootPassword=vmRootPasswd)
            containerInfo = tDocker.Container_Mount_link()
            for scan in g_systemSafePolicy:
                name = scan[1]
                info = scan[2]
                ifRed = scan[4]

                tLinux = LinuxOperate.Linux(ip=vmIP,name=vmName,user=vmUser,password=vmUserPasswd,suRoot=vmSuRoot,rootPassword=vmRootPasswd)

                if '\\' in info:
                    info = info.replace('\\', '\\\\')
                if '$' in info:
                    info = info.replace('$', '\$')
                if '"' in info:
                    info = info.replace('"', '\\"')
                if '`' in info:
                    info = info.replace('`', '\\`')

                tLinux.sendRootCommand("rm -rf /tmp/tempScan.sh")
                tLinux.sendCommand('echo \"{cmd}\">/tmp/tempScan.sh'.format(cmd=info))
                tLinux.sendRootCommand("chmod 777 /tmp/tempScan.sh")
                for container in containerInfo:
                    try:
                        image = container[0].split("/")[-1].split(":")[0]
                        id = container[1]
                        mntDir = container[2]
                        output = tLinux.sendRootCommand("docker ps |grep {id}".format(id=id))
                        if output==False or output[0]=="":
                            continue
                        tLinux.sendRootCommand("cp /tmp/tempScan.sh {dir}/tmp/tempScan.sh".format(dir=mntDir))
                        cmd = "chmod 777 /tmp/tempScan.sh"
                        output = tLinux.sendRootCommand("docker exec -u 0 {id} {cmd}".format(id=id,cmd=cmd))
                        cmd = "/usr/bin/sh /tmp/tempScan.sh"
                        output = tLinux.sendRootCommand("docker exec -u 0 {id} {cmd}".format(id=id,cmd=cmd))
                        result = output[0]
                        cmd = "rm -rf /tmp/tempScan.sh"
                        tLinux.sendRootCommand("docker exec -u 0 {id} {cmd}".format(id=id,cmd=cmd))

                        # 检查是否有需要进行结果筛选
                        if ifRed.upper() == "YES":
                            resultPath = reportPath + "/(RedLine)" + str(vmIP) + "/" + str(image)
                        else:
                            resultPath = reportPath + "/" + str(vmIP) + "/" + str(image)
                        if not os.path.exists(resultPath):
                            os.makedirs(resultPath)
                        resultFile = resultPath + "/" + str(name) + ".txt"
                        f1 = open(resultFile,'a')
                        try:
                            excel = ExcelOperate.Excel(excelName=systemSafePolicyExcel,sheetName=name)
                            ignoreKeys = excel.read()
                            if ignoreKeys == False:
                                ignoreKeys = []
                            else:
                                del ignoreKeys[0]
                            pythonRegular = ""
                            for x in ignoreKeys:
                                pythonRegular = pythonRegular + x[0] + "|"
                            if pythonRegular == "": # 没有配置python形式的结果排查，扫描结果直接写入结果文件
                                raise "no python values"
                            pythonRegular = pythonRegular[:-1]

                            lines = result.split("\n")
                            for line in lines:  # 配置了python形式的结果排查，扫描结果筛选后写入结果文件
                                if "/devicemapper/mnt/" in line:
                                    continue
                                x0 = re.findall(pythonRegular,line)
                                if x0==[]:
                                    f1.write(line+"\n")
                        except:
                            errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
                            if "no python values" in errmsg:
                                g_Log.writeLog(u"没有为{name}配置python形式的结果排查，扫描结果直接写入结果文件".format(name=name))
                            else:
                                g_Log.writeLog("traceback")
                            lines = result.split("\n")
                            for line in lines:  # 配置了python形式的结果排查，扫描结果筛选后写入结果文件
                                if "/devicemapper/mnt/" in line:
                                    continue
                                f1.write(line+"\n")
                    except:
                        g_Log.writeLog("traceback")

                    f1.close()
                tLinux.logout()
            tDocker.logout()
        except:
            g_Log.writeLog("traceback")
            #### 清除环境中的残留脚本
            try:
                tLinux = LinuxOperate.Linux(ip=vmIP,name=vmName,user=vmUser,password=vmUserPasswd,suRoot=vmSuRoot,rootPassword=vmRootPasswd)
                output = tLinux.sendRootCommand("find / -name tempScan.sh")
                if output!=False and output[0]!="":
                    files = output[0].split("\n")
                for f in files:
                    cmd = "rm -rf {file}".format(file=f)
                    tLinux.sendRootCommand("rm -rf {cmd}".format(cmd=cmd))
                tLinux.logout()
            except:
                g_Log.writeLog("traceback")

def cleanAll():
    for vm in g_vmInfo:
        try:
            vmIP = vm[0]
            vmName = vm[1]
            vmUser = vm[2]
            vmUserPasswd = vm[3]
            vmSuRoot = vm[4]
            vmRootPasswd = vm[5]
            tLinux = LinuxOperate.Linux(ip=vmIP,name=vmName,user=vmUser,password=vmUserPasswd,suRoot=vmSuRoot,rootPassword=vmRootPasswd)
            output = tLinux.sendRootCommand("find / -name tempScan.sh")
            if output!=False and output[0]!="":
                files = output[0].split("\n")
            for f in files:
                cmd = "rm -rf {file}".format(file=f)
                tLinux.sendRootCommand("rm -rf {cmd}".format(cmd=cmd))
            tLinux.logout()
        except:
            g_Log.writeLog("traceback")


'''
""" 以下定义的函数，请在特定位置添加自己的代码 """
'''
# 执行前的准备操作
def prepare():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
        cleanAll()
    except:
        g_Log.writeLog("traceback")
        return 0
    return 1

# 执行用例
def run():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
        getsystemSafePolicy()
        scan_in_MV()
    except:
        g_Log.writeLog("traceback")
        return 0
    return 1

# 执行后清理环境
def clearup():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
        cleanAll()
    except:
        g_Log.writeLog("traceback")
        return 0
    return 1

if __name__ == '__main__':
    res = prepare()
    if not res:
        print "执行用例prepare模块失败，结束用例{name}的执行".format(name=g_caseName)
    else:
        run()
        clearup()

