from models import Task, Receipt, TaskStatistics, ClientRequests
import logging
import json
import thread
import time
import threading
from subprocess import call, check_call
from datetime import datetime, timedelta, date
import os
import Helper
from django.forms import model_to_dict

logging.basicConfig(level=logging.INFO)
dblog = logging.getLogger("DB")

def taskTimeOut( delay, id ):
    time.sleep( delay )
    task = Task.objects.filter( id=id )
    if task:
        task[0].queued = False
        task[0].save()

def getTaskObject(rcpt, dt):
    #dblog.info("get object by {} {}".format(rcpt, dt))
    try:
        return Task.objects.get(receipt=rcpt, date=dt)
    except Exception, e:
        dblog.debug("*_*_*_*_*_*_* Cannot get object {} {}".format(rcpt, dt))
        dblog.debug(e)
        return None

def createTaskObject(rcpt, dt, dirtn):
    #dblog.info("create object by {} {}".format(rcpt, dt, dirtn))
    try:
        return Task.objects.create(receipt=rcpt, date=dt, direction=dirtn)
    except Exception, e:
        dblog.debug("*_*_*_*_*_*_* Cannot create object {} {} {}".format(rcpt,dt,dirtn))
        dblog.debug(e)
        return None


def getTask():

    tasks = Task.objects.filter( queued=False, solved = False ).order_by('fail_cnt')
    dblog.info( "Tasks remain : {}" .format( len( tasks ) ))

    if tasks:
        task = tasks[0]
        task.queued = True
        task.save()
        thread.start_new_thread( taskTimeOut, (150, task.id))
        task = task.as_json()
        task['result'] = 'success'
        dblog.debug( "task send to client : {}".format(task) )

        return json.dumps( task )
    else:
        return json.dumps( { "result":"error" } )

def addTaskWithTwoDirection( task ):

    token = Helper.idGenerator(10)

    addClientToken(token, task)

    addTask( task )
    task['direction'] = -task['direction']
    task['receipt']= task['receipt'][:2]+str(int(task['receipt'][2:])+task['direction']*task['distance'])
    addTask( task )



    return token

def addClientToken( token , task ):
    try:
        ClientRequests.objects.create(
            receipt = task['receipt'],
            date = task['date'],
            token = token
        )
    except Exception, e:
        dblog.error( str(e) )
        dblog.warn( 'A client token repeated' )

    return

def addTaskMultiTasks( task , turn=1 ):

    for i in range( turn ):

        task['receipt'] = Helper.modifyReceiptNum( task['receipt'] , task['direction']*task['distance'] )
        addTask( task )

    return

def genCSVFiles( taxId, dateString, token ):

    dblog.info( 'generating csv file ' + str(taxId)  )

    call( 'cd ../analysis && python gen_csv.py '+ str(taxId) , shell=True )



    dateNums = dateString.split( '/' )
    if len( dateNums[0] ) <= 3:
        dateNums[0] = str(int(dateNums[0]) + 1911)
    dateString = '/'.join( dateNums )

    date = datetime.strptime( dateString , "%Y/%m/%d" )

    for deltaDay in range( -3, 4 , 1 ):
        targetDate = date + timedelta( days = deltaDay )

        targetDateString = '{:03d}-{:02d}-{:02d}'.format( int(targetDate.year)-1911 , int(targetDate.month), int(targetDate.day) )


        docPath = './data/' + str(taxId) + '/' + targetDateString + '.csv'
        if os.path.exists( '../analysis/' + docPath[2:] ):
            call( 'cd ../analysis && python gen_data.py norm '+ docPath + ' 24' , shell=True )
            call( 'cd ../analysis && python gen_data.py freq ' + docPath + ' 20 40', shell=True )


    return

