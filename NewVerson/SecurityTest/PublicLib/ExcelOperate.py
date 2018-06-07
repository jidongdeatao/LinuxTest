#-*- coding: utf-8 -*-

import os
import sys
import xlwt
import xlrd
from xlutils.copy import copy
reload(sys)
sys.setdefaultencoding('utf8')

import Log
g_Log = None
import LocalOperate
g_Local = None

class Excel:
    def __init__(self,excelName=None,sheetName=None,sheetID=None,lineNum=None,columnNum=None):
        global g_Log,g_Local
        g_Log = Log.Log()
        g_Local = LocalOperate.Local()
        self.excelName = excelName
        self.sheetName = sheetName
        self.sheetID = sheetID
        self.lineNum = lineNum
        self.columnNum = columnNum

    def new(self):#新建一个excel
        try:
            g_Log.writeLog(u"尝试新建{excelPath}".format(excelPath=g_Local.unicode(self.excelName)))
            # 检查excel所在路径是否存在，如不存在则新建完整目录
            excelPath = os.path.split(self.excelName)[0]
            pathExist = os.path.exists(excelPath)
            if not pathExist:
                os.makedirs(excelPath)

            file = xlwt.Workbook()  #新建excel
            if self.sheetName is not None:
                table = file.add_sheet(self.sheetName) #按sheetName新建sheet
            else:
                table = file.add_sheet('sheet1') #新建sheet，取名默认sheet1
            file.save(self.excelName) #保存excel
            g_Log.writeLog(u"新建成功")
        except:
            g_Log.writeLog("traceback")
            return 0

    def write(self,result,redLine=0):# 向excel写入
        try:
            g_Log.writeLog(u"打开并尝试写入{excelPath}".format(excelPath=g_Local.unicode(self.excelName)))
            # 读取excel
            workbook = xlrd.open_workbook(r'{excelPath}'.format(excelPath=self.excelName),formatting_info=True)
            if self.sheetID is not None:
                oldSheet=workbook.sheet_by_index(self.sheetID)
                g_Log.writeLog(u"写入第{id}页".format(id=self.sheetID))
            elif self.sheetName is not None:
                oldSheet=workbook.sheet_by_name(self.sheetName)
                g_Log.writeLog(u"写入\"{sheet}\"页".format(sheet=self.sheetName))

            n_workbook = copy(workbook)
            table = n_workbook.get_sheet(0)

            # 设定excel标题的颜色和字体
            # 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray
            pattern1 = xlwt.Pattern()
            pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
            pattern1.pattern_fore_colour = 3
            style1 = xlwt.XFStyle()
            style1.pattern = pattern1
            pattern2 = xlwt.Pattern()
            pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
            pattern2.pattern_fore_colour = 2
            style2 = xlwt.XFStyle()
            style2.pattern = pattern2

            # 向excel写入内容
            firstrow = oldSheet.nrows
            firstcol = oldSheet.ncols
            for row in range(0,len(result)):
                t = result[row]
                for col in range(0,len(t)):
                    text = t[col][0:32000]
                    if row+firstrow == 0:
                        if col < len(t)-redLine:
                            table.write(row+firstrow,col,text,style1)
                        else:
                            table.write(row+firstrow,col,text,style2)
                    else:
                        table.write(row+firstrow,col,text)
            n_workbook.save(self.excelName) #保存
            g_Log.writeLog(u"写入成功")
        except:
            g_Log.writeLog("traceback")
            return 0

    def read(self): #读取excel内容
        result = []
        g_Log.writeLog(u"打开并尝试读取{excelPath}".format(excelPath=g_Local.unicode(self.excelName)))
        try:
            print self.excelName
            workbook = xlrd.open_workbook(r'{excelPath}'.format(excelPath=self.excelName))
            if self.sheetID is not None:
                sheetInfo = workbook.sheet_by_index(self.sheetID)
                g_Log.writeLog(u"读取第{id}页".format(id=self.sheetID))
            elif self.sheetName is not None:
                sheetInfo = workbook.sheet_by_name(self.sheetName)
                g_Log.writeLog(u"读取\"{sheet}\"页".format(sheet=g_Local.unicode(self.sheetName)))
            for i in range(0,sheetInfo.nrows):
                rowInfo = []
                for j in range(0,sheetInfo.ncols):
                    value = sheetInfo.row_values(i)
                    tvalue = value[j]
                    if tvalue == None:
                        tvalue = ""
                    rowInfo.append(tvalue)
                result.append(rowInfo)
            g_Log.writeLog(u"读取成功")
            return result
        except:
            g_Log.writeLog("traceback")
            return 0









