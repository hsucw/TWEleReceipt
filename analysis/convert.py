

import sqlite3
import time
from  datetime import date, datetime
conn = sqlite3.connect('example.db')
c = conn.cursor()

c.execute('drop table if exists test')

conn.commit()
# Create table
c.execute('''CREATE TABLE test
                     (id text primary key, amount numeric, date integer, taxid integer)''')

# Insert a row of data
cursor = c.execute("select * from receipt")

repeat = set()

for row in cursor.fetchall():
    #print row
    #print row[0][2:]
    alpha = ((ord(row[0][0])-ord('A'))*26+(ord(row[0][1])-ord('A')))*(10**8)
    mid = alpha+int(row[0][2:])
    cd = row[1].replace(row[1][0:3], str(int(row[1][0:3])+ 1911))
    md = (int(datetime.strptime(cd, '%Y/%m/%d').strftime("%s"))-1459468800)/86400
    ma = row[2]
    mtid = row[3]

    try:
        res = (mid, ma, md, mtid)
        c.execute("insert into test values (?,?,?,?)", res)
    except sqlite3.IntegrityError:
        try:
            res = (ma, md, mtid, mid)
            c.execute("update test set amount = ? , date = ?, taxid = ? where id = ?",  res)
        except sqlite3.IntegrityError:
            print "cannpt update"
            repeat.add(res)



conn.commit()
print len(repeat)


# Save (commit) the changes
#conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
