#!/usr/bin/env python
import httplib
import urllib
import logging as log
import time
import sys, traceback

from ImgResolver import ImgResolver
from HTMLDataResolver import HTMLDataResolver

log.basicConfig(level=log.INFO)

def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s (%s/%s)\r' % (bar, percents, '%', suffix, count, total))
    sys.stdout.flush()  # As suggested by Rom Ruben

class Connector(object):
    def __init__(self, domain="www.einvoice.nat.gov.tw"):
        self.domain = domain
        self.headers = {}
        self.postData = {}
        self.guess_total = 0
        self.guess_hit = 0

        self.errorCnt = 0

        self.imgCode = ""
        self.tmp_file = ""

        self.imgRslr = ImgResolver()
        self.imgRslr.loadPics()
        self.htmlRslr = HTMLDataResolver()
        self.cookie_str = ""
        self.conn = None

        self.publicAudit = '/APMEMBERVAN/PublicAudit/PublicAudit'
        self.postPath = '/APMEMBERVAN/PublicAudit/PublicAudit!queryInvoiceByCon'
        self.imgPath = '/APMEMBERVAN/PublicAudit/PublicAudit!generateImageCode'
        self.session_valid = False

    def setReqHeader(self):
        self.headers['Host'] = "www.einvoice.nat.gov.tw"
        self.headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:38.0) Gecko/20100101 Firefox/38.0"
        self.headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        self.headers['Accept-Language'] = "zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3"
        self.headers['Accept-Encoding'] = "gzip, deflate"
        self.headers['Referer']="https://www.einvoice.nat.gov.tw/APMEMBERVAN/PublicAudit/PublicAudit!queryInvoiceByCon"
        #self.headers['Referer'] = "https://www.einvoice.nat.gov.tw/APMEMBERVAN/PublicAudit/PublicAudit"
        #self.headers['Referer'] = "https://www.einvoice.nat.gov.tw/APMEMBERVAN/PublicAudit/PublicAudit?linkisNew=Y"
        self.headers['Connection'] = "keep-alive"
        self.headers['Content-Type'] = "application/x-www-form-urlencoded"
        self.headers['Cookie'] = self.cookie_str

    def __initConnections__(self, path):
        if self.conn is None:
            log.debug("Initial connection")
            self.conn = httplib.HTTPSConnection(self.domain, strict=False)
            self.setReqHeader()
        if self.conn is None:
            raise Exception

    def getPath(self, path="/"):
        self.body = None
        self.__initConnections__( path )
        try:
            self.conn.request("GET", path, headers=self.headers)
        except httplib.CannotSendRequest as e:
            log.error("CannotSendRequest")
            pass
        except Exception as e:
            log.error("{}".format(type(e).__name__))
            exit(1)
        #log.debug("GET:{} with {}".format(path, self.headers))

        self.res = None
        cnt = 0

        while True:
            try:
                time.sleep(1)
                self.res = self.conn.getresponse()

                if self.res is not None:
                    self.body = self.res.read()
                    break

            except Exception, e:

                if self.res is not None:
                    self.body = self.res.read()
                    break

                sys.stdout.write("\tretry {}\r".format(cnt))
                sys.stdout.flush()
                self.conn = None
                self.__initConnections__( path )
                self.conn.request("GET", path, headers=self.headers)

                continue



        for header in self.res.getheaders():
            if header[0] == 'set-cookie':
                self.cookie_str = header[1]
                break


        return self.res.status

    def resolveImg(self):
        self.imgCode = ""

        while self.imgCode is "":
            self.getPath(self.imgPath)
            self.imgCode = self.imgRslr.resolveImg(self.body)
        return self.imgCode

    def setPostData(self, num, date):
        self.postData['publicAuditVO.invoiceNumber'] = num
        self.postData['publicAuditVO.invoiceDate'] = date
        self.postData['publicAuditVO.customerIdentifier'] = ""
        self.postData['publicAuditVO.randomNumber'] = ""
        self.postData['txtQryImageCode'] = self.imgCode
        self.postData['CSRT'] = "11764538770937556216"


    def postForm(self, path):
        params = urllib.urlencode(self.postData)

        self.setReqHeader()
        self.conn.request("POST", path, params, headers=self.headers)
        #log.debug("POST:{} {} with {}".format(path, params, self.headers))
        self.res = None
        cnt = 0
        while True:
            #if cnt > 10:
            #    log.error("Max Redo Post")
            #    exit(1)
            try:
                time.sleep(1)
                self.res = self.conn.getresponse()
                if  self.res :
                    break
            except httplib.ResponseNotReady:
                if self.res is not None:
                    break
                cnt+=1
                sys.stdout.write("retry {}\r".format(cnt))
                sys.stdout.flush()

                self.conn.request("POST", path, params, headers=self.headers)
                continue
            except Exception as e:
                cnt+=1
                log.error("\tRedo All {} {}\r".format(cnt, type(e).__name__))
                self.resolveImg()
                self.setPostData(\
                        self.postData['publicAuditVO.invoiceNumber'],
                        self.postData['publicAuditVO.invoiceDate'])
                params = urllib.urlencode(self.postData)
                self.setReqHeader()
                self.conn.request("POST", path, params, headers=self.headers)
                continue

        self.body = self.res.read()
        return self.res.status

    def getInfo(self):

        self.info = self.htmlRslr.resolve(self.body)
        if (self.info is None):
            self.session_valid = False

        else:
            self.session_valid = True

        return self.info

    def guessRandNo(self):
        import json
        with open("guess_list.json","r") as f:
            guess_list = json.loads(f.readline())

        list_len = len(guess_list)
        guess_index = 0
        randNo = None
        total = 9999
        while randNo is None:

            if not self.session_valid:
                self.resolveImg()

            self.postData['publicAuditVO.randomNumber'] = guess_list[guess_index]
            self.postForm( self.postPath )

            if self.htmlRslr.findDetail(self.body):
                randNo = guess_list[guess_index]
                log.info("\nRandom Number Found "+randNo)
                break

            if guess_index < list_len:
                #log.info( "\rtrying rand no {}, total {}/{}".format(guess_list[guess_index],guess_index+1,list_len) )
                progress(guess_index, total, guess_list[guess_index])

                guess_index += 1
            else:
                log.debug("\nRandom Number Not Found")
                break



if __name__ == '__main__':
    """ give a guess for id & date"""
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger(" ")
    log.setLevel(20)
    #log.basicConfig(level=log.INFO)

    if len(sys.argv) != 3:
        log.info("Usage: python Connector.py [RECEIPT_ID] [DATE(YYYY/MM/DD)]")
        log.error("\tUnknown input\r")
        sys.exit(1)

    rec_id = sys.argv[1]
    rec_date = sys.argv[2]

    c = Connector()

    res = None
    while res is None:

        log.info('Get Image ')
        c.resolveImg()
        log.info('[{}]Resolve Image {}:{}'.format(c.res.reason, c.tmp_file, c.imgCode))
        c.setPostData(rec_id, rec_date)
        c.postForm(c.postPath)
        log.info('[{} {}]Post data'.format(c.res.status, c.res.reason))
        res = c.getInfo()

        #with open("out.html", "w") as outFd:
        #    outFd.write(c.body)

    if not bool(c.info):
        log.debug( "No Record" )
    log.info("===[Query Result]===")
    for k, r in c.info.iteritems():
        log.info( "\t{:>20s}:{:<20s}".format(k,r))

    guessRandNo = raw_input("Info found, will you like to guess the random number? [Y/N]:")
    if guessRandNo.lower() == 'y':
        c.guessRandNo()
    else:
        log.info("Bye")


