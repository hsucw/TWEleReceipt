import sqlite3

class DBManager(object):
    def __init__(self):
        self.conn = sqlite3.connect("DB/receipt.db")
        self.c = self.conn.cursor()
    def CreateTable(self):
        self.c.execute("CREATE TABLE if not exists receipt (id TEXT, date TEXT, money INTEGER)")
    def StoreData(self,data):
        for key in data: 
            self.c.execute("SELECT * FROM receipt WHERE id == '{}'".format(key))
            if self.c.fetchone() == None:
                
                self.c.execute("INSERT INTO receipt VALUES ('{}','{}',{})".format(key,data[key][0],data[key][1]))
                
        self.conn.commit()
    def Findid(self,num):
        self.c.execute("SELECT * FROM receipt WHERE id == '{}'".format(num))
        if self.c.fetchone() == None:
            return False
        else:
            return True
    def GetData(self):
        self.c.execute("SELECT * FROM receipt ORDER BY id Asc")
        rows = self.c.fetchall()
        return rows
if __name__ == '__main__':
    D = DBManager()
    D.CreateTable()
    D.c.execute("SELECT COUNT(*) FROM receipt")
    print "=====Total : ",D.c.fetchone(),"====="
    D.c.execute("SELECT * FROM receipt ORDER BY id Asc")
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
        
            
