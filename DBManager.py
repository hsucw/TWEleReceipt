import sqlite3
import sys

class DBBaseManager(object):
    def __init__(self):
        self.conn = sqlite3.connect("DB/TWEleReceipt.db")
        self.c = self.conn.cursor()

class DBManager(DBBaseManager):
    def __init__(self):
        super(DBManager, self).__init__()

    def CreateTable(self):
        self.c.execute("CREATE TABLE if not exists receipt (id TEXT UNIQUE, date TEXT, money INTEGER, taxid TEXT)")
    def StoreData(self,data):
        for key in data:
            #self.c.execute("SELECT * FROM receipt WHERE id = '{}'".format(key))
            self.c.execute("SELECT * FROM receipt WHERE id = ?",(key,))
            if self.c.fetchone() == None:

                #self.c.execute("INSERT INTO receipt VALUES ('{}','{}',{},'{}')".format(key,data[key][0],data[key][1],str(data[key][2])).zfill(8))
                self.c.execute("INSERT INTO receipt VALUES ('{}','{}',{},'{}')".format(key,data[key][0],data[key][1],str(data[key][2])).zfill(8))

        self.conn.commit()
    def Findid(self,num):
        #self.c.execute("SELECT * FROM receipt WHERE id = '{}'".format(num))
        self.c.execute("SELECT * FROM receipt WHERE id = ?",(num,))
        if self.c.fetchone() == None:
            return False
        else:
            return True
    def DeleteData(self,num):
        self.c.execute( "DELETE FROM receipt WHERE id = ?",(num,))

    def GetData(self):
        self.c.execute("SELECT * FROM receipt ORDER BY id Asc")
        rows = self.c.fetchall()
        return rows

class TaskDBManager(DBBaseManager):
    def __init__(self):
        super(TaskDBManager, self).__init__()

    def CreateTable(self):
        self.c.execute("CREATE TABLE if not exists task (id TEXT ,date TEXT,direction INTEGER,distance INTEGER)")

    def StoreAll(self,data):
        for i in data:
            self.c.execute("INSERT INTO task VALUES (?,?,?,?)",(i[0],i[1],i[2],i[3]))
        self.conn.commit()

    def GetData(self):
        self.c.execute("SELECT * FROM task")
        return self.c.fetchall()

    def Clear(self):
        #FIXME:DELETE what?
        self.c.execute("DELETE FROM task")
        self.conn.commit()

if __name__ == '__main__':
    D = TaskDBManager()
    D.CreateTable()
    D.c.execute("SELECT * FROM task")
    print D.c.fetchall()

    D = DBManager()
    D.CreateTable()
    if len(sys.argv) != 2:
        print "====wrong input : should be==== \n DBManager.py [taxid]"
        sys.exit(1)

    D.c.execute("SELECT COUNT(*) FROM receipt")
    print "=====Total : ",D.c.fetchone(),"====="
    D.c.execute("SELECT * FROM receipt WHERE taxid = ? ORDER BY id Asc",(sys.argv[1],))
    rows = D.c.fetchall()
    revenue = {}
    for row in rows:
        if str(row[1])[:6] not in revenue:
            revenue[ str(row[1])[:6] ] = row[2]
        else:
            revenue[ str(row[1])[:6] ] += row[2]
    print '======Monthly Revenue======'
    for key in revenue:
        print '{}  :  {}'.format(key,revenue[key])


