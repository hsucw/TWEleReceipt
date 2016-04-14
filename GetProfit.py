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
        self.headers = res.getheaders()
        self.body = res.read()
        print self.headers
        return res.status

    def getImage(self, imgPath):
        self.conn   =   httplib.HTTPSConnection(self.domain)
        if self.conn is None:
             raise Exception

        print self.conn.request("GET", imgPath)
        res = self.conn.getresponse()
        self.img = res.read()
        self.tmp_file = "tmp_"+int(time.time()).__str__()+".jpeg"

    def resolveImg(self):
        with open(self.tmp_file, "w") as oFd:
            oFd.write(self.img)
        self.imgCode = os.popen("tesseract -l eng {} stdout".format(self.tmp_file)).readline()
        os.remove(self.tmp_file)
        self.tmp_file = None
        self.img = None

    def postForm(self):
        pass


if __name__ == '__main__':
    einvoice_domain = 'www.einvoice.nat.gov.tw'
    publicAudit = '/APMEMBERVAN/PublicAudit/PublicAudit'
    imgPath = '/APMEMBERVAN/PublicAudit/PublicAudit!generateImageCode'

    c = Connector(einvoice_domain)
    c.connect(publicAudit)
    #c.getImage(imgPath)
    #c.resolveImg()

