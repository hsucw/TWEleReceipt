import datetime



def modifyReceiptNum( receipt, delta ):
    receipt_eng = receipt[0:2]
    receipt_num = int(receipt[2:10])
    receipt_num += int(delta)
    return receipt_eng + str(receipt_num)


def modifyDate( date, delta):
    year, month, day = date.split('/')
    iso_date = datetime.date(int(year) + 1911, int(month), int(day))
    iso_date += datetime.timedelta(int(delta))
    date_return = u"{0}/{1:02d}/{2:02d}".format(iso_date.year - 1911, iso_date.month, iso_date.day)
    return date_return