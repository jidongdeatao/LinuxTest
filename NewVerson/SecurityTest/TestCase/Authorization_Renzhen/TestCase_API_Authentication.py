#-*- coding: utf-8 -*-

import sys
import os
import traceback
import datetime
import re


from sys import path
# 系统默认Unicode解码，需要换成utf-8形式
reload(sys)
sys.setdefaultencoding('utf-8')


'''
""" 相关安全要求说明 """
《01 产品网络安全红线落地解读及指导V2_1.xls》 3.1.2 所有能对系统进行管理的人机接口以及跨信任网络的机机接口必须有接入认证机制，标准协议没有认证机制的除外。
'''
'''
""" 脚本功能 """
先由开发或雨燕工具获取到代码中的接口信息，通过该脚本，可以对这些接口进行认证测试。
'''
'''
""" 脚本配置执行说明 """
配置1：/SecurityTest/Config/config.xlsx，“vmInfo”页
        1\
配置2：本脚本所在目录下的APIs.xlsx，“API”页。每一列配置表头都有批注说明，请仔细阅读。
配置3：本脚本所在目录下的APIs.xlsx，“parameter”页。每一行配置都有说明，请仔细阅读。
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

    codeAPIExcel = g_curDir + "/APIlist.xlsx"
    excel1 = ExcelOperate.Excel(excelName=codeAPIExcel,sheetName="API")
    g_codeAPI = excel1.read()
    del g_codeAPI[0]
    excel2 = ExcelOperate.Excel(excelName=codeAPIExcel,sheetName="parameter")
    g_config = excel2.read()
    del g_config[0]
    g_apiInfo = []
    g_unAuthAPI = []
except:
    errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
    print errmsg
    exit(0)

def get_originalAPI_from_code(): ## 从源码中获取到的api接口信息，一般是开发提供的接口文档，或者是用雨燕等工具获取的接口信息，按格式存放在APIs.xlsx
    codeAPI = [] ## 格式[[url,method,microService,protocol,port]]
    try:
        for info in g_codeAPI:  #[url,method,Microservice]
            url = str(info[0]).strip()
            method = str(info[1]).strip()
            port = str(info[2]).strip()
            if ":" not in port and "." in port:
                port = port.split(".")[0]
            protocol = str(info[3]).strip()
            microService = str(info[4]).strip()
            parameter = str(info[5]).strip()
            if parameter != "":
                parameter = " -d \"{para}\"".format(para=parameter)
            header = str(info[6]).strip()
            if header != "":
                header = " " + header
            else:
                header = " -H \"Content-Type:application/json;charset=utf8\""
            if protocol == "":
                protocol = "https"
            ports = port.split(";")
            for p in ports:
                if [url,method,microService,protocol,p,parameter,header] in codeAPI:
                    continue
                codeAPI.append([url,method,microService,protocol,p,parameter,header])
    except:
        g_Log.writeLog("traceback")
        return 0
    return codeAPI

def get_registeredAPI_from_netstat(codeAPI):
    global g_apiInfo
    errAPI = [] ##格式[[ip,port]]
    try:
        tempConfig = g_curDir+"/_tempConfig.ini"
        os.system(g_curDir+"/_get_registeredPORT.py")
        file = open(tempConfig)
        info = file.readlines()
        for line in info:
            if "externalPortExcel" in line:
                netstatAPIExcel = line.split("externalPortExcel:")[1].strip()

        regExcel = ExcelOperate.Excel(excelName=netstatAPIExcel,sheetID=0)
        regRead = regExcel.read()
        del regRead[0]
        for tmpAPI in codeAPI:  ## 格式[[url,method,microService,protocol,port]]
            codePort = tmpAPI[4]
            ifFind = False
            for info in regRead: ##格式[[ip,port]]
                netService = str(info[0])
                ip_port = str(info[1])
                if codePort == ip_port.split(":")[1]:
                    g_apiInfo.append([tmpAPI[0],tmpAPI[1],tmpAPI[2],tmpAPI[3],ip_port,tmpAPI[5],tmpAPI[6]])
                    ifFind = True
            if ifFind == False:
                errAPI.append([tmpAPI[0],tmpAPI[1],tmpAPI[2],tmpAPI[3],tmpAPI[4],u"环境中没有找到该端口或端口启动在127.0.0.1"])
    except:
        g_Log.writeLog("traceback")
        return 0
    return errAPI

def get_registeredAPI_from_nginx(codeAPI): ## 如果api接口文档中未提供IP:PORT，则需要脚本到环境中的nginx注册信息中查找。
    global g_apiInfo
    errAPI = [] ## 格式[[url,method,microService,protocol,port,errInfo]]
    try:
        tempConfig = g_curDir+"/_tempConfig.ini"
        os.system(g_curDir+"/_get_registeredAPI.py")
        file = open(tempConfig)
        info = file.readlines()
        for line in info:
            if "registeredAPIExcel" in line:
                registeredAPIExcel = line.split("registeredAPIExcel:")[1].strip()

        regExcel = ExcelOperate.Excel(excelName=registeredAPIExcel,sheetID=0)
        regRead = regExcel.read()
        del regRead[0]

        for tmpAPI in codeAPI:
            url = tmpAPI[0]
            method = tmpAPI[1]
            protocol = tmpAPI[3]
            parameter = tmpAPI[5]
            header = tmpAPI[6]
            regURL = ""
            serverName = ""
            ip_port = ""
            iffind = False
            for info in regRead:  #格式[[LinuxIP,eth0IP,dir,urlNo,nginxURL,serverName,"ip_port,ip_port"]]
                nginxURL = str(info[4])
                serverName = str(info[5])
                ip_port = str(info[6])
                if nginxURL in url:
                    if len(nginxURL) > len(regURL):
                        regURL = nginxURL
                        iffind = True
            if iffind == False:
                errAPI.append([tmpAPI[0],tmpAPI[1],tmpAPI[2],tmpAPI[3],tmpAPI[4],u"环境中没有找到该API的nginx注册信息，请确认"])
                continue
            ports = ip_port.split(",")
            for port in ports:
                g_apiInfo.append([url,method,serverName,protocol,port,parameter,header])
    except:
        g_Log.writeLog("traceback")
        return 0
    return errAPI

def check_registeredAPI(): #主要函数1：校验url是否注册，输出结果：[[url,method,Microservice]]
    errURL = [] ## 格式[[url,method,microService,protocol,port,errInfo]]
    global g_apiInfo,g_unAuthAPI

    codeAPI = get_originalAPI_from_code()  ## 格式[[url,method,microService,protocol,port]]
    if codeAPI[0][4] != "" and ":" in codeAPI[0][4]: # api文档中已经写明了IP:PORT，不需要从环境中获取
        g_apiInfo = codeAPI
    elif codeAPI[0][4] != "" and ":" not in codeAPI[0][4]: # api文档中写明了端口，需要从环境中获取端口监听的IP
        errURL = get_registeredAPI_from_netstat(codeAPI)
    elif codeAPI[0][4] == "": # api文档中没有写端口信息，需要从环境中获取API的nginx注册信息
        errURL = get_registeredAPI_from_nginx(codeAPI)
    for api in g_apiInfo:
        g_unAuthAPI.append([api[0],api[1],api[2],api[3],api[4]])
    return errURL

def check_httpAPI_byCert(): #主要函数2：校验url的证书认证，输出结果：[[url,method,Microservice,serverName,link,errorLog]]
    global g_apiInfo,g_unAuthAPI
    for conf in g_config:
        if conf[0]=="certMethod":
            certMethod = conf[1]
    if certMethod == "" or certMethod == None:
        return []
    messages = []  #格式为[[url,method,Microservice,certLink,simpleLink]]
    for info in g_apiInfo:  #格式[url,method,microService,protocol,port]
        url = info[0]
        method = info[1]
        microService = info[2]
        protocol = info[3]
        port = info[4]
        parameter = info[5]
        turl = url
        turl = correct_parameter(turl)
        simpleLink = "curl -k -X {method} {protocol}://{ip_port}{url}{para}".format(method=method.upper(),ip_port=port,url=turl,protocol=protocol,para=parameter)
        certLink = "curl -k -X {method} {protocol}://{ip_port}{url} {certMethod}{para}".format(method=method.upper(),ip_port=port,url=turl,certMethod=certMethod,protocol=protocol,para=parameter)
        messages.append([url,method,microService,protocol,port,certLink,simpleLink])

    result = []  #格式为[[url,method,microService,certLink,authType,simpleLink,errorLog,result]]
    omCoreIP = g_omCoreInfo[0]
    omCoreUser = g_omCoreInfo[2]
    omCoreUserPasswd = g_omCoreInfo[3]
    omCoreSuRoot = g_omCoreInfo[4]
    omCoreRootPasswd = g_omCoreInfo[5]
    for msg in messages:
        ssh = LinuxOperate.Linux(ip=omCoreIP,user=omCoreUser,password=omCoreUserPasswd,suRoot=omCoreSuRoot,rootPassword=omCoreRootPasswd)
        certLink = msg[5]
        simpleLink = msg[6]
        output = ssh.sendCommand(certLink,timeout=30)
        if output[0]!="":
            response1 = output[0]
        else:
            response1 = output[1]
        res1 = checkResponse(response1)
        if res1[1]=="Pass":
            result.append([u"{x}".format(x=msg[0]),u"{x}".format(x=msg[1]),u"{x}".format(x=msg[2]),u"{x}".format(x=certLink),u"",u"",u"命令下发失败，可能不支持证书认证或接口不存在，请确认",u"ERROR"])
            continue
        output = ssh.sendCommand(simpleLink,timeout=30)
        if output[0]!="":
            response = output[0]
        else:
            response = output[1]
        res = checkResponse(response)
        result.append([u"{x}".format(x=msg[0]),u"{x}".format(x=msg[1]),u"{x}".format(x=msg[2]),u"{x}".format(x=certLink),u"证书认证",u"{x}".format(x=simpleLink),u"{x}".format(x=res[0]),u"{x}".format(x=res[1])])
        if [msg[0],msg[1],msg[2],msg[3],msg[4]] in g_unAuthAPI:
            g_unAuthAPI.remove([msg[0],msg[1],msg[2],msg[3],msg[4]])
        ssh.logout()
    return result

def check_httpAPI_byToken(): #主要函数3：校验url的Token认证，输出结果：[[url,method,Microservice,serverName,link,errorLog]]
    global g_apiInfo,g_unAuthAPI
    for conf in g_config:
        if conf[0]=="tokenMethod":
            tokenMethod = conf[1]
    if tokenMethod == "" or tokenMethod == None:
        return []
    messages = []  #格式为[[url,method,Microservice,certLink,simpleLink]]
    for info in g_apiInfo:  #格式[url,method,microService,protocol,port]
        url = info[0]
        method = info[1]
        microService = info[2]
        protocol = info[3]
        port = info[4]
        parameter = info[5]
        header = info[6]
        turl = url
        turl = correct_parameter(turl)
        simpleLink = "curl -k -X {method} {protocol}://{ip_port}{url}{header}{para}".format(method=method.upper(),ip_port=port,url=turl,protocol=protocol,para=parameter,header=header)
        tokenLink = "token=\"{certMethod}\";curl -k -X {method} {protocol}://{ip_port}{url} -H \"X-Auth-Token:$token\"{header}{para}".format(method=method.upper(),ip_port=port,url=turl,certMethod=tokenMethod,protocol=protocol,para=parameter,header=header)
        messages.append([url,method,microService,protocol,port,tokenLink,simpleLink])

    result = []  #格式为[[url,method,microService,certLink,authType,simpleLink,errorLog,result]]
    omCoreIP = g_omCoreInfo[0]
    omCoreUser = g_omCoreInfo[2]
    omCoreUserPasswd = g_omCoreInfo[3]
    omCoreSuRoot = g_omCoreInfo[4]
    omCoreRootPasswd = g_omCoreInfo[5]
    for msg in messages:
        ssh = LinuxOperate.Linux(ip=omCoreIP,user=omCoreUser,password=omCoreUserPasswd,suRoot=omCoreSuRoot,rootPassword=omCoreRootPasswd)
        tokenLink = msg[5]
        simpleLink = msg[6]
        output = ssh.sendCommand(tokenLink,timeout=30)
        if output[0]!="":
            response1 = output[0]
        else:
            response1 = output[1]
        res1 = checkResponse(response1)
        if res1[1]=="Pass":
            result.append([u"{x}".format(x=msg[0]),u"{x}".format(x=msg[1]),u"{x}".format(x=msg[2]),u"{x}".format(x=tokenLink),u"",u"",u"命令下发失败，可能不支持TOKEN认证或接口不存在，请确认",u"ERROR"])
            continue
        output = ssh.sendCommand(simpleLink,timeout=30)
        print output
        if output[0]!="":
            response = output[0]
        else:
            response = output[1]
        res = checkResponse(response)
        result.append([u"{x}".format(x=msg[0]),u"{x}".format(x=msg[1]),u"{x}".format(x=msg[2]),u"{x}".format(x=tokenLink),u"TOKEN认证",u"{x}".format(x=simpleLink),u"{x}".format(x=res[0]),u"{x}".format(x=res[1])])
        if [msg[0],msg[1],msg[2],msg[3],msg[4]] in g_unAuthAPI:
            g_unAuthAPI.remove([msg[0],msg[1],msg[2],msg[3],msg[4]])
        ssh.logout()
    return result

def check_httpAPI_byAKSK(): #主要函数3：校验url的AKSK认证，输出结果：[[url,method,Microservice,serverName,link,errorLog]]
    global g_apiInfo,g_unAuthAPI
    for conf in g_config:
        if conf[0]=="akskMethod":
            akskMethod = conf[1]
    if akskMethod == "" or akskMethod == None:
        return []
    messages = []  #格式为[[url,method,Microservice,certLink,simpleLink]]
    for info in g_apiInfo:  #格式[url,method,microService,protocol,port]
        url = info[0]
        method = info[1]
        microService = info[2]
        protocol = info[3]
        port = info[4]
        parameter = info[5]
        turl = url
        turl = correct_parameter(turl)
        simpleLink = "curl -k -X {method} {protocol}://{ip_port}{url}{para}".format(method=method.upper(),ip_port=port,url=turl,protocol=protocol,para=parameter)
        akskLink = "curl -k -X {method} https://{ip_port}{url}  -H \"Authorization:Basic {certMethod}\" -H \"Content-Type:application/json;charset=utf8\"{para}".format(method=method.upper(),ip_port=port,url=turl,certMethod=akskMethod,protocol=protocol,para=parameter)
        messages.append([url,method,microService,protocol,port,akskLink,simpleLink])

    result = []  #格式为[[url,method,microService,certLink,authType,simpleLink,errorLog,result]]
    omCoreIP = g_omCoreInfo[0]
    omCoreUser = g_omCoreInfo[2]
    omCoreUserPasswd = g_omCoreInfo[3]
    omCoreSuRoot = g_omCoreInfo[4]
    omCoreRootPasswd = g_omCoreInfo[5]
    for msg in messages:
        ssh = LinuxOperate.Linux(ip=omCoreIP,user=omCoreUser,password=omCoreUserPasswd,suRoot=omCoreSuRoot,rootPassword=omCoreRootPasswd)
        akskLink = msg[5]
        simpleLink = msg[6]
        output = ssh.sendCommand(akskLink,timeout=30)
        if output[0]!="":
            response1 = output[0]
        else:
            response1 = output[1]
        res1 = checkResponse(response1)
        if res1[1]=="Pass":
            result.append([u"{x}".format(x=msg[0]),u"{x}".format(x=msg[1]),u"{x}".format(x=msg[2]),u"{x}".format(x=akskLink),u"",u"",u"命令下发失败，可能不支持AKSK认证或接口不存在，请确认",u"ERROR"])
            continue
        output = ssh.sendCommand(simpleLink,timeout=30)
        if output[0]!="":
            response = output[0]
        else:
            response = output[1]
        res = checkResponse(response)
        result.append([u"{x}".format(x=msg[0]),u"{x}".format(x=msg[1]),u"{x}".format(x=msg[2]),u"{x}".format(x=akskLink),u"AKSK认证",u"{x}".format(x=simpleLink),u"{x}".format(x=res[0]),u"{x}".format(x=res[1])])
        if [msg[0],msg[1],msg[2],msg[3],msg[4]] in g_unAuthAPI:
            g_unAuthAPI.remove([msg[0],msg[1],msg[2],msg[3],msg[4]])
        ssh.logout()
    return result

def check_httpAPI_bySession(): #主要函数3：校验url的session认证，输出结果：[[url,method,Microservice,serverName,link,errorLog]]
    global g_apiInfo,g_unAuthAPI
    for conf in g_config:
        if conf[0]=="sessionMethod":
            sessionMethod = conf[1]
        if conf[0]=="sessionPort":
            sessionPort = conf[1]
    if sessionMethod == "" or sessionMethod == None:
        return []
    messages = []  #格式为[[url,method,Microservice,certLink,simpleLink]]
    for info in g_apiInfo:  #格式[url,method,microService,protocol,port]
        url = info[0]
        method = info[1]
        microService = info[2]
        protocol = info[3]
        port = info[4]
        parameter = info[5]
        if sessionPort != None and sessionPort != "":
            port = sessionPort
        turl = url
        turl = correct_parameter(turl)
        simpleLink = "curl -k -X {method} {protocol}://{ip_port}{url}{para}".format(method=method.upper(),ip_port=port,url=turl,protocol=protocol,para=parameter)
        sessionLink = "curl -k -X {method} {protocol}://{ip_port}{url} {certMethod}{para}".format(method=method.upper(),ip_port=port,url=turl,certMethod=sessionMethod,protocol=protocol,para=parameter)
        messages.append([url,method,microService,protocol,port,sessionLink,simpleLink])

    result = []  #格式为[[url,method,microService,certLink,authType,simpleLink,errorLog,result]]
    omCoreIP = g_omCoreInfo[0]
    omCoreUser = g_omCoreInfo[2]
    omCoreUserPasswd = g_omCoreInfo[3]
    omCoreSuRoot = g_omCoreInfo[4]
    omCoreRootPasswd = g_omCoreInfo[5]
    for msg in messages:
        ssh = LinuxOperate.Linux(ip=omCoreIP,user=omCoreUser,password=omCoreUserPasswd,suRoot=omCoreSuRoot,rootPassword=omCoreRootPasswd)
        sessionLink = msg[5]
        simpleLink = msg[6]
        output = ssh.sendCommand(sessionLink,timeout=30)
        if output[0]!="":
            response1 = output[0]
        else:
            response1 = output[1]
        res1 = checkResponse(response1)
        if res1[1]=="Pass":
            result.append([u"{x}".format(x=msg[0]),u"{x}".format(x=msg[1]),u"{x}".format(x=msg[2]),u"{x}".format(x=sessionLink),u"",u"",u"命令下发失败，可能不支持session认证或接口不存在，请确认",u"ERROR"])
            continue
        output = ssh.sendCommand(simpleLink,timeout=30)
        if output[0]!="":
            response = output[0]
        else:
            response = output[1]
        res = checkResponse(response)
        result.append([u"{x}".format(x=msg[0]),u"{x}".format(x=msg[1]),u"{x}".format(x=msg[2]),u"{x}".format(x=sessionLink),u"session认证",u"{x}".format(x=simpleLink),u"{x}".format(x=res[0]),u"{x}".format(x=res[1])])
        if [msg[0],msg[1],msg[2],msg[3],msg[4]] in g_unAuthAPI:
            g_unAuthAPI.remove([msg[0],msg[1],msg[2],msg[3],msg[4]])
        ssh.logout()
    return result


def check_unAuthAPI(): #主要函数3：校验url的session认证，输出结果：[[url,method,Microservice,serverName,link,errorLog]]
    messages = []  #格式为[[url,method,Microservice,certLink,simpleLink]]
    for info in g_unAuthAPI:  #格式[url,method,microService,protocol,port]
        url = info[0]
        method = info[1]
        microService = info[2]
        protocol = info[3]
        ip_port = info[4]

        turl = url
        turl = correct_parameter(turl)
        ports = ip_port.split(",")
        for port in ports:
            simpleLink = "curl -k -X {method} {protocol}://{ip_port}{url}".format(method=method.upper(),ip_port=port,url=turl,protocol=protocol)
            messages.append([url,method,microService,"",simpleLink])

    result = []  #格式为[[url,method,microService,certLink,authType,simpleLink,errorLog,result]]
    omCoreIP = g_omCoreInfo[0]
    omCoreUser = g_omCoreInfo[2]
    omCoreUserPasswd = g_omCoreInfo[3]
    omCoreSuRoot = g_omCoreInfo[4]
    omCoreRootPasswd = g_omCoreInfo[5]
    for msg in messages:
        ssh = LinuxOperate.Linux(ip=omCoreIP,user=omCoreUser,password=omCoreUserPasswd,suRoot=omCoreSuRoot,rootPassword=omCoreRootPasswd)
        simpleLink = msg[4]
        output = ssh.sendCommand(simpleLink,timeout=30)
        if output[0]!="":
            response = output[0]
        else:
            response = output[1]
        res = checkResponse(response)
        mark=res[1]
        if mark == "Pass":
            mark = "MSG_ERROR"
        result.append([u"{x}".format(x=msg[0]),u"{x}".format(x=msg[1]),u"{x}".format(x=msg[2]),u"",u"未知认证，需要确认认证方式",u"{x}".format(x=simpleLink),u"{x}".format(x=res[0]),u"{x}".format(x=mark)])
        ssh.logout()
    return result

def correct_parameter(para):
    for conf in g_config:    # 配置文件中定义了通用变量，把URL中变量替换成定义的值
        x = re.findall("\{"+conf[0]+"\}",para)
        if x != []:
            para = re.subn("\{"+conf[0]+"\}", conf[1],para)[0]
        x = re.findall("\["+conf[0]+"\]",para)
        if x != []:
            para = re.subn("\["+conf[0]+"\]", conf[1],para)[0]
        x = re.findall("\?:"+conf[0],para)
        if x != []:
            para = re.subn("\?:"+conf[0], conf[1],para)[0]
        x = re.findall(":"+conf[0],para)
        if x != []:
            para = re.subn(":"+conf[0], conf[1],para)[0]

    result = para
    result = re.subn("\{.*?\}", "parameter123",result)[0]    # 把URL中{para}的形式的参数转换成"parameter123"
    result = re.subn("\[.*?\]", "123",result)[0]    # 把URL中[para]的形式的参数转换成"123"
    result = re.subn("\?:\w+", "123",result)[0]    # 把URL中?:para的形式的参数转换成"123"
    result = re.subn(":\w+", "123",result)[0]    # 把URL中:para的形式的参数转换成"123"
    result = result.replace("&","\&")    # 把URL中的&符号转义成"\&"
    x = re.findall("/v(\d)\.0/",result)   # 把URL中v1.0、v2.0等转换成v1、v2的形式
    if x!=[]:
        result = re.subn("/v\d\.0/", "/v{i}/".format(i=x[0]),result)[0]
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
    errCase2 = "^Unauthorized| no token |404 page not found|404 Not Found| must authenticate before making a request|Please login firstly|Authorization failed|Authentication failed|validation does not pass|Authorized failed|Auth failed"
    x = re.findall(errCase1+"|"+errCase2,res,re.IGNORECASE)
    if x != []:
        result = "Pass"
    if "Operation timed out" in res:
        result = "Pass"

    return [res,result]


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
        tempConfig = g_curDir+"/_tempConfig.ini"
        pathExist = os.path.exists(tempConfig)
        if pathExist:
            os.remove(tempConfig)
        file = open( tempConfig,'a' )
        file.write("startTime:"+g_Global.getValue("startTime")+"\n")
        file.close()
    except:
        g_Log.writeLog("traceback")
        return 0
    return 1

# 执行用例
def run():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
        global g_ResultFile,g_unAuthAPI

        resultDir = g_curDir.replace("TestCase","Report")
        startTimeSign = g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")
        g_ResultFile = g_caseName.replace("TestCase","Report").replace(".py","")+"-"+startTimeSign+".xls"
        #g_ResultFile = g_caseName.replace("TestCase","Report").replace(".py","")+"-"+g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")+".xls"
        ## 列出所有未进行认证测试的API接口， #格式[[url,method,microService,protocol,port,errInfo]]
        errAPI = check_registeredAPI()
        if errAPI != []:
            errAPIExcel = resultDir + "/unregisteredAPI-"+startTimeSign+".xls"
            excelErrAPI = ExcelOperate.Excel(excelName=errAPIExcel,sheetID=0)
            excelErrAPI.new()
            excelErrAPI.write([[u"URL",u"Method",u"URL所属微服务",u"protocol",u"port",u"错误信息"]])
            excelErrAPI.write(errAPI)
        '''
        ## 备用：打印所有扫描出来的api端口信息
        allRegisteredAPIExcel = resultDir + "/allRegisteredAPI-"+startTimeSign+".xls"
        allRegisteredResult = ExcelOperate.Excel(excelName=unknowAuthAPIExcel,sheetID=0)
        allRegisteredResult.new()
        allRegisteredResult.write([[u"URL",u"Method",u"URL所属微服务",u"注册的接口前缀",u"注册的业务名称",u"注册的端口信息"]])
        allRegisteredResult.write(g_apiInfo) #[url,method,Microservice,location_url,serverName,ip_port]
        '''
        ## 创建excel用于保存扫描结果
        excelResult = ExcelOperate.Excel(excelName=g_ResultFile,sheetID=0)
        excelResult.new()
        excelResult.write([[u"URL",u"Method",u"URL所属服务",u"含有认证的curl命令",u"支持的认证方式",u"无认证的curl命令",u"执行结果",u"测试结果"]],redLine=3)
        ## 证书认证测试结果
        checkResult = check_httpAPI_byCert()  # 结果格式为[[url,method,microService,certLink,authType,simpleLink,errorLog,result]]
        excelResult.write(checkResult)
        ## Token认证测试结果
        checkResult = check_httpAPI_byToken()  # 结果格式为[[url,method,microService,certLink,authType,simpleLink,errorLog,result]]
        excelResult.write(checkResult)
        ## AKSK认证测试结果
        checkResult = check_httpAPI_byAKSK()  # 结果格式为[[url,method,microService,certLink,authType,simpleLink,errorLog,result]]
        excelResult.write(checkResult)
        ## Session认证测试结果（该功能比较独立，本脚本目录下有另外脚本执行webapp--directrouters目录下注册的API）
        checkResult = check_httpAPI_bySession()  # 结果格式为[[url,method,microService,certLink,authType,simpleLink,errorLog,result]]
        excelResult.write(checkResult)
        ## 以上四种认证都不支持的接口，尝试认证绕过
        checkResult = check_unAuthAPI()  # 结果格式为[[url,method,microService,certLink,authType,simpleLink,errorLog,result]]
        excelResult.write(checkResult)
        '''
        ## 不确定认证方式的URL
        if g_unAuthAPI != []:
            unknowAuthAPIExcel = resultDir + "/unknowAuthAPI-"+startTimeSign+".xls"
            unknowAuthResult = ExcelOperate.Excel(excelName=unknowAuthAPIExcel,sheetID=0)
            unknowAuthResult.new()
            unknowAuthResult.write([[u"URL",u"Method",u"URL所属微服务",u"注册的接口前缀",u"注册的业务名称",u"注册的端口信息"]])
            unknowAuthResult.write(g_unAuthAPI) #[url,method,Microservice,location_url,serverName,ip_port]
        '''
    except:
        g_Log.writeLog("traceback")
        return 0
    return 1

# 执行后清理环境
def clearup():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
        tempConfig = g_curDir+"/_tempConfig.ini"
        pathExist = os.path.exists(tempConfig)
        if pathExist:
            os.remove(tempConfig)
    except:
        g_Log.writeLog("traceback")
        return 0
    return 1

if __name__ == '__main__':
    res = prepare()
    if not res:
        print "错误信息：执行用例prepare模块失败，结束用例{name}的执行".format(name=g_caseName)
    else:
        run()
        clearup()

