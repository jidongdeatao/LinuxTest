#-*- coding: GBK -*-
import sys
import os
import re
import csv
import string
import time


class fileToolDef:
    resultPath = ""
    txtPath = ""

def set_txtPath(path):
    fileToolDef.txtPath = path
def get_txtPath():
    return fileToolDef.txtPath
def set_resultPath(path):
    fileToolDef.resultPath = path
def get_resultPath():
    return fileToolDef.resultPath

def getAllTxt():
    txtPath = get_txtPath()
    all_txtFile = []
    for parent, dirnames, filenames in os.walk(txtPath):
        for name in filenames:
            if name[-4:] == ".txt" : # and name[:3]=="VM_"
                parent = parent.replace("\\","/")
                if dirnames == []:
                    all_txtFile.append(parent + "/" + name)
                if dirnames != []:
                    dirname = dirnames[0].replace("\\","/")
                    all_txtFile.append(parent + "/" +dirname + "/" +name)
    return all_txtFile


def resultFile(txtFile):
    txtPath = get_txtPath()
    csvPath = txtPath.replace("/result", "/csvResult")
    return csvPath

def readBigFile(txtFile):
    size = os.path.getsize(txtFile)
    allfile = ""
    if size < 30000000:
        oldFile = open(txtFile,'rb')
        data = oldFile.read()
        allfile = allfile + data
        oldFile.close()
        return allfile
    
    i = 0
    with open(txtFile,'rb') as oldFile:
        while True:
            data = oldFile.read(30000000)
            allfile = allfile + data
            i = i+1
            if data == "":
                break
            if i > size/30000000 +1:
                break
    oldFile.close()
    return allfile

def txtFormat(txtFile):
    result = []
    reader = readBigFile(txtFile)
    reader = reader.split('\n')
    '''
    isFileRead = True
    for r in reader:
        r = r.replace("\r","").replace("\n","").strip()
        if r=='':
            continue
        if not re.match('.*(:\d+:).*',r):
            isFileRead = False
    '''
    x0 = re.findall('VM_Bash-X|VM_JSX_Language|VM_Password|VM_Sensitive|VM_unsafe_encrypt',txtFile)
    x1 = re.findall('VM_SensitiveInPross',txtFile)
    if x0!=[] and x1==[]: # or isFileRead==True
        result.append(["文件名称","行号","内容"])
        for r in reader:
            r = r.replace("\r","").replace("\n","").strip()
            temp = re.findall('^\d+:/',r)
            if temp != []:
                r = r[len(temp[0])-1:]
            
            if r=='':
                continue
            #r = r.replace("\r","")
            r1 = r
            x = re.findall(':\d+:',r1)
            if x==[]:
                continue
            i1 = r1.index(x[0])
            rec1 = r1[:i1]
            r2 = r1[i1+1:]
            i2 = r2.index(":")
            rec2 = r2[:i2]
            rec3 = r2[i2+1:]
            
            temp = re.findall('^-|^\+',rec3)
            if temp != []:
                rec3 = ' '+rec3
            
            #if len(rec3) >90000:
            #    continue
            #elif rec3 >60000:
            #    rec3 = [rec3[0:30000],rec3[30000:60000],rec3[60000:90000]]
            #elif rec3 >30000:
            #    rec3 = [rec3[0:30000],rec3[30000:60000]]
            #else:
            #    rec3 = [rec3]
            
            result.append([rec1,rec2,rec3])
    else:
        result.append(["扫描结果"])
        for r in reader:
            if r=='\n':
                continue
            r = r.replace("\r","")
            r = r.replace("\n","")
            
            temp = re.findall('^-|^\+',r)
            if temp != []:
                r = ' '+r
            
            result.append([r])

    return result

