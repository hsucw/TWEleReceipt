from oct2py import octave
import csv
import sys
import numpy as np
import os


def genNormDaily(fname, interval):
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
    outfname = os.path.splitext(fname)[0]+\
            "_norm_{}".format(interval)+os.path.splitext(fname)[1]

    with open(outfname, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|')
        for row in res:
            writer.writerow(row)

def genFreqRatio(fname, unit, num):
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
    res = octave.genFrequencyRatio(x, unit, num)
    outfname = os.path.splitext(fname)[0]+\
            "_freq_{}_{}".format(unit,num)+os.path.splitext(fname)[1]

    with open(outfname, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|')
        for row in res:
            writer.writerow(row)


def printUsage():
    print "usage: python gen_data.py [freq|norm] [options]"
    print " for norm, args: [filename] [interval]"
    print " for freq, args: [filename] [unit_money] [num_units]"

if __name__ == '__main__':
    if len(sys.argv) < 3:
        printUsage()
        exit(1)
    elif sys.argv[1] == "norm" and len(sys.argv) == 4:
        genNormDaily(sys.argv[2],int(sys.argv[3]))
    elif sys.argv[1] == "freq" and len(sys.argv) == 5:
        genFreqRatio(sys.argv[2],int(sys.argv[3]), int(sys.argv[4]))
    else:
        printUsage()

