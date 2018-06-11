#-*- coding: utf-8 -*-

import sys
import os
import traceback
import datetime
import re


from sys import path
reload(sys)
sys.setdefaultencoding('utf-8')


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
        g_omCoreInfo = [vm[0], vm[1], vm[2], vm[3], vm[4], vm[5]]
    g_errInfo = []
    g_ResultFile = g_caseName.replace("TestCase","Report").replace(".py","")+"-"+g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")+".xls"
except:
    errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
    print errmsg
    exit(0)

def get_roleInfo():
    global g_errInfo  #格式为[[roleName,url,method,tokenLink,support,response,errInfo,result]]
    roleInfo = []
    roleExcel = g_curDir + "/Authorization_Role.xlsx"
    excel1 = ExcelOperate.Excel(excelName=roleExcel,sheetName="RoleAuthority")
    roleSet = excel1.read()
    excel2 = ExcelOperate.Excel(excelName=roleExcel,sheetName="parameter")
    parameters = excel2.read()
    del parameters[0]
    apiNum = len(roleSet)
    roleNames = []
    tempInfo = []
    for i in range(0,apiNum):
        tmprole = roleSet[i]
        sup = []
        if i == 0:
            roleNum = len(tmprole)-4
            for i in range(0,roleNum):
                roleNames.append(tmprole[i+4])
            continue
        else:
            roleNum = len(tmprole)-4
            for i in range(0,roleNum):
                sup.append(tmprole[i+4])
        method = tmprole[1]
        url = tmprole[2]
        port = tmprole[3]

        roleNum = len(roleNames)
        for i in range(0,roleNum):
            tempInfo.append([roleNames[i],url,method,port,sup[i]])

    for info in tempInfo:
        roleName = info[0]
        url = info[1]
        method = info[2]
        port = info[3]
        support = info[4]
        tmpToken = ""
        for para in parameters:
            if para[0] == roleName+"_token":
                tmpToken = para[1]
            x = re.findall("\{"+para[0]+"\}|:"+para[0],url)
            if x != []:
                url = re.subn("\{"+para[0]+"\}", para[1],url)[0]
                url = re.subn(":"+para[0], para[1],url)[0]
        if tmpToken == "":
            g_errInfo.append([roleNames[i],u"",u"",u"",u"",u"",u"没有配置token值，无法测试",u"Error"])
            continue
        tokenLink = "token=\"{token}\";curl -k -X {method} https://{ip_port}{url}  -H \"X-Auth-Token:$token\"".format(method=method.upper(),ip_port=port,url=url,token=tmpToken)
        roleInfo.append([roleName,url,method,support,tokenLink])
    return roleInfo

def check_role(roleInfo):
    global g_errInfo   #格式为[[roleName,url,method,tokenLink,support,response,errInfo,result]]
    omCoreIP = g_omCoreInfo[0]
    omCoreUser = g_omCoreInfo[2]
    omCoreUserPasswd = g_omCoreInfo[3]
    omCoreSuRoot = g_omCoreInfo[4]
    omCoreRootPasswd = g_omCoreInfo[5]
    ssh = LinuxOperate.Linux(ip=omCoreIP,user=omCoreUser,password=omCoreUserPasswd,suRoot=omCoreSuRoot,rootPassword=omCoreRootPasswd)
    for role in roleInfo: #[roleName,url,method,support,tokenLink]
        tokenLink = role[4]
        support = role[3]
        output = ssh.sendCommand(tokenLink,timeout=30)
        if output[0]!="":
            response = output[0]
        else:
            response = output[1]
        res = checkResponse(response)
        if res[1]=="Error":
            g_errInfo.append([u"{x}".format(x=role[0]),u"{x}".format(x=role[1]),u"{x}".format(x=role[2]),u"{x}".format(x=role[4]),u"",u"{x}".format(x=role[3]),u"命令返回失败，可能是参数错误或接口错误，请检查",u"Error"])
        elif (res[1]=="Pass" and support=="Y") or (res[1]=="Fail" and support=="N"):
            g_errInfo.append([u"{x}".format(x=role[0]),u"{x}".format(x=role[1]),u"{x}".format(x=role[2]),u"{x}".format(x=role[4]),u"{x}".format(x=res[0]),u"{x}".format(x=role[3]),u"角色权限与命令结果不符，需定位",u"Fail"])
        else:
            g_errInfo.append([u"{x}".format(x=role[0]),u"{x}".format(x=role[1]),u"{x}".format(x=role[2]),u"{x}".format(x=role[4]),u"{x}".format(x=res[0]),u"{x}".format(x=role[3]),u"角色权限与命令结果相符",u"Pass"])

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
    if x != []:
        result = "Error"
    if "Operation timed out" in res:
        result = "Error"
    if "Permission denied" in res:
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
        roleInfo = get_roleInfo()
        check_role(roleInfo)

        ## 创建excel用于保存扫描结果 ,格式为[[roleName,url,method,tokenLink,support,response,errInfo,result]]
        excelResult = ExcelOperate.Excel(excelName=g_ResultFile,sheetID=0)
        excelResult.new()
        excelResult.write([[u"角色名称",u"接口",u"方法",u"认证命令",u"命令返回信息",u"角色权限",u"执行结果",u"测试结果"]],redLine=4)
        excelResult.write(g_errInfo)
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

