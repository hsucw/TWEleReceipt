from oct2py import octave
import csv
import sys
import numpy as np
import os

if len(sys.argv) < 4:
    print "usage: genFrequencyRatio.py [filename] [unit_money] [num_units]"
    print "                   for example: 20 dollar as one unit, 40 units"
    exit(1)
else:
    fname = sys.argv[1]
    unit_m = int(sys.argv[2])
    num_unit = int(sys.argv[3])

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
res = octave.genFrequencyRatio(x,unit_m, num_unit)
print res
outfname = os.path.splitext(fname)[0]+"_freq_{}_{}".format(unit_m,num_unit)+os.path.splitext(fname)[1]
#print outfname

with open(outfname, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='|')
    for row in res:
        writer.writerow(row)
