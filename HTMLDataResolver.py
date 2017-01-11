#!/usr/local/bin/python
########################################################
##  TWEleReceipt: A web client
##  This program is only for hacker college. All the
##  rights are preserved. You can use it on the class.
##  The program cannot be distributed, copied, or modified
##  Written by Chia-Wei Hsu
########################################################
#coding=UTF-8
import httplib, urllib
import os
import time
import re
import logging as log
import sys
from htmldom import htmldom

reload(sys)
sys.setdefaultencoding( "utf-8" )
##
## DB Column names
##
colNames =['id','date','com','stat','money','taxid','addr','note']
##
## A Chinese string for "Record Not Found"
##
no_data_rec_str = '\xe6\x9f\xa5\xe7\x84\xa1\xe7\x99\xbc\xe7\xa5\xa8\xe9\x96\x8b\xe7\xab\x8b\xe8\xb3\x87\xe6\x96\x99'
##
## A Chinese string for password error of image
##
password_error_str = '\xe5\xaf\x86\xe7\xa2\xbc\xe9\x8c\xaf\xe8\xaa\xa4!!\xe8\xab\x8b\xe8\xbc\xb8\xe5\x85\xa5\xe5\x9c\x96\xe5\xbd\xa2\xe4\xb8\x8a\xe7\x9a\x84\xe5\xaf\x86\xe7\xa2\xbc'
password_error_msg = '\xe5\x9c\x96\xe5\xbd\xa2\xe5\xaf\x86\xe7\xa2\xbc\xe9\x8c\xaf\xe8\xaa\xa4'
##
## A Chinese string for query error
##
query_receipt_data_error_str = '\xe5\x85\xa8\xe6\xb0\x91\xe7\xa8\xbd\xe6\xa0\xb8\xe7\x99\xbc\xe7\xa5\xa8\xe8\xb3\x87\xe6\x96\x99\xe6\x9f\xa5\xe8\xa9\xa2\xe7\x95\xb0\xe5\xb8\xb8'
query_unknown_error = '\xe6\x9f\xa5\xe8\xa9\xa2\xe7\x95\xb0\xe5\xb8\xb8 Sleep 10 sec...'
##
## Exception
##
class NoRecord(Exception):
    """ Query Success, but no Data """
    pass
class NotCorrectFormat(Exception):
    """ Query Failure, unexpected format """
    pass
class NotFoundResult(Exception):
    """ Query Failure, captcha error, cookie incomplete"""
    pass

##
## HTML resolver class:
## we can use this class for gathering the
## receipt info from the response web pages
##
class HTMLDataResolver(object):

    def __init__(self):
        pass

    def parseUTF8(self,instr):
        """ transform the text """
        outstr = ""
        if instr.find("&#") < 0:
            return instr.strip()
        chrs = re.split("[;&#]", instr)
        for ch in chrs:
            try:
                outstr += unichr(int(ch))
            except ValueError:
                continue
            except:
                log.debug("Unknown unichr error")
        return outstr

    def findtheData(self,items):
        """ find the sequence of data """
        text = {}
        for i in range(0,items.length()):
            if re.match("^[a-zA-Z]{2}\d{8}$", items[i].text()) is not None:
                j = 0
                for col in colNames:
                    try:
                        field = self.parseUTF8(items[i+j].text())
                    except Exception as e:
                        if text['com'] == no_data_rec_str:
                            log.debug("Record not found")
                            raise NoRecord
                        else:
                            raise NotCorrectFormat
                    text[col]=field
                    j += 1
                return text
        log.debug("Not found the number in response HTML {}".format(items.html()))
        raise NotFoundResult

    def resolve(self, content):
        """resolve the html dom"""
        if  password_error_str in content:
            log.debug( password_error_msg )
            return None
        elif query_receipt_data_error_str in content:
            log.debug( query_unknown_error )
            return None
        elif no_data_rec_str in content:
            return {}

        try:
            dom = htmldom.HtmlDom().createDom(content)
        except Exception, e:
            log.error(e)
            log.error("error content:{}".format(content))
            exit(1)

        items = dom.find("table[class=lpTb] tr td")

        try:
            data = self.findtheData(items)
        except NotFoundResult:
            data = None
        except NoRecord:
            data = {}
        except NotCorrectFormat:
            data = {}
        return data

    def findDetail(self, content):
        """resolve the detail items"""
        dom = htmldom.HtmlDom().createDom(content)

        items = dom.find("table[id=invoiceDetailTable]")
        if items.length() == 0:
            return False
        else:
            return True
##
## The main function
##
if __name__ == "__main__":
    """give a .html retrived from the www.einvoice.nat.gov.tw """
    log.basicConfig(level=log.DEBUG)
    if sys.argv[1] is not None:
        infile = sys.argv[1]

    with open(infile, "r") as inFd:
        content = inFd.read()
    resolver = HTMLDataResolver()
    res = resolver.resolve(content)
    if res is not None:
        if not bool(res):
            print "No Record"
        for k,r in res.iteritems():
            print k+":"+r
    else:
        print "NO DATA"
    #pass
