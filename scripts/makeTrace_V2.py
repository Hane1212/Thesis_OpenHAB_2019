# 2019-04-23
# This script allow to create trace in xml format
import re
import os
import time
import datetime
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom
# from xml.dom.minidom import parseString
from collections import OrderedDict
import fileinput
import subprocess
from configparser import ConfigParser  
# from ElementTree_pretty import prettify

INFO = ' [INFO ]'

parseValue = []
ruleGroup  = {}
generated_on = str(datetime.datetime.now())

# Get Argument from config.ini file
def getConfig(tag, item):
    config = ConfigParser() 
    config.read('config.ini') 
    temp_ = config.get(tag, item)
    return temp_

# def setConfig():
#     config = ConfigParser() 
#     root = getConfig('FILE_DIR', 'ROOT_test')
#     dt_now = getTimeNow()
#     log_INFO_test = root+'/INFO_'+dt_now+'.log'
#     trace_test = root+'/trace_'+dt_now+'.xml'
#     config.add_section('FILE_DIR')
#     config.set('FILE_DIR', 'log_INFO_test',log_INFO_test)
#     config.set('FILE_DIR', 'trace_test',trace_test)
#     with open('config.ini', 'a') as configfile:
#         config.write(configfile)


def getTimeNow():
    currentDT = '{0:%Y%m%d_%H%M%S}'.format(datetime.datetime.now())
    return currentDT
# Write log in xml format
def prettify(elem, tfile):
    """Return a pretty-printed XML string for the Element."""
    # rough_string = ET.tostring(elem, 'utf-8', 'xml')
    rough_string = ET.tostring(elem).decode('utf-8')
    # print(rough_string)
    reparsed = minidom.parseString(rough_string)
    myfile = open(tfile, "w")  
    myfile.write(reparsed.toprettyxml(indent="\t"))
    # return reparsed.toprettyxml(indent="  ")

# Get all data
def writeTrace(traceFile, cfile):
    trace = Element('trace')
    trace.set('version', '1.0')
    trace.append(Comment('Generated by HuongTA for M2R Project'))
    head = SubElement(trace, 'head')
    title = SubElement(head, 'title')
    title.text = 'My smart home data'
    dc = SubElement(head, 'dateCreated')
    dc.text = generated_on
    body = SubElement(trace, 'body')
    rule = SubElement(body, 'body')
    state = SubElement(body, 'body')
    startTime = getConfig('DURATION', 'startTime')
    stopTime = getConfig('DURATION', 'stopTime')
    print(startTime)
    print(stopTime)

    with open (cfile, 'rt') as f:
        line = f.readlines()
        print(len(line))
        i=0     
        while i < len(line):  
            timeLog = getTime(line[i])    
            while startTime < timeLog < stopTime:
                timestamp, tagRule, value = getArg(line[i])  
                if 'START' in line[i]:
                    rule_ = SubElement(rule, 'rule', OrderedDict([('timestamp', timestamp), ('state', 'START'), ('rule', tagRule)]))
                    ruleGroup[tagRule] = rule_
                elif 'FINISH' in line[i]:
                    SubElement(rule, 'rule', OrderedDict([('timestamp', timestamp), ('state', 'FINISH'), ('rule', tagRule)]))
                    del ruleGroup[tagRule]
                elif 'Rule:' in line[i]: 
                    rule_= ruleGroup.get(tagRule)
                    SubElement(rule_, 'action', OrderedDict([('timestamp', timestamp), ('rule', tagRule), ('action', value)]))
                elif 'STATE' in tagRule:
                    SubElement(state, 'state', OrderedDict([('timestamp', timestamp), ('state', tagRule), ('item', value)]))
                i=i+1
                timeLog = getTime(line[i])
            if timeLog > stopTime:
                i = len(line)
            i=i+1
    prettify(trace, traceFile)
    # myfile = open(traceFile, 'w')
    # myfile.write(trace)
def getTime(line):
    getT = []
    try:
        getT = line.split(' [')
    except Exception as e:
        print(e)
    return getT[0]


def newLine(i, line, body):
    if (i == len(line)-1):
        getEvent(line[i], body)
    else:
        i=i+1 
    return i

def getState(v):
    get = []
    get  = v.split(' changed to ')
    return get[0], get[1]

def getEvent(line, parent):
    timestamp, tag, value=getArg(line)
    SubElement(parent, 'event', OrderedDict([('timestamp', timestamp), ('tag', tag), ('event', value)]))    

def getArg(line):
    parseValue = parseLine(line)
    timestamp = parseValue[0]
    tag = parseValue[2]
    value = parseValue[1]
    return timestamp, tag, value

def parseLine(line):
    getV = []
    if '[' not in line:
        print(line)
    else:
        timestamp = line.split(' [')[0]
        getV.append(timestamp)
        temp_value = line.split(' - ')
        value = temp_value[len(temp_value)-1].strip()
        getV.append(value)
        if INFO in line:
            temp_value = line.split(INFO)[1]
            tag = temp_value[temp_value.find('[')+1 : temp_value.find(']')]
            temp_ = tag.split('.')
            tag = temp_[len(temp_)-1]
        else:
            tag = line[line.find('[')+1 : line.find(']')]
        getV.append(tag)
        return getV


important = []
# Filter line with INFO in openhab.log
def getINFOLog():
    INFO_temp = getConfig('FILE_DIR', 'INFO_temp')
    openHABlog = getConfig('FILE_DIR', 'openHABlog')
    try:
        exists = os.path.isfile(INFO_temp)
        if exists:
            os.remove(INFO_temp)
    except Exception as e:
        print(e)

    with open(openHABlog) as f:
        f = f.readlines()
        for line in f:
            if INFO in line:
                important.append(line)
    with open(INFO_temp, 'a') as ilog:
        for i in important:
            ilog.write(i)
# File CMD.log with time format include ',' => replace ',' by '.'
def makeTimeFormat(f):
    # Read in the file
    log_CMD_temp = getConfig('FILE_DIR','log_CMD')
    with open(log_CMD_temp, 'r') as file :
        filedata = file.read()
        # Replace the target string
        filedata = filedata.replace(',', '.')
    # Write the file out again
    with open(f, 'w') as file:
        file.write(filedata)
    
if __name__ == "__main__":
    # Filter log with [INFO ] then Write [INFO ] log to file
    # makeTimeFormat(log_CMD)
    # root = getConfig('FILE_DIR', 'ROOT_test')
    # dt_now = getTimeNow()
    # log_INFO_test = root+'/INFO_'+dt_now+'.log'
    # trace_test = root+'/trace_'+dt_now+'.xml'
    # getINFOLog()
    # cmd = 'sort '+INFO_temp+' '+ log_CMD+ ' > '+ infoFile
    # print(cmd)
    # setConfig()
    # subprocess.run([cmd])
    INFO_temp = getConfig('FILE_DIR', 'INFO_temp')
    trace_test = getConfig('FILE_DIR', 'trace')
    writeTrace(trace_test, INFO_temp)
