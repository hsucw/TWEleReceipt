#!/usr/bin/env python
import sqlite3
import sys
import csv
import os
import errno
from datetime import datetime
from os import walk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d
from aggregate import combineTaxID


DATA_DIR="./data"
tbl_name = "taskServer_receipt"
out_filename = "fingerprint.csv"

if __name__ == "__main__":

    taxid_list = []
    labels = []
    c_index = []
    colors = cm.rainbow(np.linspace(0, 1, 15))
    if len(sys.argv) < 2:
        print "usage:"
        print "python gen_csv.py filename"
        exit(1)
    elif sys.argv[1] == "stdin":
        taxid_list = sys.stdin.readlines()
    else:
        taxid_list = sys.argv[1:]

    taxid_list = ["{:08d}".format(int(t)) for t in taxid_list]

    # aggregate first
    weekday_value = {}
    count = {}


    incomes = {}

    for taxid in taxid_list:
        taxid = taxid.rstrip()

        for i in range(7):
            count[str(i)] = 0
            weekday_value[str(i)] = 0

        print "hanle {}".format(taxid)
        combineTaxID(taxid, 24, 20, 20)

        with open("data/{}/{}_income.csv".format(taxid,taxid), "r") as incomefile:
            reader = csv.reader(incomefile, delimiter=',', quotechar='|')
            for row in reader:
                day_num = (int(row[0])+6)%7

                weekday_value[str(day_num)] += float(row[1])
                count[str(day_num)] +=1
        res = {}
        for k,v in weekday_value.iteritems():
            if count[k] == 0:
                continue
            res[k] = v/count[k]

        incomes[taxid] = res
            #data = data.reshape(2,total/2)
    with open("all_incomes_by_week.csv", "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|')
        for k, v in incomes.iteritems():
            tmp = []
            tmp.append(k)
            if len(v) < 7:
                print "Should Remove {}".format(k)
                continue
            for i in range(7):
                tmp.append(v[str(i)])
            writer.writerow(tmp)

            #line =  [k,v[0],v[1],v[2],v[3],v[3],v[3]]
            #writer.writerow(line)
