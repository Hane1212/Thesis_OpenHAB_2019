# This script allow to create trace in xml format
import re
import time
import datetime
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom
from collections import OrderedDict
import json
import csv
import os, glob
import pandas as pd

csv_folder = '/Users/huongta/Home/Internship/openhab/Traces'
filec = '/Users/huongta/Home/Internship/openhab/Traces/common.csv'
infileF = '/Users/huongta/Home/Internship/openhab/openhab-2/userdata/logs/openhab.log'

# from ElementTree_pretty import prettify
traceF = '/Users/huongta/Home/Internship/openhab/openhab-2/userdata/logs/trigger_V6.txt'

INFO = '[INFO ]'
parseValue = []
GROUP1 ={'vTimeOfDay':'DAY', 'Storm':'OFF', 'LivingDining_Shutter':0, 'LivingDining_Door':'CLOSED'}
GROUP2 ={'Martin_LivingDining_Motion':'ON', 'Alice_LivingDining_Motion':'OFF', 'LivingDining_Door':'OPEN', 'LivingDining_Light':'OFF', 'LivingDining_Heating':0}
Trigger = ''    
generated_on = str(datetime.datetime.now())

# time_temp = getTimeNow()
def getTimeNow():
    currentDT = '{0:%Y%m%d_%H%M%S}'.format(datetime.datetime.now())
    return currentDT


def readLog(cfile):
    with open (cfile, 'rt') as f:
        line = f.readlines()
        print(len(line))
        i=0
        while i < len(line):           
            if 'Trigger' in line[i]:
                tag, value = getArg(line[i])
                writeTrace(traceF, value)
                i=i+1
            if 'START' in line[i]:
                tagRule, value = getArg(line[i])
                writeTrace(traceF, tagRule)
                i=i+1
                while 'FINISH' not in line[i] and i <len(line):
                    tag, value = getArg(line[i])
                    if 'STATE' in line[i]:
                        item, state = getState(value)
                        setGroup(item, state)
                        i=i+1
                    if 'OriginalTime' in line[i]:
                        time = getTime(line[i])
                        writeTrace(traceF, time)
                        i=i+1
                    i=i+1
            if 'FINISH' in line[i]:
                input = json.dumps(GROUP1)
                writeTrace(traceF, input)
                writeTrace(traceF, json.dumps(GROUP2))
                i=i+1
            if 'OriginalTime' in line[i]:
                time = getTime(line[i])
                writeTrace(traceF, time)
                i=i+1
            else:
                i=i+1

def writeTrace(file, mes):
    f = open(file, "a")
    f.write(mes)
    f.write('\n')
# update value of item in group
def setGroup(item, state):
    if item in GROUP1:
        GROUP1[item] = str(state)
    if item in GROUP2:
        GROUP2[item] = str(state)
# Get current state of item
def getState(line):
    get = []
    try:
        get = line.split(' changed to ')
    except Exception as e:
        print(e)
    return get[0], get[1]
# Get value, timestamp, tag in log line
def getArg(line):
    parseValue = parseLine(line)
    tag = parseValue[1]
    value = parseValue[0]
    return tag, value
# Analysis line in INFO.log file
def parseLine(line):
    getV = []
    if '[' in line:
        temp_value = line.split(' - ')
        value = temp_value[len(temp_value)-1].strip()
        getV.append(value)
        temp_value = line.split(INFO)[1]
        tag = temp_value[temp_value.find('[')+1 : temp_value.find(']')]
        temp_ = tag.split('.')
        tag = temp_[len(temp_)-1]
        getV.append(tag)
    return getV

def getTime(line):
    temp = []
    # 2019-04-16 10:54:50.693 [INFO ] [OriginalTime] - Martin_LivingDining_Motion: 2019-04-10 13:33:01.426000+00:00
    try:
        temp = line.split('[OriginalTime] - ')
    except Exception as e:
        print(e)
    return temp[1]

important = []
# Filter line with INFO in openhab.log
def getINFOLog(Olog, Ilog):
    with open(Olog) as f:
        f = f.readlines()
        for line in f:
            if INFO in line:
                important.append(line)
    with open(Ilog, 'a') as ilog:
        for i in important:
            ilog.write(i)

if __name__ == "__main__":
    infoFileF = '/Users/huongta/Home/Internship/openhab/openhab-2/userdata/logs/INFO_'+getTimeNow()+'.log'
    # Filter log with [INFO ] then Write [INFO ] log to file
    getINFOLog(infileF, infoFileF)
    # Write [INFO ] log to file
    # writeIlog(infoFileF)
    # readLog(infoFileF)
    # getTimeNow()
