#-*-coding:utf8;-*-
#qpy:console
#qpy:2

### script to log rssi bssid roaming
### Author: hangsu@gmail.com

import androidhelper
import time,os,sys
import threading
import Queue

def Freq2Ch(freq):
    if freq < 5000 and freq > 2000:
        baseFreq = 2412
        baseCh = 1
        freqBw = 5        
    elif freq < 6000 and freq >= 5000:
        baseFreq = 5180
        baseCh = 36
        freqBw = 5
    return int((freq - baseFreq) / freqBw + baseCh)


def GetChannel(myBssid):
    scanInfo = Droid.wifiGetScanResults()
    myFreq = -1
    myCh = -1
    for item in scanInfo[1]:
      if myBssid.find(item['bssid']) !=-1:        
        myFreq = item['frequency']
        myCh = Freq2Ch(myFreq)
        break
    return myFreq,myCh

class LogLoop(threading.Thread):
    def __init__(self,droid):
        super(LogLoop, self).__init__()         
        self.q = Queue.Queue()
        FILEPATH = os.path.join("/sdcard",'rssilog.txt')
        print FILEPATH         
        self.fd = open(FILEPATH,'w')   
        self.myCurrentBssid = 'dummy'        
        self.droid = droid
        self.lines = 0
        self.__MAXLINE = 1000000
    def run(self):
        ifPrintScreen = 1
        while True:
            if not self.q.empty():
                inq = self.q.get()         
                self.fd.write(inq+'\n')                                
                if inq == "stop":
                    self.fd.close()
                    break  
                elif inq == "scan":                    
                    myFreq, myCh = GetChannel(self.myCurrentBssid)
                    print myFreq  
                elif inq == "p":                    
                    ifPrintScreen = (ifPrintScreen + 1 ) % 2                     
            wifiInfo = self.droid.wifiGetConnectionInfo()
            wifiInfoDict = wifiInfo[1]
            myBssid = wifiInfoDict['bssid']        
            if myBssid != self.myCurrentBssid:
                ### means roaming        
                myFreq, myCh = GetChannel(myBssid)
                # if myFreq == -1:
                    # scanInfo = self.droid.wifiGetScanResults()
                    # self.fd.write(str(scanInfo[1]))
                    # print wifiInfo
                self.droid.vibrate()
                self.droid.makeToast("roam " + myBssid)
                self.myCurrentBssid = myBssid
            outStr = "%s %s %d (Ch %d) %s %s" % (time.strftime('%X'), self.myCurrentBssid, myFreq, myCh, wifiInfoDict['rssi'], wifiInfoDict['link_speed']    )
            if ifPrintScreen:
                print outStr     
            self.fd.write(outStr+'\n')                                
            self.lines += 1
            if self.lines >= self.__MAXLINE:   # in case the log file is too big. reset it
                self.fd.seek(0)
                self.lines =0  
            time.sleep(2)

if __name__ == '__main__':  
    Droid = androidhelper.Android()
    #Droid.startLocating()
    t1 =  LogLoop(Droid)
    t1.start()
    
    while True:
        a = raw_input()
        t1.q.put(a)        
        if a == "stop":
            break
