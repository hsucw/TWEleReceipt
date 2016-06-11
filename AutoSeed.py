from TaskDBManager import TaskDBManager
from DBManager import DBManager

taskdbmanager = TaskDBManager()
dbmanager = DBManager()

rows = dbmanager.GetData()

for i in range(len(rows)-1):
    if int(str(rows[i+1][0])[2:] ) - int(str(rows[i][0])[2:] ) > 2 :
        print "add seed : {} & {}".format( str(rows[i][0])[:2] + str(int(str(rows[i][0])[2:] )+1) , str(rows[i+1][0])[:2] + str(int(str(rows[i+1][0])[2:] )-1) )
        taskdbmanager.StoreAll([(str(rows[i][0])[:2] + str(int(str(rows[i][0])[2:] )+1),str(rows[i][1]),1,100),(str(rows[i+1][0])[:2] + str(int(str(rows[i+1][0])[2:] )-1),str(rows[i+1][1]),-1,100)])
