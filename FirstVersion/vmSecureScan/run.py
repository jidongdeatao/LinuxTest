#-*- coding: GBK -*-
import sys
import os
import shutil

from libs import scanFunctionDef as scanFunction
from fileTool import fileToolDef as fileToolUse

# 虚机配置
toolPath = sys.path[0]
csvfile = toolPath+"/config/vmInfo.csv"


#执行扫描
scanFunction.set_runPath(toolPath)
scanFunction.set_localTime()
scanFunction.set_csvFilename(csvfile)

scanFunction.runAll()

#txt格式的报告转化为csv格式（选作，可注释）
txtPath = scanFunction.get_resultPath()
fileToolUse.set_txtPath(txtPath)
fileToolUse.txt_to_csv()

resultPath = fileToolUse.get_resultPath()
shutil.copy(toolPath+"/config/script-description.txt",resultPath+"/结果排查说明（必读）.txt")
#shutil.rmtree(txtPath)  #删除原始扫描结果
print "请按任意键结束执行....."
os.system("pause")
