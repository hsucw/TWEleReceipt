#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys,os
from gen_data import genNormDaily, genFreqRatio
from os import walk
import csv
import matplotlib.cm as cm


def progress(count, total, suffix=''):
    bar_len = 30
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s (%s/%s)\r' % \
        (bar, percents, '%', suffix, count, total))
    sys.stdout.flush()  # As suggested by Rom Ruben

def readDataXYZ(start, end, fname):
    try:
        receiptInt = []
        dateInt = []
        money = []
        res = []
        with open(fname, 'r') as fd:
            lines = fd.read().splitlines()[1:]
            for line in lines:
                data = line.split(',')
                if int(data[5]) < end and int(data[5]) > start:
                    res.append(  (int(data[4]), int(data[5]), int(data[2])) )
                    #receiptInt.append(int(data[4]))
                    #dateInt.append(int(data[5]))
                    #money.append(int(data[2]))

            if len(dateInt) == len(receiptInt) and\
             len(money) == len(receiptInt):
                return res
            else:
                print "not equal length: {}".format(fname)
    except Exception as e:
        print e

def extractSequence(receipts):
    sorted(receipts, key=lambda tup: (tup[1],tup[2]))
    st = 0
    ed = 0
    fd = receipts[0][1] # for first day
    ld = fd
    squence = []

    for rece in receipts:
        if rece[1] == ld: #same date
            ed+=1
            continue
        elif abs(rece[1] - ld) == 1:
            ld = rece[1]
            ed+=1
        else: # break sequence
            squence.append((st,ed, fd, ld))
            fd = rece[1]
            ld = fd
            st = ed+1
            ed = st
    squence.append((st,ed, fd, ld))
    return squence

def plotSeq(data,sequ):
    # Initial
    fig, ax1 = plt.subplots(figsize=(9, 7))
    fig.subplots_adjust(left=0.115, right=0.88)
    fig.canvas.set_window_title('Receipt Sequence')

    #for taxid in data.keys():



def readAllData(args):

    sd = args['start_date']
    ed = args['end_date']
    tl = args['taxid_list']

    print "taxid_list {}".format(len(tl))

    data = {}
    seqs = {}
    for taxid in tl:
        data[taxid] = []
        seqs[taxid] = []
        for (dirpath, dirnames, fnames) in walk("data/{}".format(taxid)):
            total = len(fnames)
            cnt = 0
            for fname in fnames:
                cnt+=1
                #progress(cnt,total, fname)
                if "norm" in fname:
                    continue
                if "freq" in fname:
                    continue
                if "income" in fname:
                    continue
                if fname.split('.')[1] != "csv":
                    continue
                date = fname.split('.')[0]
                target_fname = dirpath+"/"+fname

                data[taxid] += (readDataXYZ(sd,ed,target_fname))
            data[taxid] = [ x for x in data[taxid] if x != []]
            seqs[taxid] = extractSequence(data[taxid])
        print seqs

    #print data[taxid]
    return data


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: python plot.py [start_date] [end_date]\
            [taxid1] [taxid2] [taxid3]..."
        exit(1)
    args = {}
    args['start_date'] = int(sys.argv[1])
    args['end_date'] = int(sys.argv[2])
    args['taxid_list'] = sys.argv[3:]

    data = readAllData(args)

    exit(1)

    colors = cm.rainbow(np.linspace(0, 1, len(args['taxid_list'])))
    colors = ['g','b','y']

    fig = plt.figure(figsize=(12,9))
    ax = fig.add_subplot(111, projection='3d')
    fig.suptitle("NCTU receipts")

    c_index = 0
    for taxid in args['taxid_list']:

        x = np.array(X[taxid])
        y = np.array(Y[taxid])
        z = np.array(Z[taxid])
        print "{} {}".format(taxid, colors[c_index])
        #print len(X[taxid]), len(Y[taxid]), len(Z[taxid])
        ax.scatter(x,y,z,c=colors[c_index],marker='o',\
        s=20, alpha=0.2, edgecolors='none')
        c_index += 1

    ax.set_xlabel('date')
    ax.set_ylabel('receipt')
    ax.set_zlabel('money')
    ax.zaxis.set_major_formatter(plt.FuncFormatter(\
        lambda x, loc: "{:,}".format(int(x))))
    #plt.show()

    #combineTaxID(taxid, interval, unit, num)
    #print readFileNorm(sys.argv[1], int(sys.argv[2]))
    #print readFileFreq(sys.argv[1], int(sys.argv[3]), int(sys.argv[4]))
