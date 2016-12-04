#!/usr/bin/env python
import sqlite3
import sys
import csv
import os
import errno
from datetime import datetime

DATA_DIR="./data"
tbl_name = "taskServer_receipt"

def genCsvFiles(db_name, taxid_list):

    conn = sqlite3.connect(db_name)
    c=conn.cursor()

    for taxid in taxid_list:

        print "handle {}".format(taxid)
        cmd = 'select distinct date from {} where taxid = ?'.format(tbl_name)
        c.execute(cmd,(taxid,))

        for dt in c:
            print "    -- {}".format(dt)
            date = list(dt)[0]
            d=conn.cursor()
            cmd = 'select receipt,date,money,taxid from {} where taxid = ? and date = ? order by receipt asc'.format(tbl_name)
            d.execute(cmd, (taxid, date))

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


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print "usage:"
        print "python gen_csv.py [db_file_name] [taxid]"
        exit(1)
    elif sys.argv[2] == "stdin":
        taxid_list = sys.stdin.readlines()
    else:
        taxid_list = sys.argv[2:]

    taxid_list = ["{:08d}".format(int(t)) for t in taxid_list]
    genCsvFiles(sys.argv[1], taxid_list)




