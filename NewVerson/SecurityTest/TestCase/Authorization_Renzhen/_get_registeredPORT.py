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
""" 脚本配置执行说明 """
该脚本不是单独的用例，仅用于获取环境中注册到nginx的API接口。
'''

'''
""" 可以在此处下方添加自己的代码（函数） """
'''
try:
    g_Log = None
    g_Global = None
    g_caseName = None
    g_registeredAPIExcel = None

    curFile = os.path.abspath(sys._getframe(0).f_code.co_filename)
    g_caseName = curFile.replace("\\","/")
    g_curDir = os.path.split(g_caseName)[0]
    path.append( g_caseName.split("TestCase")[0]+"PublicLib" )

    startTime = None
    tempConfig = g_curDir+"/_tempConfig.ini"
    pathExist = os.path.exists(tempConfig)
    if pathExist:
        file = open(tempConfig)
        info = file.readlines()
        for line in info:
            if "startTime" in line:
                startTime = line.split("startTime:")[1].strip()
    if startTime == None:
        startTime = str(datetime.datetime.now())
    import GlobalValue as g_Global
    g_Global.init()
    g_Global.setValue("startTime",startTime)

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

    g_allPorts = []
    for api in g_codeAPI:
        port = str(api[2]).strip().split(".")[0]
        ports = port.split(";")
        for p in ports:
            if p not in g_allPorts:
                g_allPorts.append(p)
except:
    errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
    print errmsg
    exit(0)

def get_vmRealIP(linux):  # 根据虚机挂载的大网IP获取实际eth0信息
    try:
        output = linux.sendRootCommand("/usr/sbin/ifconfig eth0")
        readIP = re.findall("inet\s+(\d+\.\d+\.\d+\.\d+)",output[0])
        return readIP[0]
    except:
        errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
        g_Log.writeLog(errmsg)
        return ""

def get_externalPortBySVC(): # 通过kubectl get svc --all-namespaces命令获取虚机上启动的external端口及容器端口，格式:[[serviceName,port]]
    externalPorts = []
    if g_omCoreInfo == []:
        return externalPorts
    for conf in g_config:
        if conf[0]=="KUBERNETES_MASTER":
            kubernetes_master = conf[1]
    if kubernetes_master == None:
        return externalPorts
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
            if svc.strip() == "" or "NAMESPACE" in svc:
                continue
            res = svc.split()
            namespace = res[0]
            serName = res[1]
            command = "export KUBERNETES_MASTER={kubernetes_master};export PAAS_CRYPTO_PATH=/var/paas/srv/kubernetes;/var/paas/kubernetes/kubectl --client-certificate=${key1}/server.cer --client-key=${key1}/server_key.pem --certificate-authority=${key1}/ca.cer -s ${key2} describe svc {serice} -n {namespace} |egrep \"IP:|Name:|Namespace:|Type:|External IPs:|LoadBalancer Ingress:|Port:|NodePort:|Endpoints:\"".format(kubernetes_master=kubernetes_master,key1="{PAAS_CRYPTO_PATH}",key2="{KUBERNETES_MASTER}",namespace=namespace,serice=serName)
            output = ssh.sendRootCommand(command)
            x = re.findall("Name:\s*(.*?)\s*\n",output[0])
            name = x[0]
            t1_port1 = re.findall("\W+Port:\s+[a-zA-Z0-9\<\>\s\-]+\s+(\d+)/\w+\s*\n\s*Endpoints:\s*([0-9:,\.]+)",output[0])
            t1_port2 = re.findall("\W+Port:\s+[a-zA-Z0-9\<\>\s\-]+\s+(\d+)/\w+\s*\n\s*NodePort:\s+[a-zA-Z0-9\s\-]+\s+\d+/\w+\s*\n\s*Endpoints:\s+([0-9:,\.]+)",output[0])
            t1_ports = t1_port1+t1_port2
            t1_ip = re.findall("IP:\s*(\d+\.\d+\.\d+\.\d+)",output[0])
            t1_externalip = re.findall("External IPs:\s*(\d+\.\d+\.\d+\.\d+)",output[0])
            t1_ingress = re.findall("LoadBalancer Ingress:\s*(\d+\.\d+\.\d+\.\d+)",output[0])
            #t1_nodeport = re.findall("NodePort:.*\s+(\d+)/\w+",output[0])
            t1_nodeport = re.findall("\W*NodePort:\s+[a-zA-Z0-9\s\-]+\s+(\d+)/\w+\s*\n\s*Endpoints:\s*([0-9:,\.]+)",output[0])

            ifFind = False
            if t1_ports != [] and t1_ip != []:
                for p in t1_ports:
                    endPoints = p[1]
                    externalPort = t1_ip[0]+":"+p[0]
                    externalPorts.append([name,externalPort,endPoints])
                ifFind = True
            if t1_ports != [] and t1_externalip != []:
                for p in t1_ports:
                    endPoints = p[1]
                    externalPort = t1_externalip[0]+":"+p[0]
                    externalPorts.append([name,externalPort,endPoints])
                ifFind = True
            if t1_ports != [] and t1_ingress != []:
                for p in t1_ports:
                    endPoints = p[1]
                    externalPort = t1_ingress[0]+":"+p[0]
                    externalPorts.append([name,externalPort,endPoints])
                ifFind = True
            if t1_nodeport != []:
                tmpcmd = "export KUBERNETES_MASTER={kubernetes_master};export PAAS_CRYPTO_PATH=/var/paas/srv/kubernetes;/var/paas/kubernetes/kubectl --client-certificate=${key1}/server.cer --client-key=${key1}/server_key.pem --certificate-authority=${key1}/ca.cer -s ${key2} get pods -n {namespace} |grep {serice}".format(kubernetes_master=kubernetes_master,key1="{PAAS_CRYPTO_PATH}",key2="{KUBERNETES_MASTER}",namespace=namespace,serice=serName)
                tmpout = ssh.sendRootCommand(tmpcmd)
                pods = re.findall("({serice}.*?)\s".format(serice=serName),tmpout[0])
                for pod in pods:
                    try:
                        tmpcmd1 = "export KUBERNETES_MASTER={kubernetes_master};export PAAS_CRYPTO_PATH=/var/paas/srv/kubernetes;/var/paas/kubernetes/kubectl --client-certificate=${key1}/server.cer --client-key=${key1}/server_key.pem --certificate-authority=${key1}/ca.cer -s ${key2} get pods {pod} -n {namespace} -o yaml |grep hostIP".format(kubernetes_master=kubernetes_master,key1="{PAAS_CRYPTO_PATH}",key2="{KUBERNETES_MASTER}",namespace=namespace,pod=pod)
                        tmpout1 = ssh.sendRootCommand(tmpcmd1)
                        tempx = re.findall("hostIP:\s*(\d+\.\d+\.\d+\.\d+)",tmpout1[0])
                        hostIP = tempx[0]
                        for p in t1_nodeport:
                            endPoints = p[1]
                            externalPort = hostIP+":"+p[0]
                            externalPorts.append([name,externalPort,endPoints])
                    except:
                        errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
                        g_Log.writeLog(errmsg)
                ifFind = True
            if ifFind == False:
                g_Log.writeLog("以下服务的端口自动化判断为不涉及认证（api注册信息中不包含这些端口），无需测试：\n"+output[0])
                continue
        except:
            errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
            g_Log.writeLog(errmsg)
    return externalPorts

def get_netstatPort(): # 通过netstat -tunlp命令获取虚机上监听的相关端口，格式:[[ip,port]]
    netstatPorts = []
    for vm in g_vmInfo:
        try:
            vmIP = vm[0]
            vmUser = vm[2]
            vmUserPasswd = vm[3]
            vmSuRoot = vm[4]
            vmRootPasswd = vm[5]
            tLinux = LinuxOperate.Linux(ip=vmIP,user=vmUser,password=vmUserPasswd,suRoot=vmSuRoot,rootPassword=vmRootPasswd)
            realIP = get_vmRealIP(tLinux)

            scanPort = "|".join(g_allPorts)
            scanPort = scanPort.replace("|"," |:")
            scanPort = ":"+scanPort+" "
            output = tLinux.sendRootCommand("/usr/bin/netstat -tunlp |egrep \"{port}\"".format(port=scanPort))
            vmPorts = re.findall("\d+\.\d+\.\d+\.\d+:\d+|:::\d+",output[0])
            rvmPorts = []
            for p in vmPorts:
                if "127.0.0.1" in p:
                    continue
                if "0.0.0.0:" in p:
                    rvmPorts.append([vmIP,realIP+":"+p.split(":")[1]])
                elif ":::" in p:
                    rvmPorts.append([vmIP,realIP+":"+p.split(":")[1]])
                else:
                    rvmPorts.append([vmIP,p])
            netstatPorts = netstatPorts+rvmPorts
        except:
            g_Log.writeLog("traceback")
    return netstatPorts

def get_allExternalPort(): #获取虚机上所有启动的external IP和端口，格式:[[ip,port]]
    allExternalPort = []
    #externalPortBySVC = get_externalPortBySVC()
    #allExternalPort = allExternalPort + externalPortBySVC
    netstatPort = get_netstatPort()
    allExternalPort = allExternalPort + netstatPort

    return allExternalPort

'''
""" 以下定义的函数，请在特定位置添加自己的代码 """
'''
# 执行前的准备操作
def prepare():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
    except:
        errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
        g_Log.writeLog(errmsg)
        return 0
    return 1

# 执行用例
def run():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
        curDir = os.path.split(g_caseName)[0]
        resultDir = curDir.replace("TestCase","Report")
        startTimeSign = g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")
        #startTimeSign = "20180228145712.735000"
        externalPortExcelName=resultDir+"/externalPorts-{startTime}.xls".format(startTime=startTimeSign)

        externalPort = get_allExternalPort()  # 输出格式：[LinuxIP,dir,urlNo,location_url,serverName,"ip_port,ip_port"]
        print externalPort
        externalPortExcel = ExcelOperate.Excel(excelName=externalPortExcelName,sheetID=0)
        externalPortExcel.new()
        externalPortExcel.write([[u"端口所在服务或虚机",u"端口"]])
        externalPortExcel.write(externalPort)

        global g_externalPortExcel
        g_externalPortExcel = externalPortExcelName
    except:
        errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
        g_Log.writeLog(errmsg)
        return 0
    return 1

# 执行后清理环境
def clearup():
    try:
        ''''''''' 可以在此处下方添加自己的代码 '''''''''
        curDir = os.path.split(g_caseName)[0]
        tempConfig=curDir+"/_tempConfig.ini"
        file = open( tempConfig,'a' )
        file.write("externalPortExcel:"+g_externalPortExcel+"\n")
        file.close()
    except:
        errmsg = ''.join(traceback.format_exception(*sys.exc_info()))
        g_Log.writeLog(errmsg)
        return 0
    return 1


res = prepare()
if not res:
    print "执行用例prepare模块失败，结束用例{name}的执行".format(name=g_caseName)
else:
    run()
    clearup()

