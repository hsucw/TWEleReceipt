import datetime


def TimeConvert(date, day_delta):

    someday = datetime.datetime.strptime(str(int(date[0:3])+1991)+date[3:], "%Y/%m/%d")

    someday = someday + datetime.timedelta(days=day_delta)
    return str(int(someday.strftime("%Y/%m/%d")[0:4])-1991)+someday.strftime("%Y/%m/%d")[4:]

if __name__ == "__main__":
    print(TimeConvert("105/08/10", 1))
