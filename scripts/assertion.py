import re
import time
import datetime
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom
from configparser import ConfigParser  
from lxml import etree
from xmldiff import main, formatting
import matplotlib.pyplot as plt
import csv
import json
import matplotlib.dates as md
import string
import difflib
import os, glob, shutil, os.path 
import csvdiff
import dominate as do
from dominate.tags import *
from jinja2 import FileSystemLoader, Environment

INFO = ' [INFO ]'
ROOT_report = 'ROOT_report'
ROOT_real = 'ROOT_real'
ROOT_test = 'ROOT_test'
FILE_DIR = 'FILE_DIR'
DURATION = 'DURATION'
Version = 'Version'
TestLog = 'openHABlog_test'
RealLog = 'openHABlog'

ruleGroup = {}
# Read information from config.ini file
def getConfig(tag, item):
    config = ConfigParser() 
    config.read('config.ini') 
    temp_ = config.get(tag, item)
    return temp_

def getDir(root, item):
    dir_=''
    root_ = getConfig('FILE_DIR', root)
    ver = getConfig('DURATION', 'Version')
    type_ = getConfig('FILE_DIR', item)
    if 'test' in root:
        dir_ = root_+ver+'/'+item+'_test_'+ver+'.'+type_
    else: dir_ = root_+ver+'/'+item+'_'+ver+'.'+type_
    return dir_

class Line:
    def __init__(self, line):
        self.line = line

    def getOrgTime(self, line):
        v = self.getValue(line)
        try:
            v = v.replace('Original timestamp: ','')
        except Exception as e:
            print(e)
        return v

    # Get time from log file
    def getLogTime(self, line):
        getT = []
        try:
            getT = line.split(' [')
        except Exception as e:
            print(e)
        return getT[0]
    # Get value, timestamp, tag in log line
    def getValue(self, line):
        parseValue = self.parseLine(line)
        value = parseValue[0]
        return value
    # Analysis line in INFO.log file
    def parseLine(self, line):
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

def clearnfile(path):
    try:
        files = glob.glob(path)
        for f in files:
            os.remove(f)
    except Exception as e:
        print(e)

def writeFile(file, mes):
    f = open(file, "a")
    f.write(mes)
    f.write('\n')
# Return original time of trigger in log
trigger_list = {}
def getRule(r, trace, dictf):
    trigger_list.clear()   
    dictf = getDir(r, dictf)
    trigger_file = getDir(r, 'trigger_trace')
    trace_xml_flie = getDir(r, trace)
    trace_xml = minidom.parse(trace_xml_flie)
    itemlist = trace_xml.getElementsByTagName('trigger')
    print(len(itemlist))
    tree = ET.parse(trace_xml_flie)
    root = tree.getroot()
    co = 0
    for trigger in root.iter('trigger'):
        trig = trigger.attrib['item'] + ': ' +trigger.attrib['state']    
        temp = []  
        for rule in trigger:
            if rule.attrib['state'] == 'START':
                temp.append(rule.attrib['rule'])
            for action in rule:
                temp.append(action.attrib['action'])
        if trig in trigger_list:  
            co=co+1
            c = isExist(trig, temp) 
            if int(c) >0:
                trigger_list[trig+'_'+str(c)] = temp
                createCSV(trig, trig+'_'+str(c), trigger_file)
            else: createCSV(trig, trig, trigger_file)
        else: 
            co=co+1
            trigger_list[trig] = temp 
            createCSV(trig, trig, trigger_file)
    with open(dictf, 'w') as f:
        writer = csv.writer(f)
        for key, value in trigger_list.items():
            writer.writerow([key, value])
    # updateFormat(dictf)

def updateFormat(dictf):
    f =  open(dictf).read()
    f = f.replace('[','')
    f = f.replace(']','')
    f = f.replace('\"','')
    f = f.replace('\'','')  
    s =  open(dictf, 'r+')
    s.write(f)
    s.close()
    with open(dictf, "r+") as f:
        lines = f.readlines()
        lines.sort()        
        f.seek(0)
        f.writelines(lines)
