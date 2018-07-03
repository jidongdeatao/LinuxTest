#-*- coding: utf-8 -*-

import sys
import os
import traceback
import datetime
import re
import pymysql


from sys import path
# 系统默认Unicode解码，需要换成utf-8形式
reload(sys)
sys.setdefaultencoding('utf-8')


'''
""" 相关安全要求说明 """
DT需求中关于数据库安全的要求
'''
'''
""" 脚本功能 """
扫描系统中数据库安全配置
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
    excel0 = ExcelOperate.Excel(excelName=excelName,sheetName="vmInfo")
    g_vmInfo = excel0.read()
    del g_vmInfo[0]
    dbInformationExcel = g_curDir + "/DatabaseInfo.xlsx"
    excel1 = ExcelOperate.Excel(excelName=dbInformationExcel,sheetName="infomation")
    g_dbInformation = excel1.read()
    del g_dbInformation[0]
    g_ResultFile = g_caseName.replace("TestCase","Report").replace(".py","")+"-"+g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")+".xls"
except:
    errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
    print errmsg
    exit(0)

def scan_all_MySQL():
    errInfo = []
    for db in g_dbInformation:
        serviceIP = db[0]
        for vm in g_vmInfo:
            vmIP = vm[0]
            if vmIP == serviceIP:
                err = scan_in_MV(vm,db)
                errInfo = errInfo+err
    return errInfo



def scan_in_MV(vmInfo,dbInfo):  #结果格式[[vmIP,DBType,DBPort,config,errlog,result,errType]]
    errInfo = []
    try:
        vmIP = vmInfo[0]
        vmName = vmInfo[1]
        vmUser = vmInfo[2]
        vmUserPasswd = vmInfo[3]
        vmSuRoot = vmInfo[4]
        vmRootPasswd = vmInfo[5]

        tLinux = LinuxOperate.Linux(ip=vmIP,name=vmName,user=vmUser,password=vmUserPasswd,suRoot=vmSuRoot,rootPassword=vmRootPasswd)
        output = tLinux.sendRootCommand("ps -ef |egrep \"/mysqld.*--port=[0-9]+\" |grep -v grep")
        if output==False or output[0]=="":
            errInfo.append( [vmIP,u"MySQL",u"",u""  "Check",""] )
            return errInfo
        dbProsses = output[0].split("\n")

        bdUser = dbInfo[2]
        bdPass = dbInfo[3]
        for pro in dbProsses:
            try:
                x0 = re.findall("--defaults-file=/opt/mysql/data/\w+-([0-9_]+)-\d+/my.cnf",pro)
                if x0==False or x0[0]=="":
                    continue
                listenIP = x0[0].replace("_",".")
                x1 = re.findall("--port=([0-9]+)",pro)
                if x1==False or x1[0]=="":
                    continue
                listenPort = x1[0]
                #conn=pymysql.connect(host=self.host,port=self.port,user=self.user,passwd=self.passwd,db=self.db,charset='utf8') #要指定编码，否则中文可能乱码
                conn=pymysql.connect(host=listenIP,port=listenPort,user=bdUser,passwd=bdPass,charset='utf8') #要指定编码，否则中文可能乱码
                errInfo1 = check_MySQL_Config(vmInfo,conn)
                errInfo = errInfo+errInfo1
                conn.close()
            except:
                g_Log.writeLog("traceback")

        errInfo2 = check_VM_Config(tLinux)
        errInfo = errInfo+errInfo2


        tLinux.logout()
    except:
        g_Log.writeLog("traceback")
    return errInfo

def check_MySQL_Config(vmInfo,mysqlSession):  #检查数据库内的配置安全，结果格式[[vmIP,DBType,DBPort,config,errlog,result,errType]]
    errInfo = []
    vmIP = vmInfo[0]
    try:
        ##01、用例SEC-MySQL-C-Author-Account-005：FILE权限允许MySQL用户将文件写入磁盘，影响数据机密性。
        cursor = mysqlSession.cursor()
        cursor.execute("select user from mysql.user where File_priv ='Y';")
        result1 = cursor.fetchall()
        errUser = ""
        for user in result1:
            if user[0] != "root" and user[0] != mysqlSession.user:
                errUser = errUser + user[0] + ","
        if errUser != "":
            errInfo.append( [vmIP,u"MySQL",mysqlSession.host+":"+mysqlSession.port,"\n".join(result1),u"命令select user from mysql.user where File_priv ='Y';查询结果存在不是权限允许的MySQL用户","Fail",u"DT需求（SEC-MySQL-C-Author-Account-005），要求仅权限允许的MySQL用户将文件写入磁盘"] )
        cursor.close()

        ##02、用例SEC-MySQL-C-Author-Account-006：PROCESS权限允许管理员查看当前运行的MySQL语句，包括用来管理密码的语句，这样的权限可能会被攻击者获取来危害MySQL数据库。
        cursor = mysqlSession.cursor()
        cursor.execute("select user from mysql.user where Process_priv ='Y';")
        result1 = cursor.fetchall()
        errUser = ""
        for user in result1:
            if user[0] != "root" and user[0] != mysqlSession.user:
                errUser = errUser + user[0] + ","
        if errUser != "":
            errInfo.append( [vmIP,u"MySQL",mysqlSession.host+":"+mysqlSession.port,"\n".join(result1),u"命令select user from mysql.user where Process_priv ='Y';查询结果存在不是管理员的用户","Fail",u"DT需求（SEC-MySQL-C-Author-Account-006），用例要求仅允许管理员查看当前运行的MySQL语句"] )
        cursor.close()

        ##03、用例SEC-MySQL-C-Author-Account-007：SUPER权限允许管理员查看和终止当前运行的MySQL语句，包括用来管理密码的语句。
        cursor = mysqlSession.cursor()
        cursor.execute("select user from mysql.user where Super_priv ='Y';")
        result1 = cursor.fetchall()
        errUser = ""
        for user in result1:
            if user[0] != "root" and user[0] != mysqlSession.user:
                errUser = errUser + user[0] + ","
        if errUser != "":
            errInfo.append( [vmIP,u"MySQL",mysqlSession.host+":"+mysqlSession.port,"\n".join(result1),u"命令select user from mysql.user where Super_priv ='Y';查询结果存在不是管理员的用户","Fail",u"DT需求（SEC-MySQL-C-Author-Account-007），用例要求仅允许管理员查看和终止当前运行的MySQL语句"] )
        cursor.close()

        ##04、用例SEC-MySQL-C-Author-Account-008：SHUTDOWN权限允许管理员关闭MySQL数据库。 这项权限可能会被攻击者获取来破坏MySQL数据库的可靠性。
        cursor = mysqlSession.cursor()
        cursor.execute("select user from mysql.user where Shutdown_priv ='Y';")
        result1 = cursor.fetchall()
        errUser = ""
        for user in result1:
            if user[0] != "root" and user[0] != mysqlSession.user:
                errUser = errUser + user[0] + ","
        if errUser != "":
            errInfo.append( [vmIP,u"MySQL",mysqlSession.host+":"+mysqlSession.port,"\n".join(result1),u"命令select user from mysql.user where Shutdown_priv ='Y';查询结果存在不是管理员的用户","Fail",u"DT需求（SEC-MySQL-C-Author-Account-008），用例要求仅允许管理员关闭MySQL数据库"] )
        cursor.close()

        ##05、用例SEC-MySQL-C-Author-Account-009：CREATE USER权限允许管理员创建MySQL用户，这样的权限可能会被攻击者获取来危害MySQL数据库。
        cursor = mysqlSession.cursor()
        cursor.execute("select user from mysql.user where Create_user_priv ='Y';")
        result1 = cursor.fetchall()
        errUser = ""
        for user in result1:
            if user[0] != "root" and user[0] != mysqlSession.user:
                errUser = errUser + user[0] + ","
        if errUser != "":
            errInfo.append( [vmIP,u"MySQL",mysqlSession.host+":"+mysqlSession.port,"\n".join(result1),u"命令select user from mysql.user where Create_user_priv ='Y';查询结果存在不是管理员的用户","Fail",u"DT需求（用例SEC-MySQL-C-Author-Account-009），用例要求仅允许管理员创建MySQL用户"] )
        cursor.close()

        ##06、用例SEC-MySQL-C-Author-Account-010：RELOAD权限允许管理员重新加载权限。 非管理员不能修改权限，所以不需要这项权限。
        cursor = mysqlSession.cursor()
        cursor.execute("select user from mysql.user where Reload_priv ='Y';")
        result1 = cursor.fetchall()
        errUser = ""
        for user in result1:
            if user[0] != "root" and user[0] != mysqlSession.user:
                errUser = errUser + user[0] + ","
        if errUser != "":
            errInfo.append( [vmIP,u"MySQL",mysqlSession.host+":"+mysqlSession.port,"\n".join(result1),u"命令select user from mysql.user where Create_user_priv ='Y';查询结果存在不是管理员的用户","Fail",u"DT需求（用例SEC-MySQL-C-Author-Account-010），用例要求仅允许管理员重新加载权限"] )
        cursor.close()

        ##07、用例SEC-MySQL-C-Author-Account-011：GRANT权限允许管理员为其他管理员授予额外权限。 这样的权限可能会被攻击者获取来危害MySQL数据库。
        cursor = mysqlSession.cursor()
        cursor.execute("select user from mysql.user where Grant_priv ='Y';")
        result1 = cursor.fetchall()
        errUser = ""
        for user in result1:
            if user[0] != "root" and user[0] != mysqlSession.user:
                errUser = errUser + user[0] + ","
        if errUser != "":
            errInfo.append( [vmIP,u"MySQL",mysqlSession.host+":"+mysqlSession.port,"\n".join(result1),u"命令select user from mysql.user where Create_user_priv ='Y';查询结果存在不是管理员的用户","Fail",u"DT需求（用例SEC-MySQL-C-Author-Account-011），用例要求仅允许管理员为其他管理员授予额外权限"] )
        cursor.close()

        ##08、用例SEC-GAUSSDB-C-Harden-Patch-001：检查数据库是否为最新版本。
        ##    用例SEC-MySQL-C-Harden-Patch-001  ：低版本的mysql可能存在业界一些已知的公开漏洞，攻击者通过这些漏洞对数据库发起攻击。
        ##    用例SEC-MySQL-C-Harden-Patch-002  ：低版本存在的漏洞或缺陷需要补丁来进行加固，保持MySQL补丁的实时性可以保证MySQL中数据的保密性，完整性，和可靠性。
        ##    用例SEC-SYS-DB-01-001             ：数据库使用当前安全稳定的、主流、且符合三方件要求的版本
        cursor = mysqlSession.cursor()
        cursor.execute("select version();")
        result1 = cursor.fetchall()
        errInfo.append( [vmIP,u"MySQL",mysqlSession.host+":"+mysqlSession.port,"\n".join(result1),u"命令select version();查询结果需要人工确认是否为最新版本","Check",u"DT需求（用例SEC-GAUSSDB-C-Harden-Patch-001），用例要求数据库为最新版本(基本要求大于5.0版本)"] )
        cursor.close()

        ##09、用例SEC-SYS-DB-09-004             ：MySQL的root账户不使用时必须禁用或删除。
        ##    用例SEC-MySQL-C-Authen-Account-010：数据库若存在多个默认帐号，必须将不使用的帐号禁用或删除。
        cursor = mysqlSession.cursor()
        cursor.execute("select user from mysql.user;")
        result1 = cursor.fetchall()
        errUser = True
        for user in result1:
            if user[0] == "root":
                errUser = False
                break
        if errUser == False:
            errInfo.append( [vmIP,u"MySQL",mysqlSession.host+":"+mysqlSession.port,"\n".join(result1),u"命令select user from mysql.user where Create_user_priv ='Y';查询结果存在root用户","Fail",u"DT需求（用例SEC-SYS-DB-09-004），用例要求MySQL的root账户不使用时必须禁用或删除"] )
        cursor.close()

        ##10、用例SEC-MySQL-C-Isolation-Physical-001：数据库若安装在系统分区，操作系统中磁盘可用空间耗尽可能造成拒绝服务。
        cursor = mysqlSession.cursor()
        cursor.execute("show variables like 'datadir';")
        result1 = cursor.fetchall()
        errInfo.append( [vmIP,u"MySQL",mysqlSession.host+":"+mysqlSession.port,"\n".join(result1),u"命令show variables like 'datadir';查询结果需要人工确认是否为系统分区","Check",u"DT需求（用例SEC-MySQL-C-Isolation-Physical-001），用例要求数据库不能安装在系统分区"] )
        cursor.close()

        ##11、用例SEC-SYS-DB-09-002：数据库账号的口令有效期合理（比如90天，根据业务需要设置），不能是口令永远有效。
        cursor = mysqlSession.cursor()
        cursor.execute("select user,password_expired from mysql.user;")
        result1 = cursor.fetchall()
        errUser = True
        for user in result1:
            if user[0] == mysqlSession.user and user[1]=="N":
                errUser = False
                break
        if errUser == False:
            errInfo.append( [vmIP,u"MySQL",mysqlSession.host+":"+mysqlSession.port,"\n".join(result1),u"命令select user,password_expired from mysql.user;查询结果存在数据库账号没有设置有效期","Fail",u"DT需求（用例SEC-SYS-DB-09-002），用例要求数据库账号的口令有效期合理，不能是口令永远有效"] )
        cursor.close()

        ##12、用例SEC-SYS-DB-05-002：数据库需提供安全日志审计功能，并确保审计功能选项开启。
        cursor = mysqlSession.cursor()
        cursor.execute("show variables like \"audit_log%\";")
        result1 = cursor.fetchall()
        errLog = True
        for log in result1:
            if log[0] != "audit_log_connection_policy" or log[1] != "ALL":
                errLog = False
                break
        if errLog == False:
            errInfo.append( [vmIP,u"MySQL",mysqlSession.host+":"+mysqlSession.port,"\n".join(result1),u"命令select user,password_expired from mysql.user;查询结果日志审计功能选项未开启","Fail",u"DT需求（用例SEC-SYS-DB-05-002），数据库需提供安全日志审计功能，并确保审计功能选项开启"] )
        cursor.close()
    except:
        g_Log.writeLog("traceback")
    return errInfo


def check_VM_Config(linuxSSH):  #检查数据库所在服务器的配置安全，结果格式[[vmIP,DBType,DBPort,config,errlog,result,errType]]
    errInfo = []
    try:
        ##01、用例SEC-GAUSSDB-C-Harden-Configure-002：使用操作系统的非管理员权限帐号来运行数据库。
        output = linuxSSH.sendRootCommand("ps -ef |egrep \"/mysqld.*--port=[0-9]+\" |grep -v grep")
        dbProsses = output[0].split("\n")
        for pro in dbProsses:
            x0 = re.findall("^root ",pro)
            if x0!=[]:
                errInfo.append( [linuxSSH.ip,u"MySQL",u"",pro,u"数据库启动在root用户","Fail","安全红线"] )
            x1 = re.findall("^(\w+) ",pro)
            if x1!=[]:
                errInfo.append( [linuxSSH.ip,u"MySQL",u"",pro,u"数据库启动在{user}账户，需人工确认该账户是否为数据库专用账户".format(user=x1[0]),"Check","安全红线"] )

        ##02、用例SEC-SYS-DB-04-001：数据库服务监听不能使用的默认端口（mysql为3306）。
        ##03、用例SEC-SYS-DB-06-001：数据库监听端口小网IP/指定IP，避免监听0.0.0.0等全网IP。
        for pro in dbProsses:
            x2 = re.findall("--port=([0-9]+)",pro)
            if x2==[]:
                errInfo.append( [linuxSSH.ip,u"MySQL",u"",pro,u"进程中没有找到数据库启动端口","Fail","安全红线"] )
                continue
            elif x2[0]=="3306":
                errInfo.append( [linuxSSH.ip,u"MySQL",u"",pro,u"数据库启动在\"3306\"端口","Fail","安全红线"] )
                continue
            res = linuxSSH.sendRootCommand("netstat -tunlp |grep \":{p} \"".format(p=x2[0]))
            netInfo = res[0].strip()
            x3 = re.findall("(\d+\.\d+\.\d+\.\d+):{p}".format(p=x2[0]),pro)
            if x3==[] or x3[0]=="0.0.0.0":
                errInfo.append( [linuxSSH.ip,u"MySQL",u"",netInfo,u"数据库监听在全网IP","Fail","安全红线"] )
            else:
                errInfo.append( [linuxSSH.ip,u"MySQL",u"",netInfo,u"数据库监听IP为\"{ip}\",需人工确认该IP是否为大网IP".format(ip=x3[0]),"Fail","安全红线"] )
    except:
        g_Log.writeLog("traceback")
    return errInfo




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
        errInfo = scan_all_MySQL() #格式[[vmIP,DBType,DBPort,config,errlog,result,errType]]

        excelResult = ExcelOperate.Excel(excelName=g_ResultFile,sheetID=0)
        excelResult.new()
        excelResult.write([[u"主机IP",u"数据库类型",u"数据库端口信息",u"检查配置信息",u"检查说明",u"测试结果",u"备注"]],redLine=1)
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

