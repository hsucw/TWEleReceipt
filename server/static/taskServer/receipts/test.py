import csv

csvfile = open('20160913.csv', 'rb') # 1
for row in csv.reader(csvfile): # 2
    print repr(row)
