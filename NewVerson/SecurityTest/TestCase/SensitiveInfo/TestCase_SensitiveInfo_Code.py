#-*- coding: utf-8 -*-

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
《01 产品网络安全红线落地解读及指导V2_1.xls》 7.1.4 用于敏感数据传输加密的密钥，不能硬编码在代码中。
《中央软件院网络安全测试基线V2.0.xlsx》 中关于代码中无用账号、敏感信息、明文密码、加密算法、解释性语言、命令注入、危险函数等要求
'''
'''
""" 脚本功能 """
扫描源码中的无用账号、敏感信息、明文密码、加密算法、解释性语言、命令注入、危险函数等问题点，扫描策略见本脚本所在目录下的scanSensitivePolicy.xlsx
'''
'''
""" 脚本配置执行说明 """
配置1：本脚本所在目录下的scanSensitivePolicy.xlsx，“policy”页。
配置2：本脚本所在目录下的scanSensitivePolicy.xlsx，“config”页。每一行配置都有说明，请仔细阅读。
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
    scanSensitivePolicyExcel = g_curDir + "/scanSensitivePolicy.xlsx"
    excel1 = ExcelOperate.Excel(excelName=scanSensitivePolicyExcel,sheetName="policy")
    g_scanPolicy = excel1.read()
    del g_scanPolicy[0]
    excel2 = ExcelOperate.Excel(excelName=scanSensitivePolicyExcel,sheetName="config")
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
        if p[0].lower() == "true" and "code" in supportSys.lower():
            policy.append(p)
    g_scanPolicy = policy
    return 1

def unzipFiles(scanDir): ##解压目录下可能含有的zip源码包
    for dirpath,dirnames,filenames in os.walk(scanDir):
        for zip in filenames:
            try:
                if ".zip" not in zip:
                    continue
                tmpfile = os.path.join(dirpath,zip).replace("\\","/")
                os.mkdir(tmpfile+"-bak")
                f = zipfile.ZipFile(tmpfile)
                f.extractall(tmpfile+"-bak")
                f.close()
                os.remove(tmpfile)
                shutil.copytree(tmpfile+"-bak",tmpfile)
                shutil.rmtree(tmpfile+"-bak")
            except:
                g_Log.writeLog("traceback")
                if os.path.isdir(tmpfile+"-bak"):
                    shutil.rmtree(tmpfile+"-bak")
    return 1

def scanFile(resultPath,filename,subDir): ## 按扫描策略在文件中扫描关键字
    reportPath = resultPath
    try:
        f = open(filename,'r')
    except:
        g_Log.writeLog("traceback")
        return 0

    shutil.copy(g_curDir+"/scanSensitivePolicy.xlsx",reportPath+"/scanSensitivePolicy.xlsx")
    for (num,line) in enumerate(f):
        #resultPath = runPath+"/result-"+beginTime+"/"+codeZip
        attrDir = os.path.split(subDir)[1]
        x0 = re.findall("/tiny/tiny|\.css|/webapp/.*\.js$|\.min\.js",filename,re.I)
        if len(line)>5000 and x0!=[]:
            continue

        try:
            for conf in g_scanPolicy:
                suffix = conf[3].replace(";","|").replace(".","\.").replace(" ","").strip()
                ifRed = conf[7]
                while True:
                    if suffix[0:1]=="|":
                        suffix = suffix[1:]
                    elif suffix[-1:]=="|":
                        suffix = suffix[:-1]
                    elif "||" in suffix:
                        suffix = suffix.replace("||","|")
                    else:
                        break
                suffix = suffix.replace("|","$|")+"$"

                fName = filename.split("/")[-1]
                x1 = re.findall(suffix,fName,re.I)
                if suffix!="":
                    if x1==[]:
                        continue
                if ifRed.upper() == "YES":
                    resultPath = reportPath+"/(RedLine)"+str(attrDir)
                else:
                    resultPath = reportPath+"/"+str(attrDir)
                resultFile = resultPath + "/" + str(conf[1]) + ".txt"
                line = line.replace("\r","").replace("\n","")
                x2 = re.findall(conf[2],line,re.I)
                if x2 == []:
                    continue
                if not os.path.exists(resultPath):
                    os.makedirs(resultPath)
                f_result = open(resultFile,'a')
                if conf[1] == "FIND_TLS_CONFIG":
                    f_result.write("###############################################################################"+"\n")
                    f1 = open(filename,'r')
                    for (num1,line1) in enumerate(f1):
                        if num1>=num and num1<num+6:
                            line1 = line1.strip()
                            f_result.write(str(filename.replace(g_codeDir,""))+":"+str(num1)+":"+str(line1)+"\n")
                    f1.close()
                    f_result.write("\n")
                else:
                    f_result.write(str(filename.replace(g_codeDir,""))+":"+str(num)+":"+str(line)+"\n")
                f_result.close()
        except:
            g_Log.writeLog("traceback")
    f.close()

    return True

def scanCodeSafe(): ##扫描主函数
    reportPath = g_caseName.replace("TestCase","Report").replace(".py","")+"-"+g_Global.getValue("startTime").replace(":","").replace(" ","").replace("-","")
    if not os.path.exists(reportPath):
        os.makedirs(reportPath)
    global g_codeDir
    getScanPolicy()
    for conf in g_config:
        if conf[0]=="codeDir":
            g_codeDir = conf[1]
    codeDir = g_codeDir
    if g_codeDir=="":
        g_Log.writeLog(u"错误信息：没有配置源码路径")
        return 0
    if g_scanPolicy==[]:
        g_Log.writeLog(u"错误信息：没有配置扫描策略")
        return 0

    unzipFiles(codeDir)
    for dir in os.listdir(codeDir):
        subDir = os.path.join(codeDir,dir).replace("\\","/")
        if not os.path.isdir(subDir):
            g_Log.writeLog(u"错误信息：{file}不是一个目录，不支持扫描".format(file=subDir))
            continue
        g_Log.writeLog(u"开始扫描 {dir}".format(dir=subDir))
        for dirpath,dirnames,filenames in os.walk(subDir):
            for filename in filenames:
                tmpfile = os.path.join(dirpath,filename).replace("\\","/")
                scanFile(reportPath,tmpfile,subDir)

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
        scanCodeSafe()
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

