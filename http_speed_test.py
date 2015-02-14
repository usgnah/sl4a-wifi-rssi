#-*-coding:utf8;-*-
#qpy:console
#qpy:2

### script to check http download speed
### Author: hangsu@gmail.com

import androidhelper
import time,os,sys
import threading
import Queue
import urllib2

class HttpDownload(threading.Thread):
    def __init__(self,droid):    
        super(HttpDownload, self).__init__() 
        self.evnt = threading.Event()
        self.q = Queue.Queue()
        self.isRun = True
        self.droid = droid
        self.state = "not_pause"
        FILEPATH = os.path.join("/sdcard",'tputlog.txt')
        print FILEPATH         
        self.fd = open(FILEPATH,'w')           
    def run(self):
        while self.isRun:
            url = "http://speedtest.fremont.linode.com/100MB-fremont.bin"    
            #url = "http://download.thinkbroadband.com/1GB.zip"
            try:
                u = urllib2.urlopen(url)    
            except:
                print "cannot open url"
                time.sleep(1)
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            print "Start Downloading - Bytes: %s" % (file_size)
            self.startTime = time.time()
            prevTime = self.startTime
            file_size_dl = 0
            prev_file_size_dl = 0
            block_sz = 8192 * 2            
            while True:
                if not self.q.empty():
                    inq = self.q.get()   
                    if inq == "stop":
                        self.isRun = False
                        self.fd.close()
                        break 
                    elif inq == "p":
                        self.state = "pause"
                        print "pause"                        
                    elif inq == "r":
                        self.state = "not_pause"                       
                        print "resume"
                if self.state == "pause":
                    time.sleep(1)                    
                else:        
                    buffer = u.read(block_sz)
                    if not buffer:
                        break
                    file_size_dl += len(buffer)        
                    cTime = time.time()
                    if cTime - prevTime < 1:
                        continue
                    else:  
                        Atput = file_size_dl *8.0 / (cTime-self.startTime) / 1e6
                        Itput = (file_size_dl - prev_file_size_dl) * 8.0 / (time.time()-prevTime) / 1e6
                        wifiInfo = self.droid.wifiGetConnectionInfo()
                        wifiInfoDict = wifiInfo[1]
                        rssi = wifiInfoDict['rssi']                    
                        status = "%s [%3.2f%%] %3.2f %3.2f %s" % (time.strftime('%X'), file_size_dl * 100. / file_size, Itput, Atput, rssi)                    
                        status = status + chr(8)*(len(status)+1)
                        print status
                        self.fd.write(status+'\n')
                        prevTime = cTime
                        prev_file_size_dl = file_size_dl                    

if __name__ == '__main__':  
    Droid = androidhelper.Android()
    
    d1 = HttpDownload(Droid)
    d1.start()
    
    while True:
        a = raw_input()
        d1.q.put(a)
        if a == "stop":            
            break