def getStatisticDataByToken( token ):

    status = checkAndUpdateClientRequestStatusByToken( token )

    if status < 0:
        if status == -1:
            dblog.warn( 'process under process' )
            return {
                'status': 'pending',
                'data': 'your request is under process'
            }
        elif status == -2:
            dblog.warn('token invalid')
            return {
                'status':'error',
                'data':'token invalid'
            }
        elif status == -3:
            dblog.warn('token not found')
            return {
                'status':'error',
                'data':'token not found'
            }

    taxId, date = getTaxIdAndDateByToken( token )

    if status > 0:
        return {
            'status': 'success',
            'data' : getCsvFileNamesByTokenAndDate( token , date ),
            'taxId' : taxId
        }


    if taxId is 0 or date is None:
        return {
            'status':'error',
            'data':'receipt provided invalid or still processing'
        }

    t = threading.Thread( target=genCSVFiles(taxId, date,token), args=(), kwargs={} )
    t.setDaemon( True )
    t.start()

    return {
        'status':'pending',
        'data':'your process is under process'
    }

def getCsvFileNamesByTokenAndDate( token , dateString ):
    date = datetime.strptime(dateString, "%Y/%m/%d")

    ret = []

    for deltaDay in range(-3, 4, 1):
        targetDate = date + timedelta(days=deltaDay)

        targetDateString = '{:03d}-{:02d}-{:02d}'.format(int(targetDate.year) - 1911, int(targetDate.month),
                                                         int(targetDate.day))
        ret.append( targetDateString  )
    return ret


def checkAndUpdateClientRequestStatusByToken( token ):

    try:
        clientRequests = ClientRequests.objects.filter(token=token)

        if clientRequests:
            clientRequest = clientRequests.values()[0]

            if clientRequest['previousRequestTime'] > 0:
                return 1

            elif clientRequest['previousRequestTime'] == 0:
                clientRequests.update(previousRequestTime= int(time.time()))

                return 0

        else:
            return -2

    except Exception, e:
        dblog.error( str(e) )

    return -3

def getTaxIdAndDateByToken( token ):

    try:
        clientRequests = ClientRequests.objects.filter( token=token )

        if clientRequests:
            clientRequest = clientRequests.values()[0]

            if clientRequest['taxId'] is not 0:
                return clientRequest['taxId'], clientRequest['date']

            receipt = clientRequest['receipt']
            date = clientRequest['date']

            if receipt and date:
                task = getTaskObject( receipt , date )
                task = model_to_dict( task )
                taskId = task['id']
                statistics = TaskStatistics.objects.filter( task=taskId )

                if statistics:
                    taxId = statistics.values()[0]['taxId']
                    clientRequest.update( taxId=taxId )
                    return taxId, date


    except Exception, e:
        dblog.error( str(e) )

    return 0, None

def addTask( task ):

    tskDate = datetime.strptime(task['date'],"%Y/%m/%d")
    if tskDate.date() > date.today():
        dblog.warn("Cannot add task, dateOverToday:{}".format(tskDate.date()))
        return
    if task['fail_cnt'] >= 5:
        dblog.warn("Cannot add task, fail count limit")
        return

    #if len( Task.objects.filter(receipt = task['receipt']) ) == 0 :
    try:
        Task.objects.create(
            receipt = task['receipt'],
            date = task['date'],
            direction = task['direction'],
            distance = task['distance'],
            fail_cnt = task['fail_cnt'],
        )
    except Exception, e:
        dblog.error( str(e) )
        #traceback.print_exc(file=sys.stdout)
        dblog.warn("Cannot add Task, already exists")

    return

def reportTask( taskReport , taxId = 0):

    task = taskReport['task']
    statistics = taskReport['result']

    if len ( taskReport['receipt'] ) > 0:
        for receipt, vals in taskReport['receipt'].iteritems():
            taxId = vals[2]
            break

    t = Task.objects.filter( id=task['id'] )
    if t:
        t=t[0]
        TaskStatistics.objects.create(
            task = t,
            time = statistics['time'],
            success = statistics['success'],
            error = statistics['error'],
            distance = taskReport['task']['distance'],
            rps = taskReport['task']['distance']/statistics['time'],
            taxId = taxId
        )

    return

def storeData( receipts ):
    dblog.debug("store data: {}".format(receipts))
    for receipt, vals in receipts.iteritems():
        try:
            Receipt.objects.get_or_create(
                receipt = receipt,
                date =  vals[0],
                money = vals[1],
                taxid = vals[2]
            )
        except ValueError:
            dblog.error("cannot save {} {}".format(receipt,vals))
    return

