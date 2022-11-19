import csv
import pandas as pd
import time
import datetime
from datetime import timedelta  
from openhab import openHAB
import requests
import logging
from configparser import ConfigParser  

base_url = 'http://0.0.0.0:8080/rest'
# base_url = 'http://127.0.0.1:8090/rest'
openhab = openHAB(base_url)
ROOT_report = 'ROOT_report'
ROOT_real = 'ROOT_real'
ROOT_test = 'ROOT_test'
FILE_DIR = 'FILE_DIR'
DURATION = 'DURATION'
INFO = ' [INFO ]'

# fetch all items
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
        dir_ = root_+item+'_test_'+ver+'.'+type_
    else: dir_ = root_+item+'_'+ver+'.'+type_
    return dir_

def getData(csv_file):
    count = 1
    df = pd.read_csv(csv_file)
    count_row = df.shape[0]
    for i in range(count_row):
        item = openhab.get_item(df.iloc[i,0])
        timeO = df.iloc[i,1]
        value = df.iloc[i,2]
        # replays(item, value)
        # writeTimeLog(timeO, item.name)
        time.sleep(10)
        print(count)
        count = count +1

def writeTimeLog(timeO, item):
    s = timeO
    s = s[:23]
    s = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')
    log_CMD = getConfig(FILE_DIR, 'log_CMD')
    logging.basicConfig(filename=log_CMD, filemode='a', format='%(asctime)s [%(levelname)s ] [------------OriginalTime------------] - %(message)s', level=logging.INFO)
    logging.info('Input value of ' + item + ' from the time: ' + datetime.datetime.strftime(s, '%Y-%m-%d %H:%M:%S.%f'))

def replays(item, value, timestamp):
    simclock = openhab.get_item('SimClock')
    simclock.command(timestamp)
    # item.command(value)
    if value =='ON' or value == 'OFF' or value == 'DAY' or value == 'NIGHT':
        item.command(value)
    else: 
        item.command(int(value))
        # sendCommand(item, str(value))

def sendCommand(item, value):
    requests.put(base_url+'/items/'+item+'/state', data=value)

def readLog(cfile):
    sim_clock = getConfig(DURATION, 'sim_clock')
    startTime = getConfig(DURATION, 'startTime')
    stopTime = getConfig(DURATION, 'stopTime')
    print(startTime)
    print(stopTime)
    with open (cfile, 'rt') as f:
        line = f.readlines()
        print(len(line))
        i=0
        count = 0
        while i < len(line):        
            if '[INFO ]' in line[i]:
                timeLog = getTime(line[i])
                while startTime < timeLog < stopTime:   
                    if 'Trigger' in line[i]:
                        timeLog, item, state = getArg(line[i])
                        replays(openhab.get_item(item), state, timeLog)
                        writeTimeLog(timeLog, item)
                        count = count +1
                        print(count)
                        time.sleep(int(sim_clock))
                    i=i+1
                    timeLog = getTime(line[i])
                if timeLog > stopTime:
                    # print(timeLog)
                    i = len(line)
            i=i+1

def getTime(line):
    getT = []
    try:
        getT = line.split(' [')
    except Exception as e:
        print(e)
    return getT[0]

def getArg(line):
    parseValue = parseLine(line)
    time = parseValue[0]
    item = parseValue[1]
    state = parseValue[2]
    return time, item, state
# Analysis line in INFO.log file
def parseLine(line):
    getV = []
    try:
        temp_value = line.split(' - ')
        # Get Time
        getV.append(line.split(INFO)[0]) 
        # Get Value
        value = temp_value[len(temp_value)-1].strip()
        temp_value = value.split(' changed to ')
        # Get item
        getV.append(temp_value[0])
        # Get state
        getV.append(temp_value[1])
    except Exception as e:
        print(e)
    return getV

def initialState():
    sendCommand('AliceMotion', 'OFF')
    sendCommand('Storm', 'OFF')
    sendCommand('Power', 'OFF')
    sendCommand('MartinMotion', 'OFF')
    sendCommand('vTimeOfDay', 'DAY')
    sendCommand('Door', 'CLOSED')
    time.sleep(3)
    print('Finish Set initial state')

if __name__ == "__main__":
    initialState()
    openHABlog = getConfig('FILE_DIR', 'openHABlog')
    readLog(openHABlog)
    # sendCommand('vTimeOfDay', 'DAY')
    print("Finish")