# Check if rule already in trigger list or not
def isExist(trig, tem):
    c = 0
    a = []
    for i in trigger_list.keys():
        if trig in i:
            val_temp = trigger_list.get(i)
            if val_temp == tem:
                return c
            else:
                try:
                    t = i.split(': ')[1]
                except Exception as e:
                        print(e)
                if '_' in t:
                    a.append(int(t.split('_')[1]))
                else: a.append(0)
    if len(a) > 0: c = max(a) +1 
    return c

# Return list of trigger from openhab.log
def getTriggerOrder(root, trigFile, openHABlogFile, start, stop):
    triggerFile = getDir(root, trigFile)
    startTime = getConfig(DURATION, start)
    stopTime = getConfig(DURATION, stop)
    openHABlog = getConfig(FILE_DIR, openHABlogFile)
    print(startTime)
    print(stopTime)
    count = 0
    with open (openHABlog, 'rt') as f:
        line = f.readlines()
        print(len(line))
        i=0
        while i < len(line):    
            line_ = Line(line[i])
            timeLog = line_.getLogTime(line[i])  
            while startTime < timeLog < stopTime:       
                if 'Trigger' in line[i]:
                    count = count+1
                    value = line_.getValue(line[i])
                    writeFile(triggerFile, value)
                i=i+1
                timeLog = line_.getLogTime(line[i])
                if timeLog > stopTime:
                    i = len(line)
            i=i+1
    return count

# CSV file to save result of matching trigger as timestamp - item - result
def logCSV(root, timestamp, item, result, type):
    csv_f = ''
    root_ = getConfig(FILE_DIR, root)
    ver = getConfig(DURATION, Version)
    if type=='Org': csv_f = root_+ver+'/State/'+item+'.csv'
    else: csv_f = root_+ver+'/State_test/'+item+'.csv'
    isExist = os.path.isfile(csv_f)
    with open(csv_f, 'a') as fp:
        fp.write(str(timestamp)+';'+ str(item)+';'+str(result)+'\n')

def w_csv(file, value):  
    with open(file, 'a') as fp:
        fp.write(value)

# CSV file to save result of matching trigger as count - result
def createCSV(count, result, file):
    with open(file, 'a') as fp:
        fp.write(str(count)+','+str(result)+'\n')

def create_Sum(elem, val, file):
    csv_file = csv.reader(open(file, "r+"), delimiter=";")
    isExist = False
    for row in csv_file:
        if row[0] == elem:
            row[1] = val
            isExist = True
    if isExist == False:
            csv_file.write(str(elem)+';'+str(val)+'\n')

def getValInCSV(val, file):
    csv_file = csv.reader(open(file, "r"), delimiter=",")
    try:
        for row in csv_file:
            if val == row[1]:
                return row[0]
    except Exception as e: print("getValInCSV: " +e)    

# Return CSV file of all sensors of the system
# getSystemState_BaseO(ROOT_test, TestLog, 'startTime_test', 'stopTime_test')
# getSystemState_BaseO(ROOT_real, RealLog, 'startTime', 'stopTime')
def getSystemState_BaseO(root, log, start, stop):
    cfile = getConfig(FILE_DIR, log)
    r = getConfig(FILE_DIR, root)
    ver = getConfig(DURATION, Version)
    clearnfile(r+ver+'/State/*')
    csv_f = r+ver+'/State/common.csv'
    startTime = getConfig(DURATION, start)
    stopTime = getConfig(DURATION, stop)
    real_time = '2019-05-07 14:22:10.126'
    original_time = '2019-05-06 14:22:43.609'
    isTest = False
    with open (cfile, 'rt') as f:
        line = f.readlines()
        print(len(line))
        i=0
        while i < len(line):  
            l = Line(line[i])
            timeLog = l.getLogTime(line[i])    
            while startTime < timeLog < stopTime:
                if 'SimClock' in line[i]:
                    isTest = True
                    real_time = timeLog
                    original_time = l.getOrgTime(line[i])
                elif 'STATE' in line[i]:
                    v = l.getValue(line[i])
                    if isTest:
                        sim_clock = str2Time(timeLog) - str2Time(real_time)
                        time_log = str2Time(original_time) + sim_clock
                        logCSV(root , time_log, v.split(' changed to ')[0], v.split(' changed to ')[1], 'Org') 
                        var = str(time_log)+';'+ str(v.split(' changed to ')[0])+';'+str(Str2Num(v.split(' changed to ')[1]))+ '\n'
                        w_csv(csv_f , var) 
                    else: 
                        logCSV(root , timeLog, v.split(' changed to ')[0], v.split(' changed to ')[1], 'Org') 
                        var = str(timeLog)+ ';'+ str(v.split(' changed to ')[0])+';'+str(Str2Num(v.split(' changed to ')[1]))+'\n'
                        w_csv(csv_f , var) 
                i = i+1
                timeLog = l.getLogTime(line[i]) 
                if timeLog > stopTime:
                    i = len(line)
            i=i+1

