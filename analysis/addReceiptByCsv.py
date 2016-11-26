import httplib, urllib
import os, sys
import csv
from htmldom import htmldom


conn = httplib.HTTPConnection("127.0.0.1:8000")
header={}
conn.request("GET", "/")
r1 = conn.getresponse()
#print r1.getheaders()
for h in r1.getheaders():
    if h[0] == 'set-cookie':
        csrftoken =  h[1].split(';')[0].split('=')[1]
        header['Cookie'] = "csrftoken={}".format(csrftoken)
        break

content = r1.read()
#print content
dom = htmldom.HtmlDom().createDom(content)
items = dom.find("form[class=mainContainer] input").first()
csrfmiddleware =  items.html().replace(">"," ").split(" ")[3].split("=")[1][1:-1]
#print "["+csrfmiddleware+"]"
#for it in items:
#    print it.text()
#print items.split('&')



with open('receipt.csv', 'rU') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        params = {}
        params['csrfmiddlewaretoken'] = csrfmiddleware
        params['receipt']= row[0]
        params['date']=row[1]
        #print params
        #params['receipt']="LY10641728"
        #params['date']="2016/11/23"
        postdata = urllib.urlencode(params)
        postdata = urllib.urlencode(params)
        conn.request("POST", "/api/addTask/", postdata, header)
        r1 = conn.getresponse()
        print "post {}".format(postdata)
        print r1.status, r1.reason
        print r1.read()
        #conn.request("POST", "/addTask", postdata)
        #r1 = conn.getresponse()
        #print r1.status, r1.reason
        #print r1.read()

"""
print postdata
print header
postdata = urllib.urlencode(params)
conn.request("POST", "/api/addTask/", postdata, header)
r1 = conn.getresponse()
print r1.status, r1.reason
data = r1.read()

print data

#conn.request("GET", "/APMEMBERVAN/PublicAudit/ateImageCode", headers=header)
#r1 = conn.getresponse()
#print r1.status, r1.reason
#data1 = r1.read()
"""
