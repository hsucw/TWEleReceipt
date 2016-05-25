import socket
import json
import sys
import Queue
import logging as log
import thread

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
    
        
        

    def AssignTask(self,number,date,direction,distance,(clientsock,addr)):
        success = 0
        datemodify = 0
        db = DBManager()
        try:
            clientsock.sendall("{} {} {} {}".format(number,date,str(direction),str(distance)))
            data = clientsock.recv(4096)
            print "original receive : {}".format(data)
            try:
                receipt = json.loads(data)
            except:
                print data
                return -1,0
            log.debug("receive length : "+str(len(receipt)))
            log.debug("receive : ")
            print receipt
            if len(receipt) >= distance-5:
                success = 1
            if receipt.get(number[0:2]+str(int(number[2:])+distance-1),date)[0] != date:
                datemodify = direction
            db.StoreData(receipt)
        except socket.error as e:
            
            print "shit happened {}".format(e)    
        return success,datemodify


    def CrawlerHandler(self,clientsock,addr):
        
        while not self.q.empty():
            wow = self.q.get()
            self.current.put(wow)
            print "Assign Task:{} {} {} {}".format(wow[0],wow[1],wow[2],wow[3])
            s,d = self.AssignTask(wow[0],wow[1],wow[2],wow[3],(clientsock,addr))
            
            if s:
                print "Success!!Add new Task~"
                self.q.put( (wow[0][:2] + str(int(wow[0][2:])+wow[3]*wow[2]),TimeConvert(wow[1],d),wow[2],wow[3]) )
            else:
                print "Fail!!Reach the end!!"
            self.current.get()
        else:
            
            print "=====All done====="

    def Run(self):
        
        data = self.taskdbmanager.GetData()
        #self.taskdbmanager.Clear()                    dont clear for testing
        for i in data:
            i = (i[0].encode('ascii','ignore'),i[1].encode('ascii','ignore'),i[2],i[3])
            self.q.put(i)
        print '!!!!!!!!!!!!!!'
        try:
            serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            serversock.bind(server_addr)
            serversock.listen(5)
            while 1:
                print 'waiting for connection...'
                clientsock, addr = serversock.accept()
                print '...connected from:', addr
                
                thread.start_new_thread(self.CrawlerHandler,(clientsock,addr) )
        except  KeyboardInterrupt:
            L = []
            while not self.current.empty():
                L.append(self.current.get())
            while not self.q.empty():
                L.append(self.q.get())
            print L
            #self.taskdbmanager.Clear()               dont clear for testing
            self.taskdbmanager.StoreAll(L)
            print "=====Task Saved====="

if __name__ == '__main__':
    #log.basicConfig(level = log.DEBUG)
    T = TaskManager()

    T.Run()

