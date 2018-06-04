#-*- coding: utf-8 -*-

import sys
import datetime
reload(sys)
sys.setdefaultencoding('utf-8')


def init():
    global _global_dict
    _global_dict = {}

def setValue(name,value):
    if name == "logDir":
        if getValue("startTime") is None:
            setValue("startTime",str(datetime.datetime.now()))
        _global_dict["logFile"] = value+"/Log"+getValue("startTime").replace(" ","").replace(":","").replace(".","").replace("-","")+".log"
    if name == "startTime":
        if getValue("startTime") is not None:
            value = getValue("startTime")
    _global_dict[name] = value

def getValue(name,value=None):
    try:
        return _global_dict[name]
    except:
        return value

