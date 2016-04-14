#!/usr/bin/python
import httplib
import os
import time
class Connector(object):
    def __init__(self, domain=None):
        self.domain = domain

    def connect(self, path="/"):
        self.conn   =   httplib.HTTPSConnection(self.domain)
        if self.conn is None:
            raise Exception
        print self.conn.request("GET", path)
        res = self.conn.getresponse()
        return res.status

    def getImage(self, imgPath):
        self.conn   =   httplib.HTTPSConnection(self.domain)
        if self.conn is None:
             raise Exception

        print self.conn.request("GET", imgPath)
        res = self.conn.getresponse()
        self.img = res.read()
        self.tmp_file = "tmp_"+int(time.time()).__str__()+".jpeg"

    def resolveImg(self)
        with open(self.tmp_file, "w") as oFd:
            oFd.write(self.img)
        #resolve
        os.remove(self.tmp_file)
        self.tmp_file = None
        self.img = None

if __name__ == '__main__':
    einvoice_domain = 'www.einvoice.nat.gov.tw'
    publicAudit = '/APMEMBERVAN/PublicAudit/PublicAudit'
    imgPath = '/APMEMBERVAN/PublicAudit/PublicAudit!generateImageCode'

    c = Connector(einvoice_domain)
    #if c.connect(publicAudit) is 200:
    c.getImage(imgPath)

