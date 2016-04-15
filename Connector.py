#!/usr/local/bin/python
import httplib, urllib
import os
import logging as log
import time
import sys

class Connector(object):
    def __init__(self, domain="www.einvoice.nat.gov.tw"):
        self.domain = domain
        self.cookie_str = ""
        self.headers = {}
        self.postData = {}
        self.guess_total = 0
        self.guess_hit = 0
        self.imgCode = ""
        self.tmp_file = ""
        self.publicAudit = '/APMEMBERVAN/PublicAudit/PublicAudit'
        self.postPath = '/APMEMBERVAN/PublicAudit/PublicAudit!queryInvoiceByCon'
        self.imgPath = '/APMEMBERVAN/PublicAudit/PublicAudit!generateImageCode'

    def setReqHeader(self):
        self.headers['User-Agent'] ="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:38.0) Gecko/20100101 Firefox/38.0"
        self.headers['Accept'] ="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        self.headers['Host']="www.einvoice.nat.gov.tw"
        self.headers['Accept-Language']="zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3"
        self.headers['Accept-Encoding']="gzip, deflate"
        self.headers['Referer']="https://www.einvoice.nat.gov.tw/APMEMBERVAN/PublicAudit/PublicAudit!queryInvoiceByCon"
        self.headers['Connection']="keep-alive"
        self.headers['Cookie']=self.cookie_str
        self.headers['Content-Type']="application/x-www-form-urlencoded"
        self.headers['Origin']="https://www.einvoice.nat.gov.tw"

    def clearCookie(self):
        self.cookie = {}

    def setPostData(self, data):
        self.postData = data

    def getPath(self, path="/"):
        self.conn   =   httplib.HTTPSConnection(self.domain)
        if self.conn is None:
            raise Exception

        self.setReqHeader()
        self.conn.request("GET", path, headers=self.headers)
        while True:
            try:
                self.res = self.conn.getresponse()
            except httplib.ResponseNotReady:
                print "retry"
                continue
            else:
                break

        for header in self.res.getheaders():
            if header[0] == 'set-cookie':
                self.cookie_str = header[1]
                #self.setCookie(self.cookie_str)
                break

        self.body = self.res.read()
        return self.res.status


    def resolveImg(self):
        # retry
        while len(self.imgCode) is not 5:
            self.guess_total += 1
            try:
                os.remove(self.tmp_file)
            except:
                pass

            self.getPath(self.imgPath)

            # keep the data
            self.tmp_file = "tmp_"+int(time.time()).__str__()+".jpeg"
            with open(self.tmp_file, "w") as oFd:
                oFd.write(self.body)

            self.imgCode = os.popen("tesseract -l eng {} stdout 2>/dev/null"\
                    .format(self.tmp_file)).readline()[0:-1]
            log.info("Guess Ratio:{}/{}={}%".format(self.guess_hit+1, self.guess_total, \
                    ((self.guess_hit+1)*100/(self.guess_total))))

        self.guess_hit += 1
        os.remove(self.tmp_file)

    def postForm(self, path, num, date ):
        self.postData['publicAuditVO.invoiceNumber'] = num
        self.postData['publicAuditVO.invoiceDate'] = date
        self.postData['publicAuditVO.customerIdentifier'] = ""
        self.postData['publicAuditVO.randomNumber'] = ""
        self.postData['txtQryImageCode'] = self.imgCode
        self.postData['CSRT'] = "13264906813807202173"
        params = urllib.urlencode(self.postData)

        self.setReqHeader()
        self.conn.request("POST", path, params, headers=self.headers)
        while True:
            try:
                self.res = self.conn.getresponse()
            except httplib.ResponseNotReady:
                print "retry"
                continue
            else:
                break
        self.body = self.res.read()


if __name__ == '__main__':
    """ give a guess for id & date"""
    log.basicConfig(level=log.INFO)

    if len(sys.argv) != 3:
        print("Usage: python Connector.py [ID] [DATE]")
        log.error("Unknown input")
        sys.exit(1)

    rec_id = sys.argv[1]
    rec_date = sys.argv[2]

    c = Connector()
    log.info('Connect to {}'.format(c.domain))

    c.getPath(c.publicAudit)
    log.info('[{}]Get normal page & set cookie'.format(c.res.reason))

    c.resolveImg()
    log.info('[{}]Get Image {}:{}'.format(c.res.reason, c.tmp_file, c.imgCode))

    c.postForm( c.postPath, rec_id, rec_date)
    log.info('[{}]Post data'.format(c.res.reason))

    print(c.body)
