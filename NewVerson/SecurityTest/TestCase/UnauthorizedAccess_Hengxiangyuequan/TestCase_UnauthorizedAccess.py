#-*- coding: utf-8 -*-

import sys
import os
import traceback
import datetime
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
先由开发提供角色权限信息，通过该脚本，可以对这些接口进行鉴权测试。
'''
'''
""" 脚本配置执行说明 """
配置1：/SecurityTest/Config/config.xlsx，“vmInfo”页，只需要配置一台虚机信息即可，确保该虚机能连通环境中所有其它虚机，“是否kubectl节点”要置为TRUE
配置2：本脚本所在目录下的accessConfig.xlsx，“api”页。每一列配置表头都有批注说明，请仔细阅读。
配置3：本脚本所在目录下的accessConfig.xlsx，“parameter”页。每一行配置都有说明，请仔细阅读。
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
            g_omCoreInfo = [vm[0], vm[1], vm[2], vm[3], vm[4], vm[5]]
    g_apiInfo = []
    g_errInfo = []
    g_ResultFile = g_caseName.replace("TestCase","Report").replace(".py","")+"-"+g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")+".xls"
except:
    errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
    print errmsg
    exit(0)

def get_apiInfo():
    global g_apiInfo  #格式为[[webMark,method,url,port,head,user1_body,user2_body]]
    roleExcel = g_curDir + "/accessConfig.xlsx"
    excel1 = ExcelOperate.Excel(excelName=roleExcel,sheetName="api")
    configs = excel1.read()
    del configs[0]
    mark = 0
    webMark = ""
    tempInfo = []
    for conf in configs:
        try:
            if conf[4].strip()=="":
                continue
            env = conf[0].strip()
            if env!="":
                mark = mark + 1
                webMark = str(mark)
                if conf != configs[0]:
                    g_apiInfo.append(tempInfo)
                tempInfo = []
                #tempInfo.append(webMark)
            tempInfo.append([conf[2],conf[3],conf[4],conf[5],conf[6]])
            if conf == configs[-1]:
                g_apiInfo.append(tempInfo)
        except:
            g_Log.writeLog("traceback")

    return 1

def runScene(): #执行一种场景（功能）下的api（遍历创建、查询、修改、删除）
    omCoreIP = g_omCoreInfo[0]
    omCoreUser = g_omCoreInfo[2]
    omCoreUserPasswd = g_omCoreInfo[3]
    omCoreSuRoot = g_omCoreInfo[4]
    omCoreRootPasswd = g_omCoreInfo[5]
    ssh = LinuxOperate.Linux(ip=omCoreIP,user=omCoreUser,password=omCoreUserPasswd,suRoot=omCoreSuRoot,rootPassword=omCoreRootPasswd)
    roleExcel = g_curDir + "/accessConfig.xlsx"
    excel1 = ExcelOperate.Excel(excelName=roleExcel,sheetName="parameter")
    configs = excel1.read()
    del configs[0]
    for conf in configs:
        if conf[0] == "user1_name":
            user1_name = conf[1]
        if conf[0] == "user2_name":
            user2_name = conf[1]
        if conf[0] == "user1_token":
            user1_token = conf[1]
        if conf[0] == "user2_token":
            user2_token = conf[1]
    for apis in g_apiInfo:
        for api in apis:
            method = api[0]
            url = api[1]
            ip_port = api[2]
            head = api[3]
            user1_body = api[4]
            check_apiAccess(ssh,user1_name,user2_name,user1_token,user2_token,method,url,ip_port,head,user1_body)

    return 1

