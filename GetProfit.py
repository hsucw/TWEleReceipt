#!/usr/local/bin/python
import httplib, urllib
import os
import time
import re
import logging as log
from htmldom import htmldom

class Connector(object):
    def __init__(self, domain=None):
        self.domain = domain
        self.cookie_str = ""
        self.headers = {}
        self.postData = {}
        self.guess_total = 0
        self.guess_hit = 0
        self.imgCode = ""
        self.tmp_file = ""

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

    #def setCookie(self, cookie_str):
    #    cookies = re.split('[;,]', cookie_str)
    #    for pair in cookies:
    #        key = pair.split("=")[0]
    #        self.cookie[key] = pair
    #        print "{}:{}".format(key, self.cookie[key])

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
            if os.path.isfile(self.tmp_file):
                os.remove(self.tmp_file)

            self.getPath(imgPath)
            self.tmp_file = "tmp_"+int(time.time()).__str__()+".jpeg"

            with open(self.tmp_file, "w") as oFd:
                oFd.write(self.body)

            self.imgCode = os.popen("tesseract -l eng {} stdout 2>/dev/null".format(self.tmp_file)).readline()[0:-1]
            log.info("NOT Right:{}/{}={}".format(self.guess_hit, self.guess_total, (self.guess_hit/(self.guess_total*1.0))))

        self.guess_hit += 1
        os.rename(self.tmp_file , self.imgCode+".jpeg")
        #os.remove(self.tmp_file)
        #self.tmp_file = None

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

    def extractInfo(self):
        #print self.body
        #if self.body.find("lpTb"):
        #    log.info("Good")

        with open("out.html", "w") as oFd:
            oFd.write(self.body)

        dom = htmldom.HtmlDom().createDom(self.body)
        items = dom.find( "table[class=lpTb] > tr > td" )
        #print "RES:"+items.text()

        #result = {}
        #result['id'] = items.first().text()
        #result['date'] = items.next.text()
        #result['time'] = None
        #result['title'] = items.next.text()
        #result['status'] = items.next.text()
        #result['money'] = items.next.text()
        #result['taxID'] = items.next.text()
        #result['addr'] = items.next.text()
        pass

if __name__ == '__main__':
    einvoice_domain = 'www.einvoice.nat.gov.tw'
    publicAudit = '/APMEMBERVAN/PublicAudit/PublicAudit'
    postPath = '/APMEMBERVAN/PublicAudit/PublicAudit!queryInvoiceByCon'
    imgPath = '/APMEMBERVAN/PublicAudit/PublicAudit!generateImageCode'

    log.basicConfig(level=log.INFO)

    c = Connector(einvoice_domain)
    log.info('Connect to {}'.format(einvoice_domain))

    c.getPath(publicAudit)
    log.info('[{}]Get normal page {}'.format(c.res.reason, publicAudit))

    c.resolveImg()
    log.info('[{}]Get Image {}:{}'.format(c.res.reason, c.tmp_file, c.imgCode))

    c.postForm( postPath, "GL07294895", "105/04/09")
    log.info('[{}]Post data {}'.format(c.res.reason,postPath))

    c.extractInfo()
