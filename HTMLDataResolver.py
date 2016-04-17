#!/usr/local/bin/python
import httplib, urllib
import os
import time
import re
import logging as log
import sys
from htmldom import htmldom

colNames =['id','date','com','stat','money','taxid','addr','note']

class NoRecord(Exception):
    log.warn("no record")
    pass
class NotCorrectFormat(Exception):
    log.warn("not correct format")
    pass
class NotFoundResult(Exception):
    """not found the result"""
    log.warn("not found result")
    pass

class HTMLDataResolver(object):

    def __init__(self):
        pass

    def parseUTF8(self,instr):
        """transform the text"""
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
                log.warn("Unknown unichr error")
        return outstr

    def findtheData(self,items):
        """find the sequence of data"""
        text = {}
        for i in range(0,items.length()):
            if re.match("^[a-zA-Z]{2}\d{8}$", items[i].text()) is not None:
                j = 0
                for col in colNames:
                    try:
                        field = self.parseUTF8(items[i+j].text())
                        #print items[i+j].html()
                        #if field is "":
                        #    raise NoRecord
                    except Exception as e:
                        log.warn(e)
                        raise NotCorrectFormat
                        break
                    text[col]=field
                    j += 1
                return text
                break
        log.warn("Not found the number in {}".format(items.text()))
        raise NotFoundResult

    def resolve(self, content):
        """resolve the html dom"""
        dom = htmldom.HtmlDom().createDom(content)

        items = dom.find("table[class=lpTb] tr td")

        if items.length is 0:
            return {}

        try:
            data = self.findtheData(items)
        except NotFoundResult:
            data = None
        except NoRecord:
            data = {}
        except NotCorrectFormat:
            data = None
        return data


if __name__ == "__main__":
    """give a .html retrived from the www.einvoice.nat.gov.tw"""
    log.basicConfig(level=log.INFO)
    if sys.argv[1] is not None:
        infile = sys.argv[1]

    with open(infile, "r") as inFd:
        content = inFd.read()
    resolver = HTMLDataResolver()
    res = resolver.resolve(content)
    for k,r in res.iteritems():
        print k+":"+r
    #pass
