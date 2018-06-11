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

    g_allCMD = []
except:
    errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
    print errmsg
    exit(0)


def checkSudoers():  # 主函数功能：校验/etc/sudoers中的配置
    errInfo = []
    for vm in g_vmInfo:
        try:
            global g_allCMD
            g_allCMD = []
            vmIP = vm[0]
            vmName = vm[1]
            vmUser = vm[2]
            vmUserPasswd = vm[3]
            vmSuRoot = vm[4]
            vmRootPasswd = vm[5]
            tLinux = LinuxOperate.Linux(ip=vmIP,name=vmName,user=vmUser,password=vmUserPasswd,suRoot=vmSuRoot,rootPassword=vmRootPasswd)
            output = tLinux.sendRootCommand("ls -al /etc/sudoers")
            fileInfo = output[0].replace('\n','').strip()
            if not 'root root' in fileInfo:
                errInfo.append([vmIP,vmName,u"{key}".format(key=" "+fileInfo),'','',u"/etc/sudoers文件不属于root的属主和属组"])
            if not '-r--------' in fileInfo:
                errInfo.append([vmIP,vmName,u"{key}".format(key=" "+fileInfo),'','',u"/etc/sudoers文件权限可能过大，建议400"])

            output = tLinux.sendRootCommand("grep -rn \"\" /etc/sudoers")
            rs = output[0]
            sudoersInfo = getSudoersConf(rs)
            tRaw = ""
            for info in sudoersInfo:
                info = info.strip()
                tmp = info.split(':')
                raw = tmp[0]
                del tmp[0]
                sudoer = ':'.join(tmp)
                if sudoer == '':
                    continue

                if sudoer[0:1] == "%":
                    if tRaw != raw:
                        errInfo.append([vmIP,vmName,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"/etc/sudoers为用户组(%开头)配置了sudo权限，sudo权限应精确到用户"])

                if sudoer[0:8] == "#include" or sudoer[0:11] == "#includedir":
                    errInfo.append([vmIP,vmName,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"include可能加载了其它sudo配置文件，请人工判断"])
                    continue
                #x = re.findall('NOPASSWD:\s*ALL',sudoer)
                x = re.findall('\(([a-zA-Z]+)\)\s*NOPASSWD:\s*ALL',sudoer)
                if x != [] and (x[0]=="root" or x[0]=="all" or x[0]=="ALL"):
                    errInfo.append([vmIP,vmName,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"/etc/sudoers文件的command字段配置为ALL，sudo命令可以执行任何root权限命令"])
                    continue
                x = re.findall('ALL=\(ALL\)|ALL=\(root\)',sudoer)
                if x == []:
                    errInfo.append([vmIP,vmName,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"自动化未实现该配置的校验，请人工判断"])
                    continue
                x = re.findall('NOPASSWD:',sudoer)
                if x == []:
                    errInfo.append([vmIP,vmName,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"自动化未实现该配置的校验，请人工判断"])
                    continue
                x = re.findall('^root.*ALL',sudoer)
                if x != []:
                    continue

                config = sudoer.split('NOPASSWD:')[1].strip()
                if config != "" and " " not in config:
                    rs1 = checkCMD(info,tLinux)
                    errInfo = errInfo + rs1
                    g_allCMD.append(config)
                elif '*' in config:
                    errInfo.append([vmIP,vmName,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"/etc/sudoers配置中带有*号，可以通过用空格、../、;等组成语句代替*号，修改或执行其他文件"])
                elif 'chmod' in config:
                    errInfo.append([vmIP,vmName,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"/etc/sudoers配置了chmod，请人工判断是否赋予权限过大（目录不大于750，可执行文件不大于750，不可执行文件不大于640，敏感文件不大于600）"])
                elif 'chown' in config:
                    errInfo.append([vmIP,vmName,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"/etc/sudoers配置了chown，如果文件或目录被赋予了普通用户权限，可能存在提权风险"])
                else:
                    errInfo.append([vmIP,vmName,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"自动化未实现该配置的校验，请人工判断"])
                tRaw = raw
            '''
            output = tLinux.sendRootCommand("find /opt -type f -user root |egrep -v \"/devicemapper/mnt/\" 2>/dev/null")
            g_allCMD = g_allCMD + output[0].strip().split("\n")
            output = tLinux.sendRootCommand("find /var -type f -user root |egrep -v \"/devicemapper/mnt/\" 2>/dev/null")
            g_allCMD = g_allCMD + output[0].strip().split("\n")
            output = tLinux.sendRootCommand("find /home -type f -user root  2>/dev/null")
            g_allCMD = g_allCMD + output[0].strip().split("\n")
            err = checkScriptInFile(tLinux)
            '''
            err = checkScriptInFile(tLinux)
            errInfo = errInfo + err
            tLinux.logout()
        except:
            g_Log.writeLog("traceback")
    return errInfo

