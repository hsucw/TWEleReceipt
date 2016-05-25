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
                print "INSERT INTO receipt VALUES ('{}','{}',{})".format(key,data[key][0],data[key][1])
                self.c.execute("INSERT INTO receipt VALUES ('{}','{}',{})".format(key,data[key][0],data[key][1]))
                
        self.conn.commit()

if __name__ == '__main__':
    D = DBManager()
    D.CreateTable()
    D.c.execute("SELECT COUNT(*) FROM receipt")
    print "=====Total : ",D.c.fetchone(),"====="
    D.c.execute("SELECT * FROM receipt")
    print D.c.fetchall()