def getSystemState_BaseV(root, log, start, stop):
    print("getSystemState_BaseV")
    print(root)
    cfile = getConfig(FILE_DIR, log)
    r = getConfig(FILE_DIR, root)
    ver = getConfig(DURATION, Version)
    root_ = getConfig(FILE_DIR, ROOT_report)
    csv_f = r+ver+'/State_test/common.csv'
    simf = root_+ver+'/SimClock.csv'
    clearnfile(r+ver+'/State_test/*')
    startTime = getConfig(DURATION, start)
    stopTime = getConfig(DURATION, stop)
    test_time = startTime
    sim_time = getConfig(DURATION, 'startTime_test')
    with open (cfile, 'rt') as f:
        line = f.readlines()
        print(len(line))
        i=0
        while i < len(line):  
            l = Line(line[i])
            timeLog = l.getLogTime(line[i])    
            while startTime < timeLog < stopTime:
                if 'Trigger' in line[i]:
                    sim_time_ = getValInCSV(timeLog, simf)
                    if sim_time_ !=None: sim_time = sim_time_
                    test_time = timeLog
                elif 'STATE' in line[i]:
                    v = l.getValue(line[i])
                    if 'test' not in log:
                        sim_clock = str2Time(timeLog) - str2Time(test_time)
                        time_log = str2Time(sim_time) + sim_clock
                        logCSV(root , time_log, v.split(' changed to ')[0], v.split(' changed to ')[1], 'test') 
                        var = str(time_log)+';'+ str(v.split(' changed to ')[0])+';'+str(Str2Num(v.split(' changed to ')[1]))+ '\n'
                        w_csv(csv_f , var) 
                    else: 
                        # print(timeLog)
                        logCSV(root , timeLog, v.split(' changed to ')[0], v.split(' changed to ')[1], 'test') 
                        var = str(timeLog)+ ';'+ str(v.split(' changed to ')[0])+';'+str(Str2Num(v.split(' changed to ')[1]))+'\n'
                        w_csv(csv_f , var) 
                i = i+1
                timeLog = l.getLogTime(line[i]) 
                if timeLog > stopTime:
                    i = len(line)
            i=i+1

def setSimClock():
    cfile = getConfig(FILE_DIR, 'openHABlog_test')
    root = getConfig(FILE_DIR, ROOT_report)
    ver = getConfig(DURATION, Version)
    startTime = getConfig(DURATION, 'startTime_test')
    stopTime = getConfig(DURATION, 'stopTime_test')
    simf = root+ver+'/SimClock.csv'
    with open (cfile, 'rt') as f:
        line = f.readlines()
        print(len(line))
        i=0
        while i < len(line):  
            l = Line(line[i])
            timeLog = l.getLogTime(line[i])    
            while startTime < timeLog < stopTime:
                if 'SimClock' in line[i]:
                    original_time = l.getOrgTime(line[i])
                    createCSV(timeLog,original_time, simf)
                i = i+1
                timeLog = l.getLogTime(line[i]) 
                if timeLog > stopTime:
                    i = len(line)
            i=i+1
# String to datetime format
def str2Time(time):
    # print(time)
    date_time_obj = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
    return date_time_obj          

