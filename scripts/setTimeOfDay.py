import time
import datetime
from openhab import openHAB
import requests
import logging

base_url = 'http://localhost:8080/rest'
openhab = openHAB(base_url)
log_file = '/Users/huongta/Home/Internship/openhab/openhab-2/userdata/logs/logTime.log'


def setTime():
    i=0
    while i < 10:
        sendCommand('vTimeOfDay', 'MORNING')
        writeTimeLog('MORNING')
        time.sleep(10)
        sendCommand('vTimeOfDay', 'DAY')
        writeTimeLog('DAY')
        time.sleep(10)
        sendCommand('vTimeOfDay', 'AFTERNOON')
        writeTimeLog('AFTERNOON')
        time.sleep(10)
        sendCommand('vTimeOfDay', 'EVENING')
        writeTimeLog('EVENING')
        time.sleep(10)
        sendCommand('vTimeOfDay', 'NIGHT')
        writeTimeLog('NIGHT')
        time.sleep(10)
        sendCommand('vTimeOfDay', 'BED')
        writeTimeLog('BED')
        time.sleep(10)
        i = i+1
        print(i)
    print('Finish')
   
def sendCommand(item, value):
    requests.put(base_url+'/items/'+item+'/state', data=value)

def writeTimeLog(item):
    logging.basicConfig(filename=log_file, filemode='a', format='%(asctime)s [%(levelname)s ] [Time_Of_Day] - %(message)s', level=logging.INFO)
    logging.info(item)

if __name__ == "__main__":
    setTime()