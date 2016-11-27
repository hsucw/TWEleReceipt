#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import sys,os
from gen_data import genNormDaily, genFreqRatio
from os import walk
import csv

def readFileNorm(fname, interval):
    norm_name = os.path.splitext(fname)[0]+"_norm_{}".format(interval)\
        +os.path.splitext(fname)[1]

    if not os.path.exists(norm_name):
        genNormDaily(fname, interval)

    try:
        with open(norm_name, 'r') as fd:
            lines = fd.read().splitlines()
            return [float(e) for e in lines]

    except Exception as e:
        print e

def readFileFreq(fname, unit, num):
    freq_name = os.path.splitext(fname)[0]+"_freq_{}_{}".format(unit,num)\
        +os.path.splitext(fname)[1]

    if not os.path.exists(freq_name):
        genFreqRatio(fname, unit, num)
    try:
        with open(freq_name, 'r') as fd:
            lines = fd.read().splitlines()
            return [float(e) for e in lines]

    except Exception as e:
        print e

def readDailyIncome(fname):
    try:
        with open(fname, 'r') as fd:
            lines = fd.read().splitlines()[1:]
            total = [float(e.split(',')[2]) for e in lines]
            return sum(total)
    except Exception as e:
        print e


def combineTaxID(taxid, intval=24, unit=20, num=50):
    freq_data = {}
    norm_data = {}
    daily_data = {}

    f = []
    for (dirpath, dirnames, fnames) in walk("data/{}".format(taxid)):
        for fname in fnames:
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
            norm_data[date] = readFileNorm(target_fname, intval)
            freq_data[date] = readFileFreq(target_fname, unit, num)
            daily_data[date]= readDailyIncome(target_fname)
        #break

    outNormFname = "data/{}/{}_norm.csv".format(taxid, taxid)
    outFreqFname = "data/{}/{}_freq.csv".format(taxid, taxid)
    outIncoFname = "data/{}/{}_income.csv".format(taxid, taxid)
    with open(outNormFname,'wb') as f:
        w = csv.writer(f,  delimiter=',', quotechar='|')
        for key, value in norm_data.items():
            value.insert(0, key)
            w.writerow(value)

    with open(outFreqFname,'wb') as f:
        w = csv.writer(f,  delimiter=',', quotechar='|')
        for key, value in freq_data.items():
            value.insert(0, key)
            w.writerow(value)

    with open(outIncoFname,'wb') as f:
        w = csv.writer(f,  delimiter=',', quotechar='|')
        for key, value in daily_data.items():
            #value.insert(0, key)
            w.writerow((key,value))

    #with open(outFreqFname,'wb') as f:
    #    w = csv.writer(f)
    #    w.writerows(freq_data.items())

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python plot.py [taxid] [interval=24] [unit=20] [num=50]"
        exit(1)
    combineTaxID(sys.argv[1])
    #print readFileNorm(sys.argv[1], int(sys.argv[2]))
    #print readFileFreq(sys.argv[1], int(sys.argv[3]), int(sys.argv[4]))