# Read data from csv file then add to array x[], y[]
def getData(file):
    x = []
    y = []
    with open(file,'r') as csvfile:
        plots = csv.reader(csvfile, delimiter=';')
        for row in plots:
            if 'item' not in row:
                x.append(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f'))
                v = Str2Num(row[2])
                y.append(int(v))
    return x, y
    
def Str2Num(state_):
    v = ''
    if state_ =='OFF': v = '0'
    elif state_ == 'ON': v = '1'
    elif state_ == 'OPEN': v = '1'
    elif state_ == 'CLOSED': v = '0'
    elif state_ == 'DAY': v = '1'
    elif state_ == 'NIGHT': v = '0'    
    else: v = state_
    return v

class Graph():
    # Display the state of system as the signal base on data in the csv file
    def graphSystemState(self, type):
        ver = getConfig(DURATION, Version)
        real_root = getConfig(FILE_DIR, ROOT_real)
        real_csv = real_root+ver+'/'+type+'/'
        test_root = getConfig(FILE_DIR, ROOT_test)
        test_csv = test_root+ver+'/'+type+'/'
        fs = os.listdir(real_csv) # 

        fig, ax = plt.subplots(len(fs)-1, sharex=True, figsize=(20, 10))
        c=0
        for file in fs:
            if file.endswith(".csv"):
                s = os.path.join(real_csv, file) # your file
                head, tail = os.path.split(s) 
                if 'TimeOfDay' not in tail: 
                    exists = os.path.isfile(test_csv+tail)
                    if exists:
                        tail_ = tail.replace('_'+ver, '')
                        tail_ = tail_.replace('.csv','')
                        addPlot(ax, c, s, tail_)
                        addPlot(ax, c, test_csv+tail, tail_)
                        c = c+1
        img = getConfig(FILE_DIR, ROOT_report)+ver+'/System'+type+'.png'
        fig.savefig(img)
    
    def graphActuator(self, type):
        ver = getConfig(DURATION, Version)
        real_root = getConfig(FILE_DIR, ROOT_real)
        real_csv = real_root+ver+'/'+type+'/'
        test_root = getConfig(FILE_DIR, ROOT_test)
        test_csv = test_root+ver+'/'+type+'/'
        fs = os.listdir(real_csv) # 
        
        for file in fs:
            if file.endswith(".csv"):
                s = os.path.join(real_csv, file) # your file
                head, tail = os.path.split(s) 
                if 'TimeOfDay' not in tail: 
                    exists = os.path.isfile(test_csv+tail)
                    if exists:
                        tail_ = tail.replace('_'+ver, '')
                        tail_ = tail_.replace('.csv','')
                        fig, ax = plt.subplots(3, sharex=True, figsize=(20, 10))
                        addPlot(ax, 0, s, tail_)
                        addPlot(ax, 1, test_csv+tail, tail_)
                        img = getConfig(FILE_DIR, ROOT_report)+ver+'/'+type+'/'+tail_+'.png'
                        fig.savefig(img)
    
# Add single graph
def addPlot(ax, j,file, ylab):
    # print(file)
    x = []
    y = []
    x, y = getData(file)
    ax[j].step(x,y, 'o-')
    plt.xlabel('timestamp')
    plt.ylabel(ylab, rotation=90)
    plt.xticks(x, rotation=25)
    xfmt = md.DateFormatter('%H:%M:%S.%f')
    ax[j].xaxis.set_major_formatter(xfmt)

# Write trigger/rule/action
def writeTuple(mylist, c = 0):
    diff_list = getDir('ROOT_report', 'trace_diff')
    temp = ''
    if mylist == 0:
        temp = '0'
    elif mylist == 1:
        temp = '1'
    else:
        temp = mylist.attrib
    with open(diff_list, 'a') as fp:
        fp.write(str(c)+' '+str(temp)+'\n')

class Assert(): 
    def __init__(self):
        r = getConfig(FILE_DIR, ROOT_report)
        ver = getConfig(DURATION, Version)
        self.report_f = r+ver+'/sumary.csv'     
    # (2) Compare trigger from openHAB log
        # Input:    openHAB log
        # Output:   trigger.txt - List of trigger(root folder)
        #           Percent of matching between two trigger files
    def trigger_assert(self):
        print('Trigger assertion')
        c1 = getTriggerOrder(ROOT_real,'trigger', 'openHABlog', 'startTime', 'stopTime')
        c2 = getTriggerOrder(ROOT_test,'trigger', 'openHABlog_test', 'startTime_test', 'stopTime_test')
        f1 = open(getDir(ROOT_real, 'trigger'), 'r')
        f2 = open(getDir(ROOT_test, 'trigger'), 'r')
        s = difflib.SequenceMatcher(None, f1.read(), f2.read())
        create_Sum('trigger_real_system', sum(1 for line in open(getDir(ROOT_real, 'trigger'))), self.report_f)
        create_Sum('trigger_sim_system', sum(1 for line in open(getDir(ROOT_test, 'trigger'))), self.report_f)
        create_Sum('trigger_match', round(s.real_quick_ratio(),2), self.report_f)
        print(s.real_quick_ratio())
        # getDiffFile('trigger', 'trigger_test', 'trigger_diff')  
    # (3) Compare two trigger.xml file, output is diff.xml and csv file which count number of match-not match 
        # Input:    trigger_trace.csv
        # Output:   Graph diff between two trace files
    def trace_assert(self):
        print('Trace assertion')
        ver = getConfig(DURATION, Version)
        f1 = open(getDir(ROOT_real, 'trigger_trace'), 'r').readlines()
        f2 = open(getDir(ROOT_test, 'trigger_trace'), 'r').readlines()
        diff_file = getDir(ROOT_report, 'traceDiffResult')
        count = 0
        for line in difflib.unified_diff(f1, f2 , n = 100):
            if '---' not in line:
                if '+++' not in line:
                    if '@@' not in line:
                        count = count+1
                        if '+' in line or '-' in line:
                            createCSV(count, 1, diff_file)
                        else: createCSV(count, 0, diff_file)
        fig, ax = plt.subplots(1, figsize=(20, 10))
        x = []
        y = []
        with open(diff_file,'r') as csvfile:
            plots = csv.reader(csvfile, delimiter=',')
            for row in plots:
                x.append(int(row[0]))
                y.append(int(row[1]))
        ax.step(x,y, 'o-')
        plt.xlabel('timestamp')
        plt.ylabel('Similar', rotation=90)
        img = getConfig(FILE_DIR, ROOT_report)+ver+'/SystemSimilary.png'
        fig.savefig(img)
    
    # (1) Compare trigger-action from trace.xml, save list of trigger/rule -> csv file
        # Input:    trace.xml
        # Output:   dict.txt - list of all rules(root folder), 
        #           trace.csv - list of trigger-rules(report folder)
        #           Percent of matching between two dicts
    def rules_assert(self):
        print('Rule assertion')
        getRule(ROOT_real, 'trace', 'dict')
        getRule(ROOT_test, 'trace', 'dict')
        f1 = open(getDir(ROOT_real, 'dict'), 'r')
        f2 = open(getDir(ROOT_test, 'dict'), 'r')
        s = difflib.SequenceMatcher(None, f1.read(), f2.read())
        create_Sum('Rule_real_system', sum(1 for line in open(getDir(ROOT_real, 'dict'))), self.report_f)
        create_Sum('Rule_sim_system', sum(1 for line in open(getDir(ROOT_test, 'dict'))), self.report_f)
        create_Sum('Rule_match', round(s.real_quick_ratio(),2), self.report_f)
        print(s.real_quick_ratio())
    # (4) Compare STATE of all sensors
        # Input:    openHAB log
        # Output:   trigger.csv - list of all state(root folder)
        #           Graph diff between two systems
    def state_assert(self):
        # g = Graph()
        print('State assertion')
        getSystemState_BaseO(ROOT_test, TestLog, 'startTime_test', 'stopTime_test')
        getSystemState_BaseO(ROOT_real, RealLog, 'startTime', 'stopTime')
        # g.graphSystemState('State')
        getSystemState_BaseV(ROOT_test, TestLog, 'startTime_test', 'stopTime_test')
        getSystemState_BaseV(ROOT_real, RealLog, 'startTime', 'stopTime')
        # g.graphSystemState('State_test')
        # g.graphActuator('State_test')
        # g.graphActuator('State')

class Report_():
    def GeneralReport_(self):
        ver = getConfig(DURATION, Version)
        img_state = getConfig(FILE_DIR, ROOT_report)+ver+'/SystemState.png'
        img_si = getConfig(FILE_DIR, ROOT_report)+ver+'/SystemSimilary.png'
        f = self.getOutDir()
        d = do.document()
        with d:
            d += h1('End User Debugging Report')
            d += p('This report was automatically generated.')
            d += h2('Quick summary')
            d += h2('TRIGGER_ASSERT')
            h = ul()
            with h:
                li('Number of Trigger in the real system:')
                li('Number of Trigger in the simulation system: ')
                li('Number of Trigger in common between two version: ')
                li('Matching: ')
        d = self.setRule_(d)
        d = self.setImg_(d, img_state, 'STATE_ASSERT')
        d = self.setImg_(d, img_si, 'TRACE_ASSERT')
        with open(f, 'w') as fi:
            fi.write(d.render())
    def setRule_(self, d):
        with d:
            d += h2('RULE_ASSERT')
            h = ul()
            with h:
                li('Number of Rule in the real system:')
                li('Number of Rule in the simulation system: ')
                li('Number of Rule in common between two version: ')
                li('Matching: ')
        return d
    def setImg_(self, d, ig, name):
        with d:
            d += h2(name)
            i = img(src = ig)
        return d

    def getOutDir_(self):
        output = getConfig(FILE_DIR, ROOT_report)
        ver = getConfig(DURATION, Version)
        dir_ = output+ver+'/Report_'+ver+'.html'
        return dir_

def initial():
    # Clearn log & report folder
    root_report = getConfig(FILE_DIR, ROOT_report)
    root_real = getConfig(FILE_DIR, ROOT_real)
    root_test = getConfig(FILE_DIR, ROOT_test)
    ver = getConfig(DURATION, Version)  
    try:
        clearnfile(root_report+'/'+ver+'/*.*')
        clearnfile(root_real+'/'+ver+'/*.*')
        clearnfile(root_test+'/'+ver+'/*.*')
    except Exception as e:
        print(e)

class Report():
    def GeneralReport(self, attr, val):
        env = Environment(loader=FileSystemLoader(searchpath="template"))
        base_template = env.get_template("report.html")
        root = getConfig(FILE_DIR, ROOT_report)
        ver = getConfig(DURATION, Version)
        out = root+ver+'/Report_'+ver+'.html'
        exists = os.path.isfile(out)
        if(exists):
            summary_section_template = out
        else: summary_section_template = env.get_template('summary_section.html')
        # attr.strip('\'')
        title = "End User Debugging Report"
        sections = list()
        print(attr)
        sections.append(summary_section_template.render(attr = val))

        with open(out, "w") as f:
            f.write(base_template.render(
                title=title,
                sections=sections
            ))

def main_():
    a = Assert()
    # r = Report()
    setSimClock()
    # initial()
    # Starting test
    # (1) Compare trigger-action from trace.xml, save list of trigger/rule -> csv file
    # Input:    trace.xml
    # Output:   dict.txt - list of all rules(root folder), 
    #           trace.csv - list of trigger-rules(report folder)
    #           Percent of matching between two dicts => TODO save to report
    # a.rules_assert()
    # (2) Compare trigger from openHAB log
    # Input:    openHAB log
    # Output:   trigger.txt - List of trigger(root folder)
    #           Percent of matching between two trigger files  => TODO save to report
    # a.trigger_assert()
    # (3) Compare two traces file
    # Input:    trigger_trace.csv
    # Output:   Graph diff between two trace files
    # a.trace_assert()
    # (4) Compare STATE of all sensors
    # Input:    openHAB log
    # Output:   trigger.csv - list of all state(report folder)
    #           Graph diff between two systems
    a.state_assert()
    # r.GeneralReport(trigger_real_system, 10)
    # r.GeneralReport(trigger_sim_system, 11)

if __name__ == "__main__":
    main_()
    
    