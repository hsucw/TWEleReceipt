import datetime

def TimeConvert(date,delta):
    someday = datetime.datetime.strptime(str(int(date[0:3])+1991)+date[3:],
"%Y/%m/%d")
    someday = someday + datetime.timedelta(days = delta)
    return str(int(someday.strftime("%Y/%m/%d")[0:4])-1991)+someday.strftime("%Y/%m/%d")[4:]
