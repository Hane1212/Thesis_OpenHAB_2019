import csv
import os, glob
import pandas as pd
from configparser import ConfigParser 
import glob
import matplotlib.dates as md
import matplotlib.pyplot as plt
import datetime
import ntpath
import datetime
import operator 
import numpy as np

ALLEN = "ALLEN"
suite = "suite"
FILE_DIR = 'FILE_DIR'
DURATION = 'DURATION'
Version = 'Version'
ROOT_report = 'ROOT_report'
ROOT_real = 'ROOT_real'
ROOT_test = 'ROOT_test'
startTime = 'startTime'
stopTime = 'stopTime'
startTime_test = 'startTime_test'
stopTime_test = 'stopTime_test'
PROPERTIES = 'PROPERTIES'


def getConfig(tag, item):
    config = ConfigParser() 
    config.read('config.ini') 
    temp_ = config.get(tag, item)
    return temp_

def getSuite(pro):
    root_ = getConfig(FILE_DIR, ROOT_real)
    config = ConfigParser() 
    config.read('properties.ini') 
    temp_ = config.get(PROPERTIES, pro)
    elem = []
    try:
        elem = temp_.split(',')
    except Exception as e:
        print('Catch Except: getSuite')
        print(e)
    return elem

def writeFile(file, mes):
    f = open(file, "a")
    f.write(mes)
    f.write('\n')

def graphActuator(log):
    dir = getConfig(ALLEN, suite)
    ver = getConfig(DURATION, Version)
    dir_log = dir+ver+'/'+log
    dir_r = dir+ver+'/result'
    list_pro = os.listdir(dir_r)
    fig, ax = plt.subplots(4, sharex=True, figsize=(20, 10))
    img = 'tem.png'
    for i in list_pro:
        pro = i.replace('.csv','')
        img = dir + ver + '/graph/'+pro+'.png'
        tem = getSuite(pro)
        c=0
        fig, ax = plt.subplots(len(tem)+1, sharex=True, figsize=(20, 10))
        for j in tem:
            ax[c].invert_yaxis()
            addPlot(ax,c, dir_log, j)
            c = c+1
        pro_file = dir_r+'/'+i
        ax[c].invert_yaxis()
        addPlot(ax, c, pro_file , 'Property ' + pro )
        fig.savefig(img)

def manualGraph():
    root = getConfig(ALLEN, suite)
    ver = getConfig(DURATION, Version)
    sensor_v0 = root + ver+ '/common_V0.csv'
    sensor_v1 = root + ver+'/common_V1.csv'
    sensor_v2 = root + ver+'/common_V2.csv'
    pro_V0 = root + ver+'/result_V0/S1.csv'
    pro_V1 = root + ver+'/result_V1/S1.csv'
    pro_V2 = root + ver+'/result_V2/S1.csv'

    pro_V0S2 = root + ver+'/result_V0/S2.csv'
    img = root + ver+'/graph/compareTrace.png'
    # img = root + ver+'/graph/CompareV0V2.png'
    # img = root + ver+'/graph/Imp.png'
    fig, ax = plt.subplots(3, sharex=True, figsize=(20, 10))
    # addPlot(ax, 0, sensor_v0, 'AliceMotion')
    # addPlot(ax, 1, sensor_v0, 'MartinMotion')
    # addPlot(ax, 4, sensor_v0, 'DoorBell')
    # addPlot(ax, 3, pro_V0S2, 'Program V0S2')

    addPlot(ax, 0, sensor_v0, 'TimeOfDay')
    addPlot(ax, 1, sensor_v0, 'Storm')
    addPlot(ax, 2, sensor_v0, 'Shutter')
    # addPlot(ax, 2, sensor_v1, 'Shutter')
    addPlot(ax, 2, sensor_v2, 'Shutter')
    
    # addPlot(ax, 4, pro_Imp, 'Program Imp')
    # addPlot(ax, 3, pro_V0S2, 'Program V0S2')
    # addPlot(ax, 0, pro_V2, 'Program V1')
    # addPlot(ax, 1, pro_V1, 'Program V1')
    # addPlot(ax, 3, pro_V0, 'Program V0')
    fig.savefig(img)
    

