import sqlite3
import sys

class DBManager(object):
    def __init__(self):
        self.conn = sqlite3.connect("DB/receipt.db")
        self.c = self.conn.cursor()
    def CreateTable(self):
        self.c.execute("CREATE TABLE if not exists receipt (id TEXT, date TEXT, money INTEGER, taxid TEXT)")
    def StoreData(self,data):
        for key in data: 
            self.c.execute("SELECT * FROM receipt WHERE id = '{}'".format(key))
            if self.c.fetchone() == None:
                
                self.c.execute("INSERT INTO receipt VALUES ('{}','{}',{},'{}')".format(key,data[key][0],data[key][1],str(data[key][2])).zfill(8))
                
        self.conn.commit()
    def Findid(self,num):
        self.c.execute("SELECT * FROM receipt WHERE id = '{}'".format(num))
        if self.c.fetchone() == None:
            return False
        else:
            return True
    def DeleteData(self,num):
        self.c.execute( "DELETE FROM receipt WHERE id = '{}'".format(num))
         
    def GetData(self):
        self.c.execute("SELECT * FROM receipt ORDER BY id Asc")
        rows = self.c.fetchall()
        return rows
if __name__ == '__main__':
    D = DBManager()
    D.CreateTable()
    if len(sys.argv) != 2:
        print "====wrong input : should be==== \n DBManager.py [taxid]"
        sys.exit(1)
    
    D.c.execute("SELECT COUNT(*) FROM receipt")
    print "=====Total : ",D.c.fetchone(),"====="
    D.c.execute("SELECT * FROM receipt WHERE taxid = '{}' ORDER BY id Asc".format(sys.argv[1]))
    rows = D.c.fetchall()
    revenue = {}
    for row in rows:
        print row
        if str(row[1])[:6] not in revenue:
            revenue[ str(row[1])[:6] ] = row[2]
        else:
            revenue[ str(row[1])[:6] ] += row[2]
    print '======Monthly Revenue======'
    for key in revenue:
        print '{}  :  {}'.format(key,revenue[key])
        
            