def compareHistory(fileName,readResult):
    compareResult = []
    abandonResult = []
    fileName = fileName.split("/")[-1]
    fileName = fileName.replace(".txt",".csv")
    historyPath = get_resultPath()+"/../config/history/"+fileName
    #historyFileName = os.listdir(historyPath)
    pathExist = os.path.exists(historyPath)
    
    if not pathExist:
        compareResult = readResult
        return [compareResult,abandonResult]
    
    historyResult = []
    historyRead = csv.reader(file(historyPath, 'rb'))
    for line in historyRead:
        #if not re.match('^\w|^-|^/|\[|^\s',line[0]):
        #    continue
        
        tmp = re.findall('VM_Set-X|VM_Bash-X|VM_JSX_Language|VM_Password|VM_Sensitive|VM_unsafe_encrypt',historyPath)
        #if ("VM_Set-X" or "VM_Bash-X" or "VM_JSX_Language" or "VM_Password" or "VM_Sensitive" or "VM_unsafe_encrypt") in historyPath:
        if tmp != []:
            type = line[3]
            historyResult.append([":".join([line[0],line[1],line[2]]),type])
        else:
            type = line[1]
            historyResult.append([line[0],type])
    
    
    history_rs = ""
    for hs in historyResult:
        temp = hs[0].replace(' -', '').replace(' +', '')
        #temp = temp.replace('\\', '\\\\').replace('*', '\*').replace('$', '\$').replace('(', '\(').replace(')', '\)').replace('^', '\^').replace("\"","\\\"").replace(".","\.").replace("|","\|").replace("[isBlock]",".*")
        temp = "^"+temp+"$"
        history_rs = history_rs + temp + "|"
    history_rs = history_rs[:len(history_rs)-1]
    
    for tmpR in readResult:
        isMatch = False
        rs = ":".join(tmpR)
        rs = rs.replace("\n","")
        rs = rs.replace(' -', '').replace(' +', '')
        if len(rs) > 70000:
            abandonResult.append(tmpR)
            continue
        if len(rs) > 3000:
            compareResult.append(tmpR)
            continue
        x0 = re.findall(history_rs,rs)
        if x0!=[]:
            isMatch = True
        
        if isMatch == False:
            compareResult.append(tmpR)
        else:
            abandonResult.append(tmpR)
        
    
    return [compareResult,abandonResult]


def txt_to_csv():
    print 'Compare with history:'
    all_txtFile = getAllTxt()
    for f in all_txtFile:
        print ' '*4+time.strftime('%Y-%m-%d %H:%M:%S')
        print ' '*4+f
        newTxt_c = f.replace("/result","/result/compareResult")
        newCsv_c = newTxt_c.replace(".txt",".csv")
        dir_c = os.path.dirname(newCsv_c)
        pathExist_c = os.path.exists(dir_c)
        if not pathExist_c:
            os.makedirs(dir_c)
        
        newTxt_a = f.replace("/result","/result/abandonResult")
        newCsv_a = newTxt_a.replace(".txt",".csv")
        dir_a = os.path.dirname(newCsv_a)
        pathExist_a = os.path.exists(dir_a)
        if not pathExist_a:
            os.makedirs(dir_a)
        
        resultPath = f.split('/result')[0]+'/result'
        set_resultPath(resultPath)
        
        newResult = txtFormat(f)
        rs = compareHistory(f,newResult)
        compareResult = rs[0]
        abandonResult = rs[1]
        
        if len(compareResult)>1: #or (compareResult!=[] and re.match('^\w|^-|^/|\[|^\s',compareResult[0][0]) ):
            csvFile = open(newCsv_c,"wb")
            txtFile = open(newTxt_c,"wb")
            writer = csv.writer(csvFile)
            for rs in compareResult:
                writer.writerow(rs)
                if rs == compareResult[0] or ""==":".join(rs):
                    continue
                txtFile.write(":".join(rs)+"\n")
            csvFile.close()
            txtFile.close()
        
        if len(abandonResult)>1 or (abandonResult!=[] and re.match('^\w|^-|^/|\[|^\s',abandonResult[0][0]) ):
            csvFile = open(newCsv_a,"wb")
            txtFile = open(newTxt_a,"wb")
            writer = csv.writer(csvFile)
            for rs in abandonResult:
                writer.writerow(rs)
                if rs == abandonResult[0] or ""==":".join(rs):
                    continue
                txtFile.write(":".join(rs)+"\n")
            csvFile.close()
            txtFile.close()

