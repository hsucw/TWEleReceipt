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
        with open(fname, 'r') as fd:
            lines = fd.read().splitlines()[1:]
            for line in lines:
                data = line.split(',')
                if int(data[5]) < end and int(data[5]) > start:
                    receiptInt.append(int(data[4]))
                    dateInt.append(int(data[5]))
                    money.append(int(data[2]))

            if len(dateInt) == len(receiptInt) and\
             len(money) == len(receiptInt):
                return dateInt, receiptInt, money
            else:
                print "not equal length: {}".format(fname)
    except Exception as e:
        print e


def readAllData(args):

    sd = args['start_date']
    ed = args['end_date']
    tl = args['taxid_list']

    X = {}
    Y = {}
    Z = {}
    for taxid in tl:
        X[taxid] = []
        Y[taxid] = []
        Z[taxid] = []
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

                x,y,z = readDataXYZ(sd,ed,target_fname)
                X[taxid]+=x
                Y[taxid]+=y
                Z[taxid]+=z

                #readDataXYZ(target_fname)
            #norm_data[date] = readFileNorm(target_fname, intval)
            #freq_data[date] = readFileFreq(target_fname, unit, num)
            #d_key, d_value= readDailyIncome(target_fname)
            #daily_data[d_key] = d_value
        #break
    return X,Y,Z

    #with open(outFreqFname,'wb') as f:
    #    w = csv.writer(f)
    #    w.writerows(freq_data.items())

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: python plot.py [start_date] [end_date]\
            [taxid1] [taxid2] [taxid3]..."
        exit(1)
    args = {}
    args['start_date'] = int(sys.argv[1])
    args['end_date'] = int(sys.argv[2])
    args['taxid_list'] = sys.argv[3:]

    X,Y,Z = readAllData(args)

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
    plt.show()

    #combineTaxID(taxid, interval, unit, num)
    #print readFileNorm(sys.argv[1], int(sys.argv[2]))
    #print readFileFreq(sys.argv[1], int(sys.argv[3]), int(sys.argv[4]))