# 对比结果：[[url,method,correctLink,response,errorLink,response,errInfo,result]]
def check_apiAccess(ssh,user1_name,user2_name,user1_token,user2_token,method,url,ip_port,head,user1_body):
    global g_errInfo
    if head == "":
        head = " -H \"Content-Type:application/json;charset=utf8\""
    if user1_body.strip() != "" and user1_body.strip().split()[0] != "-d":
        user1_body = " -d\'"+user1_body+"\'"
    correctLink = "token=\"{token}\";curl -k -X {method} https://{ip_port}{url} -H \"X-Auth-Token:$token\" {head} {body}".format(method=method.upper(),ip_port=ip_port,url=url,token=user1_token,head=head,body=user1_body)
    errorLink = "token=\"{token}\";curl -k -X {method} https://{ip_port}{url} -H \"X-Auth-Token:$token\" {head} {body}".format(method=method.upper(),ip_port=ip_port,url=url,token=user2_token,head=head,body=user1_body)
    correctLink = correctLink.replace("&","\&")
    errorLink = errorLink.replace("&","\&")

    errorOutput = ssh.sendCommand(errorLink,timeout=120)
    if errorOutput==False:
        errorOutput = ssh.sendCommand(errorLink,timeout=120)
    if errorOutput==False:
        return 0

    correctOutput = ssh.sendCommand(correctLink,timeout=120)
    if correctOutput==False:
        return 0
    response = correctOutput[0]
    if response=="":
        response = correctOutput[1]
    res = checkResponse(response)
    if "Operation timed out" in correctOutput[1]:
        g_errInfo.append([url,method,correctLink,"","","",u"用账号{user1}执行curl命令超时，请手动进一步验证".format(user1=user1_name),u"Check"])
        return 0
    if res[1] == "Fail":
        g_errInfo.append([url,method,correctLink,u"{x}".format(x=res[0]),"","",u"用账号{user1}执行curl命令失败，可能是接口或参数有问题，请手动进一步验证".format(user1=user1_name),u"Check"])
        return 0
    if correctOutput[0] == "":
        g_errInfo.append([url,method,correctLink,"","",u"用账号{user1}执行该接口，没有返回任何信息，请手动进一步验证".format(user1=user1_name),u"Check"])
        return 0
    if errorOutput[0] == correctOutput[0]:
        g_errInfo.append([url,method,correctLink,u"{x}".format(x=correctOutput[0]),errorLink,u"{x}".format(x=errorOutput[0]),u"该接口，账号{user1}执行结果与{user2}执行结果一致，可能存在横向越权风险，请确认执行结果".format(user1=user1_name,user2=user2_name),u"Fail"])
        return 0
    g_errInfo.append([url,method,correctLink,u"{x}".format(x=correctOutput[0]),errorLink,u"{x}".format(x=errorOutput[0]),u"该接口，账号{user1}执行结果与{user2}执行结果不一致，脚本认为没有越权风险，但请人工再确认一下返回结果".format(user1=user1_name,user2=user2_name),u"Pass"])

    return 1


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
    errCase2 = "^Unauthorized| no token |404 page not found|404 Not Found| must authenticate before making a request|Please login firstly|Authorization failed|validation does not pass|Authorized failed|Auth failedl"
    x = re.findall(errCase1+"|"+errCase2,res,re.IGNORECASE)
    if x == []:
        result = "Pass"
    return [res,result]

'''
""" 以下定义的函数，请在特定位置添加自己的代码 """
'''
# 执行前的准备操作
def prepare():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
    except:
        g_Log.writeLog("traceback")
        return 0
    return 1

# 执行用例
def run():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
        get_apiInfo()
        runScene()

        global g_ResultFile

        ## 创建excel用于保存扫描结果 ,格式为[[url,method,correctLink,response,errorLink,response,errInfo,result]]
        roleExcel = g_curDir + "/accessConfig.xlsx"
        excel1 = ExcelOperate.Excel(excelName=roleExcel,sheetName="parameter")
        configs = excel1.read()
        del configs[0]
        for conf in configs:
            if conf[0] == "user1_name":
                user1_name = conf[1]
            if conf[0] == "user2_name":
                user2_name = conf[1]
        excelResult = ExcelOperate.Excel(excelName=g_ResultFile,sheetID=0)
        excelResult.new()
        excelResult.write([[u"URL",u"Method",u"账号{user1}测试接口命令".format(user1=user1_name),u"账号{user1}测试接口返回结果".format(user1=user1_name),u"账号{user2}测试接口命令".format(user2=user2_name),u"账号{user2}测试接口返回结果".format(user2=user2_name),u"错误信息",u"测试结果"]],redLine=2)
        excelResult.write(g_errInfo)

    except:
        g_Log.writeLog("traceback")
        return 0
    return 1

# 执行后清理环境
def clearup():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''

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

