from oct2py import octave
import csv
import sys
import numpy as np
import os

if len(sys.argv) < 2:
    print "usage: genNormalizedDaily.py filename"
    exit(1)
else:
    fname = sys.argv[1]

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


#octave.addpath('.')
#res = octave.genNormalizedDaily(x,24)
#print res

outdir = os.path.dirname(fname)
outbase = os.path.basename(fname)
outfname = os.path.basename(fname)
print outfname