def checkCMD(info,ssh):
    tmp = info.split(':')
    raw = tmp[0]
    del tmp[0]
    sudoer = ':'.join(tmp)

    errInfo = []
    config = sudoer.split('NOPASSWD:')[1].strip()
    keyLevel0 = ["ls","dir","pwd","id","ps","du","df","who","w","whoami","file","finger","cal","dmidecode","find","wc","stat","ipcs","zip","mkdir","rmdir","touch"]
    keyLevel1 = ["cat","view","more","less","head","tail","awk","stty","rm","vi","sed","dos2unix","cp","mv","gzip","unzip","gunzip","tar","killall","pkill","chkconfig","mount","rpm","unmount","fdisk"]
    keyLevel2 = ["grep","egrep","fgrep","su","sudo","chmod","chown","chgrp","useradd","userdel","groupadd","groupdel","kill","shutdown","init","reboot","halt","poweroff","passwd","mkfs","ifconfig","ethtool","route","sh","bash","ksh","csh","crontab","sysctl"]

    if config[0:1] != '/' or '*' in config:
        errInfo.append([ssh.ip,ssh.name,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"配置的脚本没有指定绝对路径，通过空格、../等方式，有被路径绕过的风险"])
        return errInfo

    output = ssh.sendRootCommand("file {cmd}".format(cmd=config))
    fileType = output[0]
    if "No such file or directory" in fileType:
        errInfo.append([ssh.ip,ssh.name,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"配置的脚本{file}不存在，需删除这一行配置".format(file=config)])
        return errInfo

    x = re.findall("broken symbolic link to `(.*)'",fileType)
    if x != []:
        errInfo.append([ssh.ip,ssh.name,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"{cmd}脚本是软链接，对应的软链接文件{key}不存在，可能被低权限用户创建软链接文件".format(cmd=config,key=x[0])])
        return errInfo
    y = re.findall("symbolic link to `(.*)'",fileType)
    if y != []:
        tmp1 = y[0]
        if ('/' not in tmp1) and ('/' in config):
            c = config.split('/')
            del c[len(c)-1]
            dir = '/'.join(c)
            tmp1 = dir + '/' + tmp1
        config = tmp1
        output = ssh.sendRootCommand("file {cmd}".format(cmd=config))
        fileType = output[0]

    output = ssh.sendRootCommand("stat -c %U {cmd}".format(cmd=config))
    user = output[0].replace('\n','')
    if 'root' not in user:
        errInfo.append([ssh.ip,ssh.name,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"文件不属于root用户，低权限用户\"{key}\"可操作".format(key=user)])

    output = ssh.sendRootCommand("stat -c %A {cmd}".format(cmd=config))
    access = output[0].replace('\n','')
    if access[4:7]>'r-x' and access[7:10]>'---':
        errInfo.append([ssh.ip,ssh.name,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"文件权限\"{key}\"大于750，低权限用户可操作".format(key=access)])

    cmd = config.split('/')[-1]
    if cmd in keyLevel2:
        errInfo.append([ssh.ip,ssh.name,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"需要禁止配置该危险命令{cmd}".format(cmd=cmd)])
        return errInfo
    if cmd in keyLevel1:
        errInfo.append([ssh.ip,ssh.name,"/etc/sudoers",raw,u"{key}".format(key=sudoer),u"配置的危险命令{cmd}需要限制参数范围，应指明命令操作的文件或内容".format(cmd=cmd)])
        return errInfo

    if 'stripped' in fileType:
        return errInfo

    if cmd not in keyLevel0+keyLevel1+keyLevel2:
        scriptFile = []
        scriptFile.append(config)
        output = ssh.sendRootCommand("cat {file}".format(file=config))
        fileRow = output[0].split("\n")
        for f in fileRow:
            f = f.replace('\n','')
            node = f.replace('=',' ').split()
            for n in node:
                if "/" not in n:
                    continue
                output = ssh.sendRootCommand("file {file}".format(file=n))
                fileType1 = output[0]
                if "No such file or directory" not in fileType1:
                    scriptFile.append(config)
        scriptFile = set(scriptFile)

        for tmpFile in scriptFile:
            global g_allCMD
            if tmpFile in g_allCMD:
                continue
            if "/" not in tmpFile:
                continue
            output = ssh.sendRootCommand("file {file}".format(file=tmpFile))
            tempInfo = output[0]
            x = re.findall("broken symbolic link to `(.*)'",tempInfo)
            if x != []:
                errInfo.append([ssh.ip,ssh.name,tmpFile,'','',u"{file}文件是软链接，软链接文件{key}不存在，可能被低权限用户创建软链接文件".format(file=tmpFile,key=x[0])])
                continue
            y = re.findall("symbolic link to `(.*)'",tempInfo)
            if y != []:
                tmpFile = y[0]

            g_allCMD.append(tmpFile)
            output = ssh.sendRootCommand("stat -c %U {file}".format(file=tmpFile))
            user = output[0].replace('\n','')
            if 'root' not in user:
                errInfo.append([ssh.ip,ssh.name,tmpFile,'','',u"{file}文件不属于root用户，低权限用户\"{key}\"可操作".format(file=tmpFile,key=user)])

            output = ssh.sendRootCommand("stat -c %A {file}".format(file=tmpFile))
            access = output[0].replace('\n','')
            if '-rwxr-x---'<access:
                errInfo.append([ssh.ip,ssh.name,tmpFile,'','',u"{file}文件权限\"{key}\"大于750，低权限用户可操作".format(file=tmpFile,key=access)])

            output = ssh.sendRootCommand("grep -rn \"\" {file}".format(file=tmpFile))
            fileRow = output[0].split('\n')
            allPara = []
            for f in fileRow:
                f = f.replace('\n','')
                temp = f.split(":")
                raw = temp[0]
                del temp[0]
                line = ':'.join(temp)

                x1 = re.findall('^\s*#',line)
                if x1!=[]:
                    continue

                p = re.findall('(\w+)=',f)
                if p!=[]:
                    allPara = allPara+p

                temp = line.replace('=',' ').split()

                if 'chmod' in temp:
                    errInfo.append([ssh.ip,ssh.name,tmpFile,raw,u"{key}".format(key=line),u"{file}脚本中配置了chmod，请人工判断是否赋予权限过大（目录不大于750，可执行文件不大于750，不可执行文件不大于640，敏感文件不大于600）".format(file=tmpFile)])
                if 'chown' in temp:
                    errInfo.append([ssh.ip,ssh.name,tmpFile,raw,u"{key}".format(key=line),u"{file}脚本中配置了chown，请人工判断是否赋予权限过大（如果文件或目录被赋予了普通用户权限，可能存在提权风险）".format(file=tmpFile)])

                for t in temp:
                    x = re.findall('(\$\w+)',t)

                    t = t.replace('\"','')
                    if "/" not in t:
                        continue
                    output = ssh.sendRootCommand("file \"{file}\"".format(file=t))
                    fileType2 = output[0]

                    if ( t[0:1]=="/" and "No such file or directory" not in fileType2 ) or ('./' in t):
                        errInfo.append([ssh.ip,ssh.name,tmpFile,raw,u"{key}".format(key=line),u"{file}脚本中调用了其它脚本{key}，请手动判断{key}的安全（文件权限不大于750、属主为root、参数引入白名单配置等）".format(file=tmpFile,key=t)])
                    elif '.sh' in t:
                        errInfo.append([ssh.ip,ssh.name,tmpFile,raw,u"{key}".format(key=line),u"{file}脚本中调用了sh脚本，请手动判断sh脚本的安全（文件权限不大于750、属主为root、参数引入白名单配置等）".format(file=tmpFile)])
                    elif x!=[] and x[0][1:] not in allPara:
                        errInfo.append([ssh.ip,ssh.name,tmpFile,raw,u"{key}".format(key=line),u"{file}脚本中引用了外部参数{key}，请手动进一步判断引用的外部参数的安全（应该限制访问范围，做外部参数白名单校验）".format(file=tmpFile,key=x[0])])
    return errInfo

