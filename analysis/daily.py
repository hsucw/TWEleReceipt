
import sqlite3
import time
from  datetime import date, datetime
conn = sqlite3.connect('example.db')
c = conn.cursor()

c.execute('drop table if exists daily2')

conn.commit()
# Create table
c.execute('''CREATE TABLE daily2
                     (tid integer, amount numeric, date integer)''')


cursor = c.execute("select * from receipt")

repeat = set()

total = {}

for row in cursor.fetchall():

    cd = row[1].replace(row[1][0:3], str(int(row[1][0:3])+ 1911))
    md = (int(datetime.strptime(cd, '%Y/%m/%d').strftime("%s"))-1459468800)/86400
    ma = row[2]
    mtid = row[3]
    if mtid not in total:
        total[mtid]={}
    if md not in total[mtid]:
        total[mtid][md] = 0;
    total[mtid][md] += ma;

for com in total:
    if com not in ['18221188','42078697']:
        next
    for d in total[com]:
        res = (com, total[com][d], d)
        #print res
        c.execute("insert into daily values (?,?,?)", res)

conn.commit()
