#!/usr/local/bin/python
import httplib, urllib
import os
import time
import re
import logging as log
from htmldom import htmldom

with open("test.html", "r" ) as inFd:
    content = inFd.read()

dom = htmldom.HtmlDom().createDom(content)
items = dom.find( "table[class=lpTb] " ).text()



if __name__ == "__main__":
    pass