def getSudoersConf(sudoers): # 处理sudoers文件中的配置
    conf_f = []
    sudoers = sudoers.strip()
    if sudoers=="" or sudoers=="\n":
        conf_f = conf_f + []
    else:
        conf_f = conf_f + sudoers.split("\n")
    conf_g = []
    for c in conf_f:
        c1 = c.strip()
        x = re.findall('\(ALL\)|\(root\)',c1)
        if len(x) < 2:
            conf_g.append( c1 )
            continue
        x = re.split('\(ALL\)|\(root\)',c1)
        suf = x[0]
        del x[0]
        for c2 in x:
            if c2[-1:] == ",":
                c2 = c2.rstrip()[0:-1]
            conf_g.append( suf+"(ALL)"+c2 )

    conf_s = []
    for c in conf_g:
        c1 = c.strip()
        x = re.findall('^\d+:(.*)',c1)

        if x == []:
            continue

        c1 = x[0]
        if c1[0:8] == "#include" or c1[0:11] == "#includedir":
            conf_s.append( c )
        if c1[0:1] != "#" and c1[0:8] != "Defaults":
            conf_s.append( c )
    return conf_s

def checkScriptInFile(linux): # 主函数功能：校验运行脚本的操作权限
    errInfo = []
    saveDirs = []
    errDirs = []
    fileInfo = list(set(g_allCMD))
    for file in fileInfo:
        try:
            length = len(file.split("/"))
            dirs = []
            dir = file
            for i in range(0,length-2):
                dir = os.path.split(dir)[0]
                dirs.append(dir)
            dirs.reverse()
            if dirs == []:
                continue
            for dir in dirs:
                if dir in saveDirs:
                    continue
                if dir in errDirs:
                    errInfo.append([linux.ip,linux.name,file,"","",u"root文件所在目录{dir}，others用户可操作，存在越权风险".format(dir=dir)])
                    continue
                output = linux.sendRootCommand("stat -c %A {file}".format(file=dir))
                access = output[0].replace('\n','').strip()
                if access == "":
                    continue
                output = linux.sendRootCommand("stat -c %U {file}".format(file=dir))
                user = output[0].replace('\n','').strip()
                if user == "root":
                    if access[-2:]=="wx":
                        errInfo.append([linux.ip,linux.name,file,"","",u"文件属于root用户，但其所在目录{dir}权限为{access}，others用户可操作，存在越权风险".format(dir=dir,access=access)])
                        errDirs.append(dir)
                    else:
                        saveDirs.append(dir)
                if user != "root":
                    errInfo.append([linux.ip,linux.name,file,"","",u"文件属于root用户，但其所在目录{dir}属于{user}用户，{user}用户可操作，存在越权风险".format(dir=dir,user=user)])
                    continue
        except:
            #errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
            g_Log.writeLog("traceback")
    return errInfo

