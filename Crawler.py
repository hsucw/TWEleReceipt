#!/usr/local/bin python
from Connector import Connector
from DBManager import DBManager
import logging as log
import sys
import re
import thread

class Crawler(object):
    def __init__(self):
        self.tasks = []
        self.conn = Connector()
        self.dbmgr = DBManager()
        

    def getTasks(self, task):
        """ getTasks """
        pass
    
    def Query(self):
        
        c = Connector()
        #log.info('Connect to {}'.format(c.domain))

        res = None
        while res is None:
            c.imgRslr.reportFail(c.imgCode, c.imgSHA)
            c.resolveImg()
            log.info('[{}]Get Image {}:{}'.format(c.res.reason, c.tmp_file, c.imgCode))
            log.info('{} and {}'.format(self.id_tag + str(self.id_num) , str(self.yy) + '/' + str(self.mm).zfill(2) + '/' + str(self.dd).zfill(2)))
            c.setPostData( self.id_tag + str(self.id_num) , str(self.yy) + '/' + str(self.mm).zfill(2) + '/' + str(self.dd).zfill(2) )
            c.postForm( c.postPath )
            log.info('[{} {}]Post data'.format(c.res.status,c.res.reason))
            res = c.getInfo()

            with open("out.html" , "w") as outFd:
                outFd.write(c.body)

        if not bool(c.info):
            print "No Record"
            return False
        print("===[Query Result]===")
        for k,r in c.info.iteritems():
            print k+":\t\t"+r
            if k == 'id':
                res_id = r
            if k == 'money':
                res_money = r
            if k == 'date':
                res_date = r
        with open('data.txt' , 'a') as outFd:
            outFd.write(res_id + '\t\t')
            outFd.write(res_date + '\t\t')
            outFd.write(res_money + '\n')
        return True
    def NextDate(self):
        if self.yy%4 == 1 :
            if self.mm in [1,3,5,7,8,10,12] :
                if self.dd==31 and self.mm==12: 
                    self.dd = 1
                    self.mm = 1
                    self.yy += 1
                elif self.dd==31 and self.mm!=12 :
                    self.dd =1
                    self.mm += 1
                else :
                    self.dd += 1

            elif self.mm == 2 :
                if self.dd==29 :
                    self.dd =1
                    self.mm += 1
                else :
                    self.dd += 1 

            else:
                if self.dd == 30 :
                    self.dd =1
                    self.mm += 1
                else :
                    self.dd += 1 
        else:
            if self.mm in [1,3,5,7,8,10,12] :
                if self.dd==31 and self.mm==12 :
                    self.dd = 1
                    self.mm = 1
                    self.yy += 1
                elif self.dd==31 and self.mm!=12 :
                    self.dd =1
                    self.mm += 1
                else :
                    self.dd += 1

            elif self.mm == 2 :
                if self.dd==29 :
                    self.dd =1
                    self.mm += 1
                else :
                    self.dd += 1 

            else:
                if self.dd==30 :
                    self.dd =1
                    self.mm += 1
                else :
                    self.dd += 1

    def Crawl(self , num , date):
        self.rec_id = num
        self.rec_date = date
        
        self.id_tag = self.rec_id[0:2] 
        self.id_num = int(self.rec_id[2:10])
        self.yy = int(self.rec_date[0:3])
        self.mm = int(self.rec_date[4:6])
        self.dd = int(self.rec_date[7:9])
        cont = 0

        while True:
            success = self.Query()
            if success is True :
                self.id_num += 1
                cont = 0
            elif  (success is False) and (cont==0):
                self.NextDate()
                cont+=1
            else :
            	   break



if __name__ == '__main__':
    """ give a guess for id & date"""
    log.basicConfig(level=log.INFO)

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

    

    c = Crawler()
    c.Crawl(sys.argv[1],sys.argv[2])