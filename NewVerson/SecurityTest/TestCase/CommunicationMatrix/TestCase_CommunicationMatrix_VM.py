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
《01 产品网络安全红线落地解读及指导V2_1.xls》 3.1.1 系统所有的对外通信连接必须是系统运行和维护必需的，对使用到的通信端口在产品通信矩阵文档中说明，动态侦听端口必须限定确定的合理的范围。通过端口扫描工具验证，未在通信矩阵中列出的端口必须关闭。
'''
'''
""" 脚本功能 """
扫描环境中的端口信息（包含netstat -tunlp和kubectl describe svc --all-namespaces的查询结果），与通信矩阵的内容对比，查看是否有多余或缺失的端口。
'''
'''
""" 脚本配置执行说明 """
配置1：/SecurityTest/Config/config.xlsx，“vmInfo”页
配置2：本脚本所在目录下的CommunicationMatrix_VM.xlsx，“VM”页。每一列配置表头都有批注说明，请仔细阅读。
配置3：本脚本所在目录下的CommunicationMatrix_VM.xlsx，“config”页。每一行配置说明，请仔细阅读。
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

    communicationMatrixExcel = g_curDir + "/CommunicationMatrix_VM.xlsx"
    excel1 = ExcelOperate.Excel(excelName=communicationMatrixExcel,sheetName="VM")
    g_matrixInfo = excel1.read()
    del g_matrixInfo[0]
    excel2 = ExcelOperate.Excel(excelName=communicationMatrixExcel,sheetName="config")
    g_config = excel2.read()
    del g_config[0]

    g_ResultFile = g_caseName.replace("TestCase","Report").replace(".py","")+"-"+g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")+".xls"
except:
    errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
    print errmsg
    exit(0)

def getNetstatInfo(): ## 遍历每一台虚机，netstat -tunlp命令查询所有监听端口及其对应的进程
    #netstatInfo格式：[[vmIP,cmd,port,portIP,protocol,proc]]
    netstatInfo = []
    for vm in g_vmInfo:
        try:
            vmIP = vm[0]
            vmName = vm[1]
            vmUser = vm[2]
            vmUserPasswd = vm[3]
            vmSuRoot = vm[4]
            vmRootPasswd = vm[5]
            tLinux = LinuxOperate.Linux(ip=vmIP,name=vmName,user=vmUser,password=vmUserPasswd,suRoot=vmSuRoot,rootPassword=vmRootPasswd)
            output = tLinux.sendRootCommand("netstat -tunlp")
            netInfo = output[0].split("\n")

            for net in netInfo:
                if net[:3]!="tcp" and net[:3]!="udp":
                    continue
                temp = net.split()

                ip_port = temp[3]
                x = re.findall("\d+",ip_port)
                port = x[-1]
                ptip = ip_port[:len(ip_port)-len(port)-1]

                protocol = temp[0]
                x = re.findall("\d+/.*",net)
                if "/" in temp[-1]:
                    pid = temp[-1].split("/")[0]
                elif x != []:
                    pid = x[0].split("/")[0]
                else:
                    pid = "00000"

                if pid == "00000":
                    netstatInfo.append([vmIP,"netstat -tunlp",port,ptip,protocol,"The process does not exist!"])
                    continue
                output = tLinux.sendRootCommand("ps -ef |egrep \"^\w+\s+{pid} \" |egrep -v \"grep|\s\[\"".format(pid=pid) )
                procs = output[0].split("\n")
                proc = ""
                for p in procs:
                    if p.split()[1] == pid:
                        proc = p
                        break
                netstatInfo.append([vmIP,"netstat -tunlp",port,ptip,protocol,proc])
        except:
            g_Log.writeLog("traceback")

    return netstatInfo

