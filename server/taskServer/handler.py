from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from utils.Exceptions import TaskAlreadyExistsError, DateOverFlowError
from django.conf import settings
from django.db import IntegrityError


import logging
import DB
import json
import Helper
import urlparse
import datetime
import traceback
import sys


logging.basicConfig(level=logging.DEBUG)
srvlog = logging.getLogger("SEVR")

# send the task to client
def getTask( request ):

    task = DB.getTask()


    return HttpResponse( task  , content_type='application/json')



def __repackTask__( task ):

    retTask = {}

    retTask[ 'receipt' ] = task['receipt'][0]
    retTask[ 'receipt' ] = retTask['receipt'][:2] + str( int(int(retTask[ 'receipt' ][2:]) / 100) * 100  ).zfill(8)

    #handle 2016-10-15, 105-10-15 ==> 2016/10/15
    y,m,d = task['date'][0].replace('-','/').split("/")
    if int(y) < 1000:
        y = str(int(y)+1911)
    retTask[ 'date'] = '/'.join((y,m,d))
    date = datetime.date( int(y),int(m),int(d) )

    retTask[ 'direction' ] = 1
    retTask[ 'distance' ] = settings.RECEIPT_DISTANCE
    retTask[ 'fail_cnt' ] = 0


    srvlog.info( "{}, {} has been received".format( retTask['receipt'] , retTask['date'] ) )

    return retTask



@csrf_exempt
# add task by client submitted qr code
def addTask( request ):
    token = ''
    try:
        if request.method == 'POST':

            task = urlparse.parse_qs( request.body )
            srvlog.debug(task)
            task = __repackTask__( task )

            srvlog.debug(task)
            token = DB.addTaskWithTwoDirection( task )

    except DateOverFlowError:
        srvlog.error( 'date out of range' )
        return HttpResponse( 'date out of range' )
    except TaskAlreadyExistsError:
        srvlog.error( 'receipt already in record' )
        return HttpResponse( 'receipt already in record' )
    except Exception, e:
        srvlog.error( str(e) )
        traceback.print_exc(file=sys.stdout)
        return HttpResponse( 'add Task Failed' )


    url = settings.SERVER_URL + 'showStatistics/' + token

    return HttpResponse( 'add Task Success<br>' + '<a href="{}">{} </a>'.format( url, url ))





# receive task report from client
@csrf_exempt
def reportTask( request ):
    if request.method == 'POST':

        srvlog.debug( request.body )

        taskReport = json.loads( request.body )
        queryResult = taskReport['result']
        task = taskReport['task']
        direction = task['direction']
        distance = task['distance']
        todo = task['todo']
        fails = queryResult['fail']

        curDate =  task['date']
        curReceipt = task['receipt']
        curTask = DB.getTaskObject(curReceipt,curDate)

        nextDate = Helper.modifyDate(task['date'], 1*direction)
        nextReceipt = Helper.modifyReceiptNum(task['receipt'], direction*distance)

        lastDate = Helper.modifyDate(task['date'], 1*direction)
        lastReceipt = Helper.modifyReceiptNum(task['receipt'], -1*direction*distance)
        lastTask = DB.getTaskObject(lastReceipt,lastDate)

        DB.reportTask( taskReport )
        genNew = False
        if queryResult['success'] > 0:
            DB.storeData( taskReport['receipt'] )
            genNew = True

        if genNew:
            nextTask = DB.createTaskObject(nextReceipt,curDate, direction)
            if nextTask:#fail_cnt = 0
                nextTask.save()
                srvlog.debug("create new Task {} {}".format(nextReceipt,curDate))

            if lastTask:
                lastTask.fail_cnt = 5
                lastTask.solved = True
                lastTask.save()
                srvlog.debug("close lastTask {}".format(lastTask.as_json()))

            if curTask:
                if curTask.fail_cnt == 0:
                    curTask.fail_cnt=4
                else:
                    curTask.fail_cnt =5
                    curTask.solved = True
                curTask.succ = distance - len(fails)
                curTask.todo = ','.join(fails)
                curTask.save()
                srvlog.debug("update curTask todo {}".format(curTask.as_json()))

        else:
            if curTask: #First fail
                if curTask.fail_cnt == 0:
                    curTask.fail_cnt = 4
                    curTask.date = nextDate
                else:
                    curTask.solved = True
                curTask.todo = ','.join(fails)
                curTask.succ = distance - len(fails)
                try:
                    curTask.save()
                    srvlog.debug("move curTask to next date {}".format(curTask.as_json()))
                except IntegrityError:
                    srvlog.warn("Task already exists")
                    curTask.date = curDate
                    curTask.solved = True
                    curTask.save()

            if lastTask:
                if lastTask.solved:
                    lastTask.date = nextDate
                    lastTask.fail_cnt=3
                lastTask.save()
                srvlog.debug("update lastTask to next date {}".format(curTask.as_json()))

        try:
            curTask.queued = False
            srvlog.debug("update curTask {}".format(curTask.as_json()))
        except Exception, e:
            srvlog.error("*_*_*_: No Such Current Task {} {} {}".format(curReceipt, curDate, direction))
            srvlog.error(e)
            return HttpResponse('no such record')

        return HttpResponse('report recorded')

    else:
        srvlog.info( "a client send an invalid request {}".format( request.body ) )
        return HttpResponse( 'Invalid Request' )


