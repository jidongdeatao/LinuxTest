#-*- coding: utf-8 -*-

import sys
import os
import traceback
import datetime
import yaml
import json
import re


from sys import path
reload(sys)
sys.setdefaultencoding('utf-8')


'''
""" 相关安全要求说明 """
《01 产品网络安全红线落地解读及指导V2_1.xls》 3.1.2 所有能对系统进行管理的人机接口以及跨信任网络的机机接口必须有接入认证机制，标准协议没有认证机制的除外。
'''
'''
""" 脚本功能 """
遍历环境中的所有节点，查询tomcat下的directrouters中配置的接口，用session认证进行认证测试
'''
'''
""" 脚本配置执行说明 """
配置1：/SecurityTest/Config/config.xlsx，“vmInfo”页
配置2：本脚本所在目录下的APIlist.xlsx，“parameter”页。需配置sessionMethod和sessionPort
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
    g_omCoreInfo = []
    for vm in g_vmInfo:
        if vm[6]==1 or str(vm[6]).upper() == "TRUE":
            g_omCoreInfo = [ vm[0], vm[1], vm[2], vm[3], vm[4], vm[5]]
    excel2 = ExcelOperate.Excel(excelName=excelName,sheetName="otherConfig")
    g_config = excel2.read()
    del g_config[0]
    g_apiInfo = []
except:
    errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
    print errmsg
    exit(0)

def getAPI_by_Tomcat():
    apis = []
    global g_apiInfo
    for vm in g_vmInfo:
        try:
            vmIP = vm[0]
            vmName = vm[1]
            vmUser = vm[2]
            vmUserPasswd = vm[3]
            vmSuRoot = vm[4]
            vmRootPasswd = vm[5]
            tLinux = LinuxOperate.Linux(ip=vmIP,user=vmUser,password=vmUserPasswd,suRoot=vmSuRoot,rootPassword=vmRootPasswd)
            output = tLinux.sendRootCommand("find / -name directrouters")
            if output[0] == "":
                continue
            dirs = output[0].split("\n")
            for dir in dirs:
                output = tLinux.sendRootCommand("ls {dir}".format(dir=dir))
                if output[0] == "":
                    continue
                files = output[0].split()
                for f in files:
                    if f[-4:] != ".xml":
                        continue
                    fileName = dir + "/" + f
                    output = tLinux.sendRootCommand("cat {f1}".format(f1=fileName) + " |egrep \"^\s{8}<uri>|^\s{8}<protocol>|\s{16}<method>\"")
                    if output[0] == "":
                        continue
                    x1 = output[0].replace(" ","").replace("\n","").replace("<uri>","\n<uri>")
                    fileInfo = x1.split("\n")
                    for info in fileInfo:
                        info = info.strip()
                        if info == "":
                            continue
                        a = re.findall("<uri>(.*?)</uri>",info)
                        uri = a[0]
                        a = re.findall("<protocol>(.*?)</protocol>",info)
                        protocol = a[0]
                        a = re.findall("<method>(.*?)</method>",info)
                        methods = a
                        for method in methods:
                            apis.append([vmIP,fileName,method,protocol,uri])
                            if [method,protocol,uri] in g_apiInfo:
                                continue
                            g_apiInfo.append([method,protocol,uri])

        except:
            g_Log.writeLog("traceback")
    return apis


def check_httpAPI_bySession(): #主要函数3：校验url的cookie认证，输出结果：[[method,protocol,uri,certLink,simpleLink,errorLog]]
    global g_apiInfo
    for conf in g_config:
        if conf[0]=="sessionMethod":
            sessionMethod = conf[1]
        if conf[0]=="sessionPort":
            sessionPort = conf[1]
    messages = []  #格式为[[method,protocol,uri,certLink,simpleLink,errorLog]]
    for info in g_apiInfo:  #[method,protocol,uri]
        url = info[2]
        protocol = info[1]
        method = info[0]
        simpleLink = "curl -k -X {method} {protocol}://{ip_port}{url}".format(method=method.upper(),ip_port=sessionPort,url=url,protocol=protocol)
        sessionLink = "curl -k -X {method} {protocol}://{ip_port}{url} {sessionMethod}".format(method=method.upper(),ip_port=sessionPort,url=url,sessionMethod=sessionMethod,protocol=protocol)
        sessionLink = re.subn("\{.*?\}", "parameter123",sessionLink)[0]
        simpleLink = re.subn("\{.*?\}", "parameter123",simpleLink)[0]
        messages.append([info[0],info[1],info[2],sessionLink,simpleLink,""])

    result = []  #格式为[[microService,url,serverName,link,errorLog]]
    omCoreIP = g_omCoreInfo[0]
    omCoreUser = g_omCoreInfo[2]
    omCoreUserPasswd = g_omCoreInfo[3]
    omCoreSuRoot = g_omCoreInfo[4]
    omCoreRootPasswd = g_omCoreInfo[5]
    for msg in messages:
        ssh = LinuxOperate.Linux(ip=omCoreIP,user=omCoreUser,password=omCoreUserPasswd,suRoot=omCoreSuRoot,rootPassword=omCoreRootPasswd)
        sessionLink = msg[3]
        simpleLink = msg[4]
        #certLink = revisePara(certLink)
        output = ssh.sendCommand(sessionLink,timeout=30)
        if output[0]=="":
            result.append([u"{x}".format(x=msg[0]),u"{x}".format(x=msg[1]),u"{x}".format(x=msg[2]),u"{x}".format(x=msg[3]),u"{x}".format(x=msg[4]),u"",u"命令下发失败，可能支持session认证或参数错误",u"请手动测试"])
            continue
        output = ssh.sendCommand(simpleLink,timeout=30)
        if output[0]!="":
            response = output[0]
        else:
            response = output[1]
        res = checkResponse(response)
        result.append([u"{x}".format(x=msg[0]),u"{x}".format(x=msg[1]),u"{x}".format(x=msg[2]),u"{x}".format(x=msg[3]),u"{x}".format(x=msg[4]),u"{x}".format(x=res[0]),u"{x}".format(x=res[1])])
        ssh.logout()
    return result

def checkResponse(response):
    res = ""
    lines = response.split("\n")
    for line in lines:
        x = re.findall("(curl:\s*\(.*)",line)
        if x!=[]:
            res = x[0]
            break
        elif "<head><title>" in line:
            res = line
            break
        elif "Connection refused" in line:
            res = line
            break
        elif "You like 404 pages" in line:
            res = "404 page not found"
            break
        else:
            res = ""
            continue
    if res=="":
        res = response

    result = "Fail"
    errCase1 = "curl:.*certificate|curl:.*identifier|curl:.*unrecognized|curl:.*Connection refused|curl:.*SSL received a record|curl:.*clientcert|curl:.*authenticate"
    errCase2 = "^Unauthorized| no token |404 page not found|404 Not Found| must authenticate before making a request|Please login firstly|Authorization failed|validation does not pass|Authorized failed|Auth failed|token error"
    x = re.findall(errCase1+"|"+errCase2,res,re.IGNORECASE)
    if x != []:
        result = "Pass"
    if "Operation timed out" in res:
        result = "Pass"

    return [res,result]

#def get_unAuthAPI(authAPI):


'''
""" 以下定义的函数，请在特定位置添加自己的代码 """
'''
# 执行前的准备操作
def prepare():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
        if g_omCoreInfo == []:
            g_Log.writeLog(u"错误信息：没有配置kubectl节点，请配置在/SecurityTest/Config/config.xlsx")
            return 0

    except:
        errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
        g_Log.writeLog(errmsg)
        return 0
    return 1

# 执行用例
def run():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
        global g_ResultFile

        curDir = os.path.split(g_caseName)[0]
        resultDir = curDir.replace("TestCase","Report")
        startTimeSign = g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")
        g_ResultFile = g_caseName.replace("TestCase","Report").replace(".py","")+"-"+startTimeSign+".xls"
        #g_ResultFile = g_caseName.replace("TestCase","Report").replace(".py","")+"-"+g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")+".xls"

        ## 查找所有注册在tomcat的API接口，格式：[method,protocol,uri]
        errAPI = getAPI_by_Tomcat()
        sessionAPIExcel = resultDir + "/sessionAPI-"+startTimeSign+".xls"
        sessionAPI = ExcelOperate.Excel(excelName=sessionAPIExcel,sheetID=0)
        sessionAPI.new()
        sessionAPI.write([[u"主机IP",u"来源文件",u"Method",u"Protocol",u"URL"]])
        sessionAPI.write(errAPI)

        ## 创建excel用于保存扫描结果
        excelResult = ExcelOperate.Excel(excelName=g_ResultFile,sheetID=0)
        excelResult.new()
        excelResult.write([[u"Method",u"Protocol",u"URL",u"URL正常认证命令",u"URL无认证命令",u"执行结果",u"测试结果"]],redLine=1)
        ## Session认证测试结果（该功能比较独立，本脚本目录下有另外单独脚本）
        checkResult = check_httpAPI_bySession()  #[[method,protocol,uri,certLink,simpleLink,errorLog,result]]
        excelResult.write(checkResult)

    except:
        errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
        g_Log.writeLog(errmsg)
        return 0
    return 1

# 执行后清理环境
def clearup():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''

    except:
        errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
        g_Log.writeLog(errmsg)
        return 0
    return 1


if __name__ == '__main__':
    res = prepare()
    if not res:
        print "错误信息：执行用例prepare模块失败，结束用例{name}的执行".format(name=g_caseName)
    else:
        run()
        clearup()

