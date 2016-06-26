#!/usr/local/bin python
from Connector import Connector
from DBManager import DBManager
from TimeConvert import TimeConvert

import socket
import json
import logging as log
import sys
import re
import thread

class Crawler(object):
    def __init__(self):
        self.tasks = []
        self.conn = Connector()
        self.dbmgr = DBManager()
        self.c = Connector()
        self.data = ""
    def getTasks(self, task):
        """ getTasks """
        pass
    
    def Query(self):
        
        
        #log.info('Connect to {}'.format(c.domain))
        
        res = None
        while res is None:
            
            if not self.c.session_valid:
                self.c.imgRslr.reportFail(self.c.imgCode, self.c.imgSHA)
                self.c.resolveImg()
            log.info('[{}]Get Image {}:{}'.format(self.c.res.reason, self.c.tmp_file, self.c.imgCode))
            log.info('{} and {}'.format(self.id_tag + str(self.id_num).zfill(8) , self.rec_date))
            self.c.setPostData( self.id_tag + str(self.id_num).zfill(8) , self.rec_date )
            self.c.postForm( self.c.postPath )
            log.info('[{} {}]Post data'.format(self.c.res.status,self.c.res.reason))
            res = self.c.getInfo()

            with open("out.html" , "w") as outFd:
                outFd.write(self.c.body)

        if not bool(self.c.info):
            print "No Record"
            
            return False
        print("===[Query Result]===")

        for k,r in self.c.info.iteritems():
            print k+":\t\t"+r
            if k == 'id':
                res_id = r
            if k == 'money':
                res_money = r.replace(',','')
            if k == 'date':
                res_date = r
            if k == 'taxid':
                res_taxid = r
        
        self.receipt[res_id] = (res_date,res_money,res_taxid)
        return True

    def Crawl(self , num , date, direct, distance):
        self.rec_id = num
        self.rec_date = date
        
        self.id_tag = self.rec_id[0:2] 
        self.id_num = int(self.rec_id[2:10]) 
        self.receipt = {}
        cont = 0
        cont2 = 0
        
        while ( abs(int(self.id_num) - int(self.rec_id[2:10])) < distance):
            success = self.Query()
            if success is True :
                self.id_num += direct
                cont = 0
                cont2 = 0
            elif (success is False)  and (abs(cont2) < 3):
                print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                self.id_num += direct
                cont2 += direct
            elif  (success is False) and (cont==0) and (abs(cont2) >= 3):
                self.rec_date = TimeConvert(self.rec_date , direct)
                print "TimeConvert : "+ self.rec_date
                self.id_num -= cont2
                cont2 = 0
                cont+=1
            elif (success is False) and (cont!=0) and (abs(cont2) >= 3) :
                break
            else:
                log.error('main loop unusually break')
                sys.exit(1)
        return self.receipt


if __name__ == '__main__':
    """ give a guess for id & date"""
    log.basicConfig(level=log.INFO)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', 5555)
    print  'connecting to {} '.format(server_address)
    sock.connect(server_address)
    C = Crawler()
    try:
        while True:
            data = sock.recv(256)
            if data:
                _data = data.strip().split()
                if len(_data) != 4 or len(_data[0]) != 10 or len(_data[1]) != 9:
                    print "=====Wrong Format=====\nShould be(ReceiptId,Date,HowMany)\n{}".format(data)
                    sock.sendall("=====Wrong Format=====\nShould be(ReceiptId,Date,HowMany)\n")
                print "Recieve task : {} {} {} {}".format(_data[0],_data[1],_data[2],_data[3])
                receipt = C.Crawl(_data[0],_data[1],int(_data[2]),int(_data[3]))
                print "send : \n{}".format(receipt)
                sock.sendall(json.dumps(receipt))
                print "Task done!!"
    except KeyboardInterrupt:
        print >>sys.stderr, 'closing socket'
        sock.close()
    '''
    if len(sys.argv) != 3:
        print("Usage: python Crawler.py [ID] [DATE]")
        log.error("Unknown input")
        sys.exit(1)
    if (len(sys.argv[1]) != 10) or ( re.match( '[A-Z]{2}[0-9]{8}' , sys.argv[1] ) is None ):
        print("Wrong ID format (ex : AB12345678)")
        log.error("Unknown input")
        sys.exit(1)
    if ( len(sys.argv[1])  != 10 ) or ( re.match( '[0-9]{3}/[0-9]{2}/[0-9]{2}', sys.argv[2] ) is None ):
        print("Wrong DATE format (ex : 105/01/01)")
        log.error("Unknown input")
        sys.exit(1)

    

    c1 = Crawler()
    c1.Crawl(sys.argv[1],sys.argv[2],1,100)
    
    c2 = Crawler()
    c2.Crawl(sys.argv[1],sys.argv[2],-1,100)
    '''