def getNamespacesInfo(): ## OM管理节点上查询业务端口及其实例名称
    #namespacesInfo格式：[[vmIP,cmd,port,portIP,protocol,serName]]
    namespacesInfo = []
    omCoreIP = g_omCoreInfo[0]
    omCoreUser = g_omCoreInfo[2]
    omCoreUserPasswd = g_omCoreInfo[3]
    omCoreSuRoot = g_omCoreInfo[4]
    omCoreRootPasswd = g_omCoreInfo[5]
    ssh = LinuxOperate.Linux(ip=omCoreIP,user=omCoreUser,password=omCoreUserPasswd,suRoot=omCoreSuRoot,rootPassword=omCoreRootPasswd)
    command = "ps -ef | grep /usr/local/bin/kubelet | grep -v grep | awk -F \"api-servers=\" '{print $2}' | awk '{print $1}'"
    output = ssh.sendCommand(command)
    kubernetes_master = output[0].strip()
    command = "export KUBERNETES_MASTER={kubernetes_master};export PAAS_CRYPTO_PATH=/var/paas/srv/kubernetes;/var/paas/kubernetes/kubectl --client-certificate=${key1}/server.cer --client-key=${key1}/server_key.pem --certificate-authority=${key1}/ca.cer -s ${key2} get svc --all-namespaces".format(kubernetes_master=kubernetes_master,key1="{PAAS_CRYPTO_PATH}",key2="{KUBERNETES_MASTER}")
    output = ssh.sendRootCommand(command)
    svcInfo = output[0].split("\n")
    for svc in svcInfo:
        try:
            if svc.strip() == "":
                continue
            res = svc.split()
            namespace = res[0]
            serName = res[1]
            command = "export KUBERNETES_MASTER={kubernetes_master};export PAAS_CRYPTO_PATH=/var/paas/srv/kubernetes;/var/paas/kubernetes/kubectl --client-certificate=${key1}/server.cer --client-key=${key1}/server_key.pem --certificate-authority=${key1}/ca.cer -s ${key2} describe svc {serice} -n {namespace} |egrep \"IP:|Name:|Namespace:|Type:|External IPs:|LoadBalancer Ingress:|Port:|NodePort:\"".format(kubernetes_master=kubernetes_master,key1="{PAAS_CRYPTO_PATH}",key2="{KUBERNETES_MASTER}",namespace=namespace,serice=serName)
            output = ssh.sendRootCommand(command)
            cmd = "kubectl describe svc {serice} -n {namespace}".format(namespace=namespace,serice=serName)
            portInfo = output[0]
            check1 = re.findall("Type:\s+([0-9a-zA-Z_\-]+)",portInfo)
            if check1 == []:
                g_Log.writeLog(u"错误信息：{cmd}没有查询到业务\"Type\"信息".format(cmd=cmd))
            elif check1[0] != "ClusterIP":
                x10 = re.findall("\d+/[A-Z]+",portInfo)
                if x10 == []:
                    g_Log.writeLog(u"错误信息：{cmd}没有查询到业务端口信息".format(cmd=cmd))
                    continue
                for pInfo in x10:
                    port = pInfo.split("/")[0]
                    protocol = pInfo.split("/")[1]
                    namespacesInfo.append([omCoreIP,cmd,port,"externalIP",protocol,serName])
                continue
            check2 = re.findall("NodePort:\s+[0-9a-zA-Z_\-]+\s+(\d+/[A-Z]+)",portInfo)
            if check2 != []:
                for pInfo in check2:
                    port = pInfo.split("/")[0]
                    protocol = pInfo.split("/")[1]
                    namespacesInfo.append([omCoreIP,cmd,port,u"略",protocol,serName])
        except:
            g_Log.writeLog("traceback")

    return namespacesInfo

def getPortInfo(): ## 查询环境中的各种监听端口，格式：[[vmIP,cmd,port,portIP,protocol,proc]]
    portInfo = []
    if g_omCoreInfo!=[]:
        omCoreIP = g_omCoreInfo[0]
        omCoreUser = g_omCoreInfo[2]
        omCoreUserPasswd = g_omCoreInfo[3]
        omCoreSuRoot = g_omCoreInfo[4]
        omCoreRootPasswd = g_omCoreInfo[5]
        ssh = LinuxOperate.Linux(ip=omCoreIP,user=omCoreUser,password=omCoreUserPasswd,suRoot=omCoreSuRoot,rootPassword=omCoreRootPasswd)
        output = ssh.sendRootCommand("ls -l /var/paas/kubernetes/kubectl")
        res = output[0]
        if "/var/paas/kubernetes/kubectl" in res:
            portInfo = portInfo + getNamespacesInfo()

    portInfo = portInfo + getNetstatInfo()
    #portInfo = list(set(portInfo))
    return portInfo

