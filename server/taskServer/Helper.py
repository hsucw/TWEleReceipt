from datetime import datetime, timedelta

def modifyReceiptNum( receipt, delta ):
    receipt_eng = receipt[0:2]
    receipt_num = int(receipt[2:10])
    receipt_num += int(delta)
    return receipt_eng + str(receipt_num)


def modifyDate( date, delta):
    newDate = datetime.strptime(date, "%Y/%m/%d")
    newDate = newDate + timedelta(days=delta)
    return newDate.strftime("%Y/%m/%d")


