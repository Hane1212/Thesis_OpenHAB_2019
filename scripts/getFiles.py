import csv
import os, glob
import pandas as pd
from configparser import ConfigParser  

csv_folder = '/Users/huongta/Home/Internship/openhab/openHAB_test/openhab/userdata/logs/20190516_093500/State_test'
filec = '/Users/huongta/Home/Internship/openhab/openHAB_test/openhab/userdata/logs/20190516_093500/State_test/common.csv'
file_out = '/Users/huongta/Home/Internship/openhab/openhab-2/userdata/logs/20190524_090000/common.csv'
file_out_test = '/Users/huongta/Home/Internship/openhab/openHAB_test/openhab/userdata/logs/20190524_090000/common.csv'

infileF = '/Users/huongta/Home/Internship/openhab/openhab-2/userdata/logs/openhab.log'
infoFileF = '/Users/huongta/Home/Internship/openhab/openhab-2/userdata/logs/INFO.log'
infileS = '/Users/huongta/Home/Internship/openhab/openhab-2/userdata/logs/10/openhab.log'
infoFileS = '/Users/huongta/Home/Internship/openhab/openhab-2/userdata/logs/10/INFO.log'


# def modifyFiles():
    #   for file in os.listdir(csv_folder):
    #       if file.endswith(".csv"):
    #           modifyFile(os.path.join(csv_folder, file))
# def modifyFile(file):
    #     df = pd.read_csv(file)
    #     df['time'] = df['time'].map(modifyTime)
    #     df.to_csv(file)
# def modifyTime(time):
    #     time = pd.Timestamp(time).strftime("%Y-%m-%d %H:%M:%S")
    #     return time    
important = []
phrase = '[INFO ]'
INFO = ' [INFO ]'
ROOT_report = 'ROOT_report'
ROOT_real = 'ROOT_real'
ROOT_test = 'ROOT_test'
FILE_DIR = 'FILE_DIR'
DURATION = 'DURATION'
Version = 'Version'
openHABlog = 'openHABlog'
openHABlog_test = 'openHABlog_test'
# Read information from config.ini file
def getConfig(tag, item):
    config = ConfigParser() 
    config.read('config.ini') 
    temp_ = config.get(tag, item)
    return temp_

class Line:
    def getTime(self,line):
        getT = []
        try:
            getT = line.split(' [')
        except Exception as e:
            print(e)
        return getT[0]

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

def getStateSystem(file_in, file_out, start, stop):
    log = getConfig(FILE_DIR, file_in)
    startTime = getConfig(DURATION, start)
    stopTime = getConfig(DURATION, stop)
    with open (log, 'rt') as f:
        line = f.readlines()
        print(len(line))
        i=0     
        while i < len(line):  
            l = Line()
            timeLog = l.getTime(line[i])   
            while startTime < timeLog < stopTime:
                if 'STATE' in line[i]: 
                    v = l.getValue(line[i])
                    logCSV(file_out , timeLog, v.split(' changed to ')[0], v.split(' changed to ')[1])  
                i = i+1
                timeLog = l.getTime(line[i]) 
                if timeLog > stopTime:
                    i = len(line)
            i=i+1

def logCSV(file_o, timestamp, item, result):
    with open(file_o, 'a') as fp:
        result = Str2Num(result)
        fp.write(str(timestamp)+';'+ str(item)+';'+str(result)+'\n')

def Str2Num(state_):
    v = ''
    if state_ =='OFF': v = '1'
    elif state_ == 'ON': v = '0'
    elif state_ == 'OPEN': v = '0'
    elif state_ == 'CLOSED': v = '1'
    else: v = state_
    return v

# Get time in log line
def getTime(line):
    getT = []
    try:
        getT = line.split(' [')
    except Exception as e:
        print(e)
    return getT[0]

def getCommonFile():
    pieces = []
    for file in os.listdir(csv_folder):
        if file.endswith(".csv"):
            s = pd.read_csv(os.path.join(csv_folder, file)) # your directory
            pieces.append(s)
    newcsv = pd.concat(pieces) # this will yield multiple columns
    newcsv['time'] = pd.to_datetime(newcsv['time'])
    newcsv = newcsv.sort_values(by='time', ascending=True)
    newcsv.to_csv(filec, index=False)

def readOlog(file):
    with open(file) as f:
        f = f.readlines()
        for line in f:
            if phrase in line:
                important.append(line)

def writeIlog(file):
    with open(file, 'a') as ilog:
        for i in important:
            ilog.write(i)

def main():
    # getCommonFile()
    getStateSystem(openHABlog, file_out ,'startTime', 'stopTime')
    getStateSystem(openHABlog_test, file_out_test ,'startTime_test', 'stopTime_test')

if __name__ == "__main__":
    main()
    # # modifyFiles()
    # # Filter log with [INFO ]
    # readOlog(infileF)
    # readOlog(infileS)
    # Write [INFO ] log to file
    # writeIlog(infoFileF)
    # writeIlog(infoFileS)
    # Merge all csv file
    
 
