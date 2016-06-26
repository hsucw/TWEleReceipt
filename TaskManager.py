import socket
import json
import sys
import Queue
import logging as log
import thread
import time
import random

from TimeConvert import TimeConvert
from DBManager import DBManager
from TaskDBManager import TaskDBManager

server_addr = ('127.0.0.1',5555)
log.basicConfig(level=log.DEBUG)

class TaskManager(object):
    def __init__(self):
        self.dbmanager = DBManager()
        self.taskdbmanager = TaskDBManager()
        self.current = Queue.Queue()
        self.q = Queue.Queue()
        self.guess = Queue.Queue()
        self.guess2 = Queue.Queue()
        
        

    def AssignTask(self,number,date,direction,distance,(clientsock,addr)):
        success = 0
        datemodify = 0
        db = DBManager()
        try:
            clientsock.sendall("{} {} {} {}".format(number,date,str(direction),str(distance)))
            data = clientsock.recv(65536)
            
            try:
                receipt = json.loads(data)
            except:
                print data
                return -1,0
            
            if len(receipt) >= distance-5:
                success = 1
            
            if receipt.get(number[0:2]+str(int(number[2:])+distance*direction-1).zfill(8),[date])[0] != date:
                datemodify = direction
            while True:
                try:
                    db.StoreData(receipt)
                    break;
                except :
                    print 'store data fail'
                    time.sleep(random.randint(1,60))
            
        except socket.error as e:
            
            print "shit happened {}".format(e)
            time.sleep(60)    
        return success,datemodify


    def CrawlerHandler(self,clientsock,addr):
        db = DBManager()
        while True:

            

            if not self.q.empty():
                wow = self.q.get()
                if db.Findid(wow[0]) and db.Findid(wow[0][:2] + str(int(wow[0][2:])+wow[2]).zfill(8)) and db.Findid(wow[0][:2] + str(int(wow[0][2:])+wow[2]*2).zfill(8)):
                    log.debug("data is already found")
                    continue
                self.current.put(wow)
                print "Assign Task:{} {} {} {}".format(wow[0],wow[1],wow[2],wow[3])
                s,d = self.AssignTask(wow[0],wow[1],wow[2],wow[3],(clientsock,addr))
                
                if s:
                    print "Success!!Add new Task~"
                    log.debug('add new Task : ' + TimeConvert(wow[1],d) )
                    self.q.put( (wow[0][:2] + str(int(wow[0][2:])+wow[3]*wow[2]).zfill(8),TimeConvert(wow[1],d),wow[2],wow[3]) )
                else:
                    print "Reach end!!Add guess data!!"             
                    self.guess.put( (wow[0][:2] + str(int(wow[0][2:])+wow[3]*wow[2]*5).zfill(8),TimeConvert(wow[1],0),wow[2],wow[3],14,20) )
                    
                self.current.get()
            elif not self.guess.empty():
                wow = self.guess.get()
                if db.Findid(wow[0]) and db.Findid(wow[0][:2] + str(int(wow[0][2:])+wow[2]).zfill(8)) and db.Findid(wow[0][:2] + str(int(wow[0][2:])+wow[2]*2).zfill(8)):
                    log.debug("data is already found")
                    continue
                print "Assign Task:{} {} {} {} from guess".format(wow[0],wow[1],wow[2],wow[3])
                s,d = self.AssignTask(wow[0],wow[1],wow[2],wow[3],(clientsock,addr))
                
                if s:
                    print "Success!!Add new Task~"
                    log.debug('add new Task : ' + TimeConvert(wow[1],d) )
                    self.q.put( (wow[0][:2] + str(int(wow[0][2:])+wow[3]*wow[2]).zfill(8),TimeConvert(wow[1],d),wow[2],wow[3]) )
                    self.q.put( (wow[0], wow[1], wow[2]*(-1), wow[3]) )
                else:
                    print "guess fail"
                    if wow[5]>0: 
                        
                        if wow[4]==14:
                            self.guess.put( (wow[0][:2] + str(int(wow[0][2:])+wow[3]*wow[2]*5).zfill(8),TimeConvert(wow[1],0),wow[2],wow[3],14,wow[5]-1) )
                            self.guess.put( (wow[0] ,TimeConvert(wow[1],1),wow[2],wow[3],wow[4]-1,wow[5]) )
                            self.guess.put( (wow[0] ,TimeConvert(wow[1],-1),wow[2],wow[3],wow[4]-2,wow[5]) )
                        elif (wow[4]%2) == 1 and wow[4]>=6:
                            self.guess.put( (wow[0] ,TimeConvert(wow[1],1),wow[2],wow[3],wow[4]-2,wow[5]) )
                        elif (wow[4]%2) == 0 and wow[4]>=6:
                            self.guess.put( (wow[0] ,TimeConvert(wow[1],-1),wow[2],wow[3],wow[4]-2,wow[5]) )
                        elif (wow[4]%2) == 1 and wow[4]<6:
                            self.guess2.put( (wow[0] ,TimeConvert(wow[1],1),wow[2],wow[3],wow[4]-2,wow[5]) )
                        elif (wow[4]%2) == 0 and wow[4]<6:
                            self.guess2.put( (wow[0] ,TimeConvert(wow[1],-1),wow[2],wow[3],wow[4]-2,wow[5]) )
                        else :
                            log.error("guess data : {},{},{},{},{},{},{} should not in guess queue".format(wow[0],wow[1],wow[2],wow[3],wow[4],wow[5]))
                    else:
                        self.guess2.put( (wow[0][:2] + str(int(wow[0][2:])+wow[3]*wow[2]*5).zfill(8),TimeConvert(wow[1],0),wow[2],wow[3],14,wow[5]-1) )
            elif not self.guess2.empty():
                wow = self.guess2.get()
                if db.Findid(wow[0]) and db.Findid(wow[0][:2] + str(int(wow[0][2:])+wow[2]).zfill(8)) and db.Findid(wow[0][:2] + str(int(wow[0][2:])+wow[2]*2).zfill(8)):
                    log.debug("data is already found")
                    continue
                print "Assign Task:{} {} {} {} from guess2".format(wow[0],wow[1],wow[2],wow[3])
                s,d = self.AssignTask(wow[0],wow[1],wow[2],wow[3],(clientsock,addr))
                
                if s:
                    print "Success!!Add new Task~"
                    log.debug('add new Task : ' + TimeConvert(wow[1],d) )
                    self.q.put( (wow[0][:2] + str(int(wow[0][2:])+wow[3]*wow[2]).zfill(8),TimeConvert(wow[1],d),wow[2],wow[3]) )
                    self.q.put( (wow[0], wow[1], wow[2]*(-1), wow[3]) )
                else:
                    print "guess fail"
                    if wow[5]>0: 
                        
                        if (wow[4]%2) == 1 and wow[4]>=0:
                            self.guess2.put( (wow[0] ,TimeConvert(wow[1],1),wow[2],wow[3],wow[4]-2,wow[5]) )
                            
                        elif (wow[4]%2) == 0 and wow[4]>=0:
                            self.guess2.put( (wow[0] ,TimeConvert(wow[1],-1),wow[2],wow[3],wow[4]-2,wow[5]) )
                        
                        else :
                            log.info("date guess finished")
                    else:
                        if wow[4]==14:
                            self.guess2.put( (wow[0][:2] + str(int(wow[0][2:])+wow[3]*wow[2]*5).zfill(8),TimeConvert(wow[1],0),wow[2],wow[3],14,wow[5]-1) )
                            self.guess2.put( (wow[0] ,TimeConvert(wow[1],1),wow[2],wow[3],wow[4]-1,wow[5]) )
                            self.guess2.put( (wow[0] ,TimeConvert(wow[1],-1),wow[2],wow[3],wow[4]-2,wow[5]) )
                        elif (wow[4]%2) == 1 and wow[4]>=0:
                            self.guess2.put( (wow[0] ,TimeConvert(wow[1],1),wow[2],wow[3],wow[4]-2,wow[5]) )
                            
                        elif (wow[4]%2) == 0 and wow[4]>=0:
                            self.guess2.put( (wow[0] ,TimeConvert(wow[1],-1),wow[2],wow[3],wow[4]-2,wow[5]) )
                        
                        else :
                            log.info("date guess finished")
            else:
                print "queue is empty"
                time.sleep(20)
            # delete after testing
            with open('record.txt' , 'a') as outFd:
                outFd.write(wow[0] + '\t')
                outFd.write(wow[1] + '\t')
                outFd.write(str(wow[2]) + '\t')
                outFd.write(str(wow[3]) + '\n')
            # delete after testing
                
    def CheckTaskDB(self):
        task_db = TaskDBManager()
        db = DBManager()
        while True:
            time.sleep(60)
            data = task_db.GetData()
            task_db.Clear()
            for i in data:
                i = (i[0].encode('ascii','ignore'),i[1].encode('ascii','ignore'),i[2],i[3])
                if not db.Findid(i[0]):
                    self.q.put(i)
    def Run(self):
        
        data = self.taskdbmanager.GetData()
        self.taskdbmanager.Clear()                   
        for i in data:
            i = (i[0].encode('ascii','ignore'),i[1].encode('ascii','ignore'),i[2],i[3])
            self.q.put(i)
        print '!!!!!!!!!!!!!!'
        thread.start_new_thread(self.CheckTaskDB,() )
        try:
            serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            serversock.bind(server_addr)
            serversock.listen(5)
            while 1:
                print 'waiting for connection...'
                clientsock, addr = serversock.accept()
                print '...connected from:', addr
                
                thread.start_new_thread(self.CrawlerHandler,(clientsock,addr) )
        except  :
            L = []
            while not self.current.empty():
                L.append(self.current.get())
            while not self.q.empty():
                L.append(self.q.get())
            print L
            
            self.taskdbmanager.StoreAll(L)
            print "=====Task Saved====="

if __name__ == '__main__':
    #log.basicConfig(level = log.DEBUG)
    T = TaskManager()

    T.Run()