def checkDirAccess(): # 主函数功能：校验运行脚本的操作权限
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
            output = tLinux.sendRootCommand("find / -type d -user root -perm -750 ! -perm 750 -exec ls -ld {key} \; 2>/dev/null |egrep \"^........wx\" | egrep -v \"/proc/\"".format(key="{}"))
            dirInfo = output[0].strip().split("\n")
            if dirInfo == [""] or dirInfo == []:
                continue
            for info in dirInfo:
                dir = re.findall("(/.*)",info)[0]
                access = re.findall("(^.*?) ",info)[0]
                if dir == "/":
                    continue
                errInfo.append([vmIP,vmName,dir,"","",u"目录{dir}属于root用户，但其权限为{access}，others用户可操作，该目录下的所有脚本可能存在越权风险".format(dir=dir,access=access)])

            output = tLinux.sendRootCommand("find / -type d ! -user root -exec ls -ld {key} \; 2>/dev/null | egrep -v \"/proc/|/devicemapper/\"".format(key="{}"))
            dirInfo = output[0].strip().split("\n")
            fileDir = []
            for dinfo in dirInfo:
                dir = re.findall(" (/.*)",dinfo)[0]
                dir = "/"+dir.split("/")[1]
                if dir == "/proc":
                    continue
                fileDir.append(dir)
            fileDir = list(set(fileDir))
            fileInfo = []
            tLinux.logout()
            for fdir in fileDir:
                tLinux = LinuxOperate.Linux(ip=vmIP,name=vmName,user=vmUser,password=vmUserPasswd,suRoot=vmSuRoot,rootPassword=vmRootPasswd)
                output = tLinux.sendRootCommand("find {dir} -type f -user root -exec ls -ld {key} \; 2>/dev/null | egrep -v \"/devicemapper/\"".format(dir=fdir,key="{}"))
                fileInfo = fileInfo + output[0].strip().split("\n")
                tLinux.logout()

            for dinfo in dirInfo:
                dir = re.findall(" (/.*)",dinfo)[0]
                user = dinfo.split()[2]
                for finfo in fileInfo:
                    try:
                        file = re.findall(" (/.*)",finfo)
                        if file == []:
                            continue
                        file = file[0]
                        if dir in file:
                            errInfo.append([vmIP,vmName,dir,"","",u"目录{dir}属于{user}用户，该目录下存在root用户的脚本或文件，可能存在越权风险".format(file=file,dir=dir,user=user)])
                            break
                    except:
                        #errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
                        g_Log.writeLog("traceback")


            '''
            for finfo in fileInfo:
                file = re.findall(" (/.*)",finfo)[0]
                for dinfo in dirInfo:
                    dir = re.findall(" (/.*)",dinfo)[0]
                    user = dinfo.split()[2]
                    if dir in file:
                        errInfo.append([vmIP,vmName,file,"","",u"文件{file}属于root用户，但其所在目录{dir}属于{user}用户，存在越权风险".format(file=file,dir=dir,user=user)])
            '''
        except:
            #errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
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
        #errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
        g_Log.writeLog("traceback")
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

        excelResult = ExcelOperate.Excel(excelName=g_ResultFile,sheetID=0)
        excelResult.new()
        excelResult.write([[u"主机IP",u"主机名",u"文件名",u"行号",u"内容",u"问题描述"]],redLine=1)
        checkResult1 = checkSudoers()
        checkResult2 = checkDirAccess()
        excelResult.write(checkResult1+checkResult2)

    except:
        #errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
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

