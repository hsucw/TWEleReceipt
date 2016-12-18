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

DATA_DIR="./data"
tbl_name = "taskServer_receipt"
out_filename = "fingerprint.csv"



def fingerprintByTaxID(db_name, taxid_list):

    conn = sqlite3.connect(db_name)
    c=conn.cursor()

    fp={}
    for taxid in taxid_list:
        fp[taxid]={}

        print "handle {}".format(taxid)

        #cmd = 'select distinct date from {} where taxid = ?'.format(tbl_name)
        #c.execute(cmd,(taxid,))

        for dt in c:
            #print "    -- {}".format(dt)
            date = list(dt)[0]
            d=conn.cursor()
            cmd = 'select count(*) from {} where taxid = ? and\
             date = ? order by receipt asc'.format(tbl_name)
            d.execute(cmd, (taxid, date))
            amount = int(d.fetchone()[0])
            print "{}:{}".format(date, amount)
            fp[taxid][date] = amount

"""
            fname = "{}/{}/{}.csv".format(DATA_DIR,taxid,date.replace('/','-'))

            if not os.path.exists(os.path.dirname(fname)):
                try:
                    os.makedirs(os.path.dirname(fname))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        print "cannot open file"
                        raise

            with open(fname, "w+") as f:
                f.write("recp,date,money,taxid,recp_id,date_num\n")
                for line in d:
                    l = list(line)
                    alpha = ((ord(l[0][0])-ord('A'))*26+(ord(l[0][1])-ord('A')))*(10**8)
                    recp_id = alpha+int(l[0][2:])
                    y,m,d = l[1].split('/')
                    if int(y) < 2000:
                        y=str(int(y)+1911)
                    iso_date = '/'.join((y,m,d))                    #2016-01-01
                    date_num = (int(datetime.strptime(iso_date, '%Y/%m/%d').strftime("%s"))-1451606400)/86400
                    rec =  "{},{},{},{},{},{}\n".format(l[0],l[1],l[2],l[3], recp_id, date_num)
                    f.write(rec)
"""
def readRecord(fname):
    res = []
    day = None
    with open(fname, 'r') as fd:
        for line in fd.read().splitlines()[1:]:
            tempData = line.split(',')
            res.append( int(tempData[2]) )
            if not day:
                day = int(tempData[5])
        med = np.median(res)

        return day, res, med

def checkFname(fname):
    if "norm" in fname:
        return False
    if "freq" in fname:
        return False
    if "income" in fname:
        return False
    if fname.split('.')[1] != "csv":
        return False
    return True

def readAllData(taxid_list):

    tl = taxid_list
    data = {}
    for taxid in tl:
        data[taxid] = ()
        for (dirpath, dirnames, fnames) in walk("data/{}".format(taxid)):
            total = len(fnames)
            cnt = 0
            all_num = []
            all_data = []
            for fname in fnames:
                cnt+=1
                #progress(cnt,total, fname)
                if not checkFname(fname):
                    continue
                date = fname.split('.')[0]
                target_fname = dirpath+"/"+fname

                d, a, m = readRecord(target_fname)
                l = len(a)

                #print a, m
                all_num.append(l)
                all_data += a


        m = np.mean(all_num)
        s = np.std(all_num)
        # Remove incomplete days
        all_num = [x for x in all_num if x >= m-s ]
        num_m = np.mean(all_num)

        #print len(all_data)

        total = len(all_data)
        #med = np.median(all_data)
        mean = np.mean(all_data)
        s = np.std(all_data)
        y = mean / 20
        out = [x for x in all_data if x/20 <= y]
        cur = len(out)

        #data[taxid] = (float(num_m),float(mean),float(cur*1.0/total),float(mean*1.0/s))
        data[taxid] = (float(num_m),float(mean),float(cur*1.0/total),float(1.0*s))


    return data
    #print data[taxid]

def plot3D(data, taxid_list):
    colors = cm.rainbow(np.linspace(0, 1, len(taxid_list)))

    fig = plt.figure(figsize=(12,9))
    ax = fig.add_subplot(111, projection='3d')
    fig.suptitle("NCTU receipts")

    c_index = 0
    for taxid in taxid_list:

        (x, y, z) = data[taxid]
        print "{} {}".format(taxid, colors[c_index])
        #print len(X[taxid]), len(Y[taxid]), len(Z[taxid])
        ax.scatter(np.log(x),y,z,c=colors[c_index],marker='o',\
        s=20, alpha=0.2, edgecolors='none')
        #x2, y2, _ = proj3d.proj_transform(x,y,z, ax.get_proj())
        #label = plt.annotate(\
        #taxid,\
        #xy = (x2, y2), xytext = (-20, 20),\
        #textcoords = 'offset points', ha = 'right', va = 'bottom',\
        #bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.1),\
        #arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

        c_index += 1


    ax.set_xlabel('num')
    #ax.set_xscale('log',nonposx='clip')
    ax.set_ylabel('med')
    ax.set_zlabel('ratio')
    ax.zaxis.set_major_formatter(plt.FuncFormatter(\
        lambda x, loc: "{:,}".format(int(x))))
    #fig.canvas.mpl_connect('button_release_event', update_position)
    plt.show()

def update_position(e):
    x2, y2, _ = proj3d.proj_transform(1,1,1, ax.get_proj())
    label.xy = x2,y2
    label.update_positions(fig.canvas.renderer)
    fig.canvas.draw()

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
        with open(sys.argv[1]) as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                if row[2] == '0' or row[0]=='':
                    continue
                taxid_list.append(row[0])
                labels.append(row[1])
                c_index.append(int(row[2]))

    taxid_list = ["{:08d}".format(int(t)) for t in taxid_list]
    d = readAllData(taxid_list)

    with open(out_filename, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|')
        for k, v in d.iteritems():
            line =  [k,v[0],v[1],v[2],v[3]]
            writer.writerow(line)

    """
    with open("fingerprint.csv", 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            print row #data.append(row[2])
    """
    for i in range(len(taxid_list)):
        taxid = taxid_list[i]
        label = labels[i]
        (x, y, z, s) = d[taxid]

        plt.scatter(np.log10(x), np.log10(y), s=np.pi *(s/100)**2, c=colors[c_index[i]], alpha=z)
        #plt.annotate(label, xy=(np.log10(x), np.log10(y)),\
        # fontsize=12)

    plt.savefig('all_taxid.png', format='png', dpi=300)
    plt.show()