def addPlot(ax, j,file, ylab):
    x = []
    y = []
    if 'Program' in ylab:
        x, y = getPro(file)
    else:    
        x, y = getElem(file, ylab)
    print(ylab)
    print(y)
    ax[j].step(x,y, '-', where="post")
    ax[j].set_ylabel(ylab)
    ax[j].set_ylim([-0.1,1.1])
    plt.xlabel('timestamp')
    # plt.title('Property S2')
    plt.xticks(x, rotation=25)
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S.%f')
    ax[j].xaxis.set_major_formatter(xfmt)
    # plt.close()

def getElem(file, elem):
    T_start = getConfig(DURATION, startTime)
    T_stop = getConfig(DURATION, stopTime)
    x = []
    y = []
    with open(file,'r') as csvfile:
        plots = csv.reader(csvfile, delimiter=';')
        flag = False
        for row in plots: 
            if elem in row: 
                x.append(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f'))
                y.append(int(row[2]))
                flag = True
        if flag == False:
            x.append(datetime.datetime.strptime(T_start, '%Y-%m-%d %H:%M:%S.%f'))
            y.append(0)
            x.append(datetime.datetime.strptime(T_stop, '%Y-%m-%d %H:%M:%S.%f'))
            y.append(0)
            
    return x, y

def getPro(file):
    T_start = getConfig(DURATION, startTime)
    T_stop = getConfig(DURATION, stopTime)
    x = []
    y = []
    with open(file) as csvfile:
        plots = csv.reader(csvfile, delimiter=';')
        data = list(plots)
        row_count = len(data)
        if row_count == 0:
            x.append(datetime.datetime.strptime(T_start, '%Y-%m-%d %H:%M:%S.%f'))
            y.append(0)
            x.append(datetime.datetime.strptime(T_stop, '%Y-%m-%d %H:%M:%S.%f'))
            y.append(0)
        else:
            for row in data:
                if ('1970-01-01' in row[0]): 
                    x.append(datetime.datetime.strptime(T_start, '%Y-%m-%d %H:%M:%S.%f'))
                    y.append(1)
                else:
                    x.append(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f'))
                    y.append(int(row[2]))
    return x, y
  
def Str2Num(state_):
    v = ''
    if state_ =='OFF': v = '1'
    elif state_ == 'ON': v = '0'
    elif state_ == 'OPEN': v = '0'
    elif state_ == 'CLOSED': v = '1'
    elif state_ == 'DAY': v = '1'
    elif state_ == 'NIGHT': v = '0'    
    else: v = state_
    return v
#  From suite-s to property.csv
def getPropertyResult(result):
    al = getConfig(ALLEN, suite)
    ver = getConfig(DURATION, Version)
    p = 'test'
    time_ = 't'
    r = '1'
    out_f = al+ver+'/out/suite.csv' 
    for f in glob.glob(os.path.join(al+ver+'/out/', '*')):
        line = open(f,'r').readlines()
        i=0     
        if '#' not in line[0]:
            print('Format error')
            return  
        while i < len(line):  
            if '#' in line[i]:
                try:
                    p = line[i].split(' ')[2]
                except Exception as e:
                    print('DEBUG1')
                    print(e)
                out_f = al+ver+'/'+result+'/'+p+'.csv'
                with open(os.path.join(out_f), 'w'):
                    pass
            if '#' not in line[i]:    
                try:
                    time_ = line[i].split(';')[0].replace('T', ' ')
                    r = line[i].split(';')[2]
                except Exception as e:
                    print("DEBUG2")                     
                    print(line[i])
                writeFile(out_f, time_+';'+p+';'+r)
            i = i+1        

def main():
    # getPropertyResult('result_V0')
    # graphActuator('common.csv')
    manualGraph()

if __name__ == "__main__":
    main()