from TaskDBManager import TaskDBManager 

taskdbmanager = TaskDBManager()

while True:
    try:
        print "Enter Seed:"
        number = raw_input("number:")
        if len(number) != 10:
            print "format wrong"
            continue
        date = raw_input("date:")
        if len(date) != 9 or date[3] != '/' or date[6] != '/':
            print "format wrong"
            continue
        taskdbmanager.StoreAll([(number,date,1,100),(number,date,-1,100)])
    except KeyboardInterrupt:
        print "\n~~~~~Bye~~~~~"
        break
