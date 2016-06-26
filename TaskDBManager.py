import sqlite3

class TaskDBManager(object):
    def __init__(self):
        self.conn = sqlite3.connect("DB/task.db")
        self.c = self.conn.cursor()

    def CreateTable(self):
        self.c.execute("CREATE TABLE if not exists task (id TEXT,date TEXT,direction INTEGER,distance INTEGER)")

    def StoreAll(self,data):
        for i in data:
            self.c.execute("INSERT INTO task VALUES ('{}','{}',{},{})".format(i[0],i[1],i[2],i[3]))
        self.conn.commit()

    def GetData(self):
        self.c.execute("SELECT * FROM task") 
        return self.c.fetchall()
    
    def Clear(self):
        self.c.execute("DELETE FROM task")
        self.conn.commit()

if __name__ == '__main__':
    D = TaskDBManager()
    D.CreateTable()
    D.c.execute("SELECT * FROM task")
    print D.c.fetchall()
