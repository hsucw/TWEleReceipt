from oct2py import octave
import csv
import sys
import numpy as np
import os

if len(sys.argv) < 3:
    print "usage: genNormalizedDaily.py filename interval"
    exit(1)
else:
    fname = sys.argv[1]
    interval = sys.argv[2]

print "open csv file:{}".format(fname)

data = []
with open(fname, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    next(reader,None)#skip header
    #srt= sorted(reader, key=lambda x: x[3])
    for row in reader:
        data.append(row[2])

x = np.array(data, dtype=int)[np.newaxis]
x = np.transpose(x)


octave.addpath('.')
res = octave.genNormalizedDaily(x, interval)
#print res
outfname = os.path.splitext(fname)[0]+"_norm_{}".format(interval)+os.path.splitext(fname)[1]
print outfname

with open(outfname, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='|')
    for row in res:
        writer.writerow(row)