def checkMonitorPort(monitorPort,matrixPort,vmPorts,monitorProc,description):
    result = False
    matrixPort = str(matrixPort).split(".")[0] #防止在通信矩阵中获取到的是float型

    pts1 = matrixPort.split(",")
    if monitorPort in pts1:
        result = True

    pts2 = matrixPort.split("/")
    if monitorPort in pts2:
        result = True

    pts3 = re.findall('\d+-\d+',matrixPort)
    for p in pts3:
        tmp = p.split("-")
        netPort_int = int(monitorPort)
        pf_int = int(tmp[0])
        pe_int = int(tmp[1])
        if "/bin/kube-proxy" in monitorProc:
            if "kube-proxy" in description: #对"kube-proxy"监听端口的特殊处理（该端口在通信矩阵中1024~65535，描述太广）
                if netPort_int > pf_int and netPort_int < pe_int and netPort_int not in vmPorts:
                    result = True
        else:
            if "kube-proxy" not in description:
                if netPort_int > pf_int and netPort_int < pe_int and netPort_int not in vmPorts:
                    result = True

    pts4 = re.findall('\d+~\d+',matrixPort)
    for p in pts4:
        tmp = p.split("~")
        netPort_int = int(monitorPort)
        pf_int = int(tmp[0])
        pe_int = int(tmp[1])
        if "/bin/kube-proxy" in monitorProc:
            if "kube-proxy" in description: #对"kube-proxy"监听端口的特殊处理（该端口在通信矩阵中1024~65535，描述太广）
                if netPort_int > pf_int and netPort_int < pe_int and netPort_int not in vmPorts:
                    result = True
        else:
            if "kube-proxy" not in description:
                if netPort_int > pf_int and netPort_int < pe_int and netPort_int not in vmPorts:
                    result = True

    return result

def check_Ports_in_CommunicationMatrix(vmPorts):
    errInfo = []
    for vmPt in vmPorts:  ## 查询环境中的各种监听端口，格式：[[vmIP,cmd,port,portIP,protocol,proc]]
        vmIP = vmPt[0]
        command = vmPt[1]
        monitorPort = vmPt[2]
        monitorIP = vmPt[3]
        monitorProtocol = vmPt[4]
        monitorProc = vmPt[5]
        #x = re.findall("/usr/sbin/ntpd|/usr/sbin/sshd",monitorProc)
        #if x != []:
        #    continue

        checkPortResult = False
        checkIpResult = False
        checkProtocolResult = False
        checkServiceResult = False
        for matrix in g_matrixInfo:
            destPort = str(matrix[1])
            destIP = str(matrix[0])
            protocol = str(matrix[2])
            service = str(matrix[4])
            destPort = destPort.replace("、","/").replace(" ","/").replace("～","~")

            checkPort = checkMonitorPort(monitorPort,destPort,vmPorts,monitorProc,destIP+service)
            if checkPort == False:
                continue
            else:
                checkPortResult = True

            if "127.0.0.1" in destIP and "127.0.0.1" == monitorIP:
                checkIpResult = True
            elif "0.0.0.0" in destIP and "0.0.0.0" == monitorIP:
                checkIpResult = True
            elif "ipv6" in destIP.lower() and "::" == monitorIP:
                checkIpResult = True

            if "tcp" in monitorProtocol.lower() and "tcp" in protocol.lower():
                checkProtocolResult = True
            elif "udp" in monitorProtocol.lower() and "udp" in protocol.lower():
                checkProtocolResult = True
            elif monitorProtocol.lower() == protocol.lower():
                checkProtocolResult = True

            if service.lower() in monitorProc.lower():
                checkServiceResult = True

        err = ""
        errLevel = "Pass"
        if checkPortResult == False:
            errLevel = "Fail"
            err = u"通信矩阵中没有找到该端口"
        else:
            if checkIpResult == False:
                err = err + u"通信矩阵中\"目的IP\"的描述与环境实际端口监听的IP可能不匹配，请人工观察对比\n"
            if checkProtocolResult == False:
                err = err + u"通信矩阵中\"协议\"的描述与环境实际端口协议可能不匹配，请人工观察对比\n"
            if checkServiceResult == False:
                err = err + u"通信矩阵中\"所属微服务\"的描述与环境实际端口所在服务可能不匹配，请人工观察对比\n"
            err = err.strip()
            if err != "":
                errLevel = "Warn"

        errInfo.append([vmIP,command,monitorPort,monitorIP,monitorProtocol,monitorProc,errLevel,err])
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
        portInfo = getPortInfo()
        result = check_Ports_in_CommunicationMatrix(portInfo) #[vmIP,command,monitorPort,monitorIP,monitorProtocol,monitorProc,errLevel,err]
        excelResult = ExcelOperate.Excel(excelName=g_ResultFile,sheetID=0)
        excelResult.new()
        excelResult.write([[u"端口所在节点",u"查询命令",u"端口",u"监听IP",u"协议",u"进程或实例信息",u"问题级别",u"问题描述"]],redLine=2)
        excelResult.write(result)
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

