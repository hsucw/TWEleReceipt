#!env python2
import httplib
import urllib
import logging as log
import sys
import time
import os
import thread

from ImgResolver import ImgResolver
from HTMLDataResolver import HTMLDataResolver

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

        self.imgCode = ""
        self.tmp_file = ""

        self.imgRslr = ImgResolver()
        self.htmlRslr = HTMLDataResolver()
        self.cookie_str = ""

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
        # self.headers['Referer']="https://www.einvoice.nat.gov.tw/APMEMBERVAN/PublicAudit/PublicAudit!queryInvoiceByCon"
        self.headers['Referer'] = "https://www.einvoice.nat.gov.tw/APMEMBERVAN/PublicAudit/PublicAudit"
        self.headers['Connection'] = "keep-alive"
        self.headers['Content-Type'] = "application/x-www-form-urlencoded"
        self.headers['Cookie'] = self.cookie_str

    def getPath(self, path="/"):
        log.debug('GET URL :{}'.format(path))
        self.conn = httplib.HTTPSConnection(self.domain)
        if self.conn is None:
            raise Exception

        self.setReqHeader()
        log.debug("GET:{} with {}".format(path, self.headers))

        try:
            self.conn.request("GET", path, headers=self.headers)
        except Exception as e:
            log.error("{0} : {2}".format( type(e).__name__, e.strerror))
            exit(1)

        while True:
            try:
                self.res = self.conn.getresponse()
            except httplib.ResponseNotReady:
                log.info ("retry after 3 seconds...")
                time.sleep( 0.1 )
                continue
            else:
                break

        for header in self.res.getheaders():
            if header[0] == 'set-cookie':
                self.cookie_str = header[1]
                log.debug("Set-cookie:{}".format(header[1]))
                break

        self.body = self.res.read()
        log.debug('[{}]:{}'.format(self.res.status, self.res.reason))
        return self.res.status

    def resolveImg(self):
        self.imgCode = ""

        while self.imgCode is "":
            self.getPath(self.imgPath)
            #time.sleep( 3 )
            self.imgCode= self.imgRslr.resolveImg(self.body)
        return self.imgCode

    def setPostData(self, num, date):
        self.postData['publicAuditVO.invoiceNumber'] = num
        self.postData['publicAuditVO.invoiceDate'] = date
        self.postData['publicAuditVO.customerIdentifier'] = ""
        self.postData['publicAuditVO.randomNumber'] = ""
        self.postData['txtQryImageCode'] = self.imgCode
        # self.postData['CSRT'] = "13264906813807202173"
        self.postData['CSRT'] = "10413798442182405690"

    def postForm(self, path):
        params = urllib.urlencode(self.postData)

        self.setReqHeader()
        try:
            self.conn.request("POST", path, params, headers=self.headers)
        except Exception as e:
            log.error("{0} : {2}".format( type(e).__name__, e.strerror))
            exit(1)
        log.debug("POST:{} {} with {}".format(path, params, self.headers))
        while True:
            try:
                self.res = self.conn.getresponse()
            except (httplib.ResponseNotReady ,httplib.BadStatusLine):
                log.info("retry")
                time.sleep( 0.1 )
                continue
            else:
                break
        if  self.res :
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
        while randNo is None:

            if not self.session_valid:
                #self.imgRslr.reportFail(self.imgCode, self.imgSHA)
                self.resolveImg()
                log.info("Session invalid")

            self.postData['publicAuditVO.randomNumber'] = guess_list[guess_index]
            self.postForm( self.postPath )

            if self.htmlRslr.findDetail(self.body):
                randNo = guess_list[guess_index]
                log.debug("\nRandom Number Found "+randNo)
                break

            if guess_index < list_len:
                log.debug( "\rtrying rand no {}, total {}/{}".format(guess_list[guess_index],guess_index+1,list_len) )
                progress(guess_index, 9999)
                guess_index += 1
            else:
                log.debug("\nRandom Number Not Found")
                break



if __name__ == '__main__':
    """ give a guess for id & date"""
    log.basicConfig(level=log.INFO)

    if len(sys.argv) != 3:
        log.info("Usage: python Connector.py [RECEIPT_ID] [DATE(YYYY/MM/DD)]")
        log.error("Unknown input")
        sys.exit(1)

    rec_id = sys.argv[1]
    rec_date = sys.argv[2]

    c = Connector()
    # log.info('Connect to {}'.format(c.domain))

    res = None
    while res is None:
        log.info("Get New Image")
        #c.imgRslr.reportFail(c.imgCode, c.imgSHA)
        c.resolveImg()
        log.info("Resolve Image:{}".format(c.imgCode))
        c.setPostData(rec_id, rec_date)
        c.postForm(c.postPath)
        log.info('[{} {}]Post data'.format(c.res.status, c.res.reason))
        res = c.getInfo()

        with open("out.html", "w") as outFd:
            outFd.write(c.body)





    if not bool(c.info):
        log.debug( "No Record" )
    log.info("===[Query Result]===")
    for k, r in c.info.iteritems():
        log.info( "{:>16}".format(k)+":\t"+"{:<20}".format(r) )

    guessRandNo = raw_input("Info found, will you like to guess the random number? [Y/N]:")
    if guessRandNo.lower() == 'y':
        c.guessRandNo()
    else:
        log.info("Bye")


