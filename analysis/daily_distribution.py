import sqlite3
import time
from  datetime import date, datetime
conn = sqlite3.connect('example.db')
c = conn.cursor()

c.execute('drop table if exists daily_dist')

conn.commit()
# Create table
c.execute('''CREATE TABLE daily_dist
                     (tid integer, date integer ,did integer, amount integer)''')


cursor = c.execute("select * from receipt")

repeat = set()

total = {}

total['18221188'] = {}
total['42078697'] = {}

for row in cursor.fetchall():
    alpha = ((ord(row[0][0])-ord('A'))*26+(ord(row[0][1])-ord('A')))*(10**8)
    mid = alpha+int(row[0][2:])
    cd = row[1].replace(row[1][0:3], str(int(row[1][0:3])+ 1911))
    md = (int(datetime.strptime(cd, '%Y/%m/%d').strftime("%s"))-1459468800)/86400
    ma = row[2]
    mtid = row[3]

    if mtid not in total:
        continue
    if md not in total[mtid]:
        total[mtid][md] = []
    total[mtid][md].append((mid, ma))
    #print "{} {} {} {}".format(mtid,md,mid,ma)

for com in total:
    full = []
    not_good = []
    for d in total[com]:
        total[com][d].sort(key=lambda tup: tup[0])

        total_size  = len(total[com][d])
        col = {}
        cur_min = float("inf")
        for ts in total[com][d]:
            did = ts[0]
            amount = ts[1]
            if cur_min > did:
                cur_min = did
                col[cur_min]= 0
            if did - cur_min > total_size:
                cur_min = did
                col[cur_min] = 0
            col[cur_min] += 1

        max_ele = 0
        min_id = 0
        for dd in col:
            if col[dd]>max_ele:
                max_ele = col[dd]
                min_id = dd

        seq_ratio = max_ele*100.0/total_size
        print "min_id= {}, seq_len= {}".format(min_id, seq_ratio)
        if seq_ratio < 85:
            not_good.append(d)
            continue
        else:
            full.append(d)

        res_tuples = []
        for i in range(0, total_size):
            new_id = int(total[com][d][i][0])-min_id
            if new_id < 0 or new_id > total_size:
                continue
            res_tuples.append((new_id, total[com][d][i][1]))
        total[com][d] = res_tuples

        for ts in total[com][d]:
            did = ts[0]
            amount = ts[1]
            res = (com, d, did, amount)
            #print res
            c.execute('''insert into daily_dist values (?,?,?,?)''', res)

    print "{}: {}%".format(com, len(full)*100.0/(len(full)+len(not_good)))
    print "good samples:{}".format(full)
    print "bad samples:{}".format(not_good)

conn.commit()
