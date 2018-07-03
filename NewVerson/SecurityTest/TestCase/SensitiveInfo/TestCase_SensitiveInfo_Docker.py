#-*- coding: utf-8 -*-

import sys
import os
import traceback
import datetime
import re
import time
import shutil


from sys import path
# 系统默认Unicode解码，需要换成utf-8形式
reload(sys)
sys.setdefaultencoding('utf-8')


'''
""" 相关安全要求说明 """
《01 产品网络安全红线落地解读及指导V2_1.xls》：
        7.1.1 认证凭据不允许明文存储在系统中，应该加密保护。
        7.1.2 在非信任网络之间进行敏感数据（包括口令，银行帐号，批量个人数据等）的传输须采用安全传输通道或者加密后传输，有标准协议规定除外。
        7.1.8 禁止使用公司认定的不安全的加密算法
《中央软件院网络安全测试基线V2.0.xlsx》 中关于系统中中敏感信息、明文密码、加密算法、解释性语言、调试命令等要求
'''
'''
""" 脚本功能 """
扫描系统中的敏感信息、明文密码、加密算法、解释性语言、调试命令等问题点，扫描策略见本脚本所在目录下的scanSensitivePolicy.xlsx
'''
'''
""" 脚本配置执行说明 """
配置1：本脚本所在目录下的scanSensitivePolicy.xlsx，“policy”页。
配置2：本脚本所在目录下的scanSensitivePolicy.xlsx，“config”页。每一行配置都有说明，请仔细阅读。
配置3：本脚本所在目录下的scanSensitivePolicy.xlsx，其它页。每一列配置都有批注说明，请仔细阅读。（不要轻易维护，需要正则表达式精通的人员维护）
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
    scanPolicyExcel = g_curDir + "/scanSensitivePolicy.xlsx"
    excel1 = ExcelOperate.Excel(excelName=scanPolicyExcel,sheetName="policy")
    g_scanPolicy = excel1.read()
    del g_scanPolicy[0]
    excel2 = ExcelOperate.Excel(excelName=scanPolicyExcel,sheetName="config")
    g_config = excel2.read()
    del g_config[0]
    g_ResultFile = g_caseName.replace("TestCase","Report").replace(".py","")+"-"+g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")+".xls"
except:
    errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
    print errmsg
    exit(0)

def getScanPolicy(): #获取所有支持系统扫描的策略信息
    global g_scanPolicy
    policy = []
    for p in g_scanPolicy:
        supportSys = p[6].lower()
        if p[0].lower() == "true" and "docker" in supportSys.lower():
            policy.append(p)
    g_scanPolicy = policy
    return 1

def adaptFileNames(fileTypes): #处理扫描策略中的“文件名”，使变成shell格式命令
    files = ""
    if fileTypes=="":
        return files
    fileTypes = fileTypes.replace(" ","")
    for f in fileTypes.split(";"):
        if "*" in f:
            f = f.split("*")[1]
        files = files+" -name \"*{file}\" -o".format(file=f)
    files = files[:-3]
    return files

def adaptIgnoreDirs(ignoreDir):
    dirs = ""
    if ignoreDir == "":
        return dirs
    ignoreDir = ignoreDir.replace(" ","")
    for d in ignoreDir.split(";"):
        dirs = dirs+" -path {dir} -prune -o".format(dir=d)
    return dirs

def adaptIgnoreKeysExcel(ignoreKeySheet):
    keys = ""
    try:
        excel = ExcelOperate.Excel(excelName=scanPolicyExcel,sheetName=ignoreKeySheet)
        ignoreKeys = excel.read()
        if ignoreKeys == False:
            return keys
        del ignoreKeys[0]
        for x in ignoreKeys:
            if x[1].lower() == "shell":
                keys = keys + x[0] + "|"
        if keys != "":
            keys = "|egrep -i -v \"{k}\"".format(k=keys[:-1])
    except:
        g_Log.writeLog("traceback")
    return keys

def scan_in_MV():
    reportPath = g_caseName.replace("TestCase","Report").replace(".py","")+"-"+g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")
    if not os.path.exists(reportPath):
        os.makedirs(reportPath)
    shutil.copy(g_curDir+"/scanSensitivePolicy.xlsx",reportPath+"/scanSensitivePolicy.xlsx")
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
            tDocker.logout()
            tLinux = LinuxOperate.Linux(ip=vmIP,name=vmName,user=vmUser,password=vmUserPasswd,suRoot=vmSuRoot,rootPassword=vmRootPasswd)
            tLinux.sendRootCommand("rm -rf /tempScanDocker")
            # 创建临时存放脚本的路径，会从该路径下拷贝到容器中
            tLinux.sendRootCommand("mkdir /tempScanDocker")
            tLinux.sendRootCommand("chmod 777 /tempScanDocker")
            for scan in g_scanPolicy:
                name = scan[1]
                policy = scan[2]
                fileType = scan[3]
                workDir = scan[4]
                ignoreDir = scan[5]
                appointFiles = adaptFileNames(fileType)
                ignoreDirs = adaptIgnoreDirs(ignoreDir)
                uselessWords = adaptIgnoreKeysExcel(name)
                dirs = workDir.split(";")
                cmd = ""
                for dir in dirs:
                    info = "find {dir} {iDir} -type f {scanFile} | xargs file|grep -E 'text|XML|PC bitmap data'|awk '{p}'|sed 's/:$//g'|xargs grep -i -n -E -H \"{key}\" |egrep -i -v \"/devicemapper/mnt/|Binary file|/usr/lib(64|)/python2\.7/|tempScan\" {uselessWords} 2>/dev/null".format(dir=dir,key=policy,p="{print $1}",scanFile=appointFiles,iDir=ignoreDirs,uselessWords=uselessWords)
                    if "FIND_Password" in name:
                        info = info.replace("-i -n -E -H","-i -a -n -E -H")

                    if '\\' in info:
                        info = info.replace('\\', '\\\\')
                    if '$' in info:
                        info = info.replace('$', '\$')
                    if '"' in info:
                        info = info.replace('"', '\\"')
                    if '`' in info:
                        info = info.replace('`', '\\`')
                    cmd = cmd + info + " >> /tempScanDocker/{name}.txt".format(name=name) + "\n"

                #tLinux.sendRootCommand("rm -rf /tempScanDocker/{name}.sh".format(name=name))
                # 创建扫描脚本
                tLinux.sendCommand('echo \"{cmd}\" >> /tempScanDocker/{name}.sh'.format(cmd=cmd,name=name))
                tLinux.sendCommand('echo \"echo \\\"#### note:end scanning\\\" >> /tempScanDocker/{name}.txt\" >> /tempScanDocker/{name}.sh'.format(name=name)) # 脚本执行完，增加end标记
                tLinux.sendRootCommand("chmod 777 /tempScanDocker/{name}.sh".format(name=name))
                # 创建扫描脚本的后台执行脚本
                tLinux.sendCommand('echo \"/usr/bin/sh /tempScanDocker/{name}.sh &\">/tempScanDocker/scan_{name}.sh'.format(name=name))
                tLinux.sendRootCommand("chmod 777 /tempScanDocker/scan_{name}.sh".format(name=name))
                for container in containerInfo:
                    try:
                        id = container[1]
                        mntDir = container[2]
                        output = tLinux.sendRootCommand("docker ps |grep {id}".format(id=id))
                        if output==False or output[0]=="":
                            continue
                        # 创建容器临时扫描路径
                        cmd = "mkdir /tempScanDocker"
                        tLinux.sendRootCommand("docker exec -u 0 {id} {cmd}".format(id=id,cmd=cmd))
                        cmd = "chmod 777 /tempScanDocker"
                        tLinux.sendRootCommand("docker exec -u 0 {id} {cmd}".format(id=id,cmd=cmd))
                        # 拷贝容器扫描脚本
                        tLinux.sendRootCommand("cp /tempScanDocker/{name}.sh {dir}/tempScanDocker/{name}.sh".format(dir=mntDir,name=name))
                        tLinux.sendRootCommand("cp /tempScanDocker/scan_{name}.sh {dir}/tempScanDocker/scan_{name}.sh".format(dir=mntDir,name=name))
                        cmd = "chmod 777 /tempScanDocker/{name}.sh".format(name=name)
                        tLinux.sendRootCommand("docker exec -u 0 {id} {cmd}".format(id=id,cmd=cmd))
                        cmd = "chmod 777 /tempScanDocker/scan_{name}.sh".format(name=name)
                        tLinux.sendRootCommand("docker exec -u 0 {id} {cmd}".format(id=id,cmd=cmd))
                        # 执行"后台执行脚本"
                        cmd = "/usr/bin/sh /tempScanDocker/scan_{name}.sh 1>&2".format(name=name)
                        tLinux.sendRootCommand("docker exec -u 0 {id} {cmd}".format(id=id,cmd=cmd),timeout=120)
                    except:
                        g_Log.writeLog("traceback")
            tLinux.logout()
        except:
            g_Log.writeLog("traceback")

    reportPath = g_caseName.replace("TestCase","Report").replace(".py","")+"-"+g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")
    shutil.copy(g_curDir+"/scanSensitivePolicy.xlsx",reportPath+"/scanSensitivePolicy.xlsx")
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
            tDocker.logout()
            tLinux = LinuxOperate.Linux(ip=vmIP,name=vmName,user=vmUser,password=vmUserPasswd,suRoot=vmSuRoot,rootPassword=vmRootPasswd)
            totalTime = 3600 # 一台虚机最多允许执行1小时
            leftTime = 1800 # 一台虚机理论上最长执行0.5小时
            performanceKey = False #虚机性能标记，如果性能差，则会适当延长执行0.5小时。
            while True:
                g_Log.writeLog("waiting 30 seconds...")
                time.sleep(30)
                leftTime = leftTime - 30
                endScan = True
                leftScanNum = 0
                for container in containerInfo:
                    image = container[0].split("/")[-1].split(":")[0]
                    id = container[1]
                    mntDir = container[2]
                    output = tLinux.sendRootCommand("docker ps |grep {id}".format(id=id))
                    if output==False or output[0]=="":
                        continue

                    cmd = "ls -l {dir}/tempScanDocker".format(dir=mntDir)
                    output = tLinux.sendRootCommand(cmd,timeout=5)
                    if output != False and "No such file or directory" in output[1]:
                        g_Log.writeLog(u"错误信息：Docker容器{image}内没有扫描脚本，可能是新增启动或重新启动的容器，请重新扫描该容器".format(image=image))
                        continue
                    downloadFile = []
                    for scan in g_scanPolicy:
                        try:
                            name = scan[1]
                            ifRed = scan[7]
                            endStat = False
                            # 检查脚本是否有end scanning标记
                            cmd = "tail -n 2 {dir}/tempScanDocker/{name}.txt".format(dir=mntDir,name=name)
                            output = tLinux.sendRootCommand(cmd,timeout=5)
                            if output != False and "No such file or directory" in output[1]:
                                g_Log.writeLog(u"错误信息：Docker容器{image}内因为某些原因没有启动扫描策略{sh}，或是扫描结果被人为误删，请重新扫描该容器".format(image=image,sh=name))
                                continue
                            if output != False and "note:end scanning" in output[0]:
                                if name in downloadFile:
                                    continue
                                downloadResult(reportPath,image,mntDir,name,tLinux,vmIP,ifRed)
                                downloadFile.append(name)
                                endStat = True
                            if endStat == False:
                                leftScanNum = leftScanNum + 1
                                endScan = False
                        except:
                            g_Log.writeLog("traceback")

                if (totalTime == 0 and leftTime<0) or performanceKey == True:  ## 最多再允许执行时间为0，退出执行
                    break
                if leftScanNum>0 and leftTime<0 and totalTime!=0 : ## 在第一个0.5小时扫描结束时，如果存在扫描脚本任务没有完成，则理论执行时间再增加0.5小时
                    leftTime = 1800    # 理论执行时间再增加0.5小时
                    totalTime = 0   # 同时最多再允许执行的时间置为0
                if leftScanNum>0 and leftTime<0 and totalTime==0 and performanceKey == False: ## 如果存在多个扫描脚本任务没有完成，可能是环境性能差，则理论执行时间再增加0.5小时
                    leftTime = 1800    # 理论执行时间再增加0.5小时
                    performanceKey = True  #虚机性能标记为True，后续不再延长执行时间
                if endScan == True or leftTime<0: ## 所有执行结果中都出现了end标记，或者理论执行时间为0，退出执行
                    break
            tLinux.logout()
        except:
            g_Log.writeLog("traceback")


def downloadResult(reportPath,image,mntDir,name,tLinux,vmIP,ifRed):
    try:
        output = tLinux.sendRootCommand("cat {dir}/tempScanDocker/{name}.txt".format(dir=mntDir,name=name),timeout=30)
        if output == False or "Operation timed out" in output[1]:
            output = tLinux.sendRootCommand("cat {dir}/tempScanDocker/{name}.txt".format(dir=mntDir,name=name),timeout=30)
        elif len(output[0].strip())==0:
            return False

        if output == False or "Operation timed out" in output[1]:
            output = ["Result download error! please scan {name} by hand.".format(name=name),""]

        result = output[0]
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
            excel = ExcelOperate.Excel(excelName=scanPolicyExcel,sheetName=name)
            ignoreKeys = excel.read()
            if ignoreKeys == False:
                ignoreKeys = []
            else:
                del ignoreKeys[0]
            pythonRegular = ""
            for x in ignoreKeys:
                if x[1].lower() == "python":
                    pythonRegular = pythonRegular + x[0] + "|"
            if pythonRegular == "": # 没有配置python形式的结果排查，扫描结果直接写入结果文件
                raise "no python values"
            pythonRegular = pythonRegular[:-1]

            lines = result.split("\n")
            for line in lines:  # 配置了python形式的结果排查，扫描结果筛选后写入结果文件
                if len(line) > 70000:
                        continue
                if len(line) > 10000:
                    f1.write(line+"\n")
                    continue
                x0 = re.findall(pythonRegular,line)
                if x0==[]:
                    f1.write(line+"\n")
        except:
            errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
            if "no python values" in errmsg:
                g_Log.writeLog(u"没有为{name}配置python形式的结果排查，扫描结果直接写入结果文件".format(name=name))
            else:
                g_Log.writeLog(errmsg)
            lines = result.split("\n")
            for line in lines:  # 配置了python形式的结果排查，扫描结果筛选后写入结果文件
                if len(line) > 70000:
                    continue
                f1.write(line+"\n")
        f1.close()
        tLinux.sendRootCommand("rm -rf {dir}/tempScanDocker/{name}.txt".format(dir=mntDir,name=name),timeout=5)
        #tLinux.sendRootCommand("rm -rf {dir}/tempScanDocker/{name}.txt".format(dir=mntDir,name=name),timeout=5)
    except:
        g_Log.writeLog("traceback")
    return True


def clean_all():
    for vm in g_vmInfo:
        try:
            vmIP = vm[0]
            vmName = vm[1]
            vmUser = vm[2]
            vmUserPasswd = vm[3]
            vmSuRoot = vm[4]
            vmRootPasswd = vm[5]
            tLinux = LinuxOperate.Linux(ip=vmIP,name=vmName,user=vmUser,password=vmUserPasswd,suRoot=vmSuRoot,rootPassword=vmRootPasswd)
            output = tLinux.sendRootCommand("find / -name tempScanDocker")
            for dir in output[0].split("\n"):
                tLinux.sendRootCommand("rm -rf {dir}".format(dir=dir))
            for dir in output[0].split("\n"):
                tLinux.sendRootCommand("rm -rf {dir}".format(dir=dir))
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
        clean_all()
    except:
        g_Log.writeLog("traceback")
        return 0
    return 1

# 执行用例
def run():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
        getScanPolicy()
        scan_in_MV()
    except:
        g_Log.writeLog("traceback")
        return 0
    return 1

# 执行后清理环境
def clearup():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
        clean_all()
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

