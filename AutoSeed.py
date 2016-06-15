import sys


from TaskDBManager import TaskDBManager
from DBManager import DBManager


taskdbmanager = TaskDBManager()
dbmanager = DBManager()

rows = dbmanager.GetData()
cont=0
for i in range(len(rows)-1):
    if int(str(rows[i+1][0])[2:] ) - int(str(rows[i][0])[2:] ) != 1 and int(str(rows[i+1][0])[2:] ) - int(str(rows[i][0])[2:] ) != 2 :
        if str(rows[i][3]) == str(rows[i+1][3]):
            print 'missing interval : {}'.format(str(int(str(rows[i+1][0])[2:] ) - int(str(rows[i][0])[2:] )))
            cont+=1
        if int(str(rows[i+1][0])[2:] ) - int(str(rows[i][0])[2:] ) ==0:
            print 'delete repeat data'
            dbmanager.DeleteData(str(rows[i][0]))
            dbmanager.StoreData( {rows[i][0]:(rows[i][1],rows[i][2],rows[i][3])} )
        print "add seed : {} & {}".format( str(rows[i][0])[:2] + str(int(str(rows[i][0])[2:] )+1).zfill(8) , str(rows[i+1][0])[:2] + str(int(str(rows[i+1][0])[2:] )-1).zfill(8) )
        taskdbmanager.StoreAll([(str(rows[i][0])[:2] + str(int(str(rows[i][0])[2:] )+1).zfill(8),str(rows[i][1]),1,100),(str(rows[i+1][0])[:2] + str(int(str(rows[i+1][0])[2:] )-1).zfill(8),str(rows[i+1][1]),-1,100)])
print "missing interval : {}".format(str(cont))



