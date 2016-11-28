tfrom django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from utils.Exceptions import TaskAlreadyExistsError, DateOverFlowError
from django.conf import settings

import logging
import DB
import json
import Helper
import urlparse
import datetime
import traceback
import sys


logging.basicConfig(level=logging.INFO)
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

    retTask[ 'date_guess' ] = 0
    retTask[ 'direction' ] = 1
    retTask[ 'distance' ] = settings.RECEIPT_DISTANCE
    retTask[ 'fail_cnt' ] = 0


    srvlog.info( "{}, {} has been received".format( retTask['receipt'] , retTask['date'] ) )

    return retTask



#@csrf_exempt
# add task by client submitted qr code
def addTask( request ):

    try:
        if request.method == 'POST':

            task = urlparse.parse_qs( request.body )
            srvlog.debug(task)
            task = __repackTask__( task )

            srvlog.debug(task)
            DB.addTaskWithTwoDirection( task )

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


    return HttpResponse( 'add Task Success' )





# receive task report from client
@csrf_exempt
def reportTask( request ):
    if request.method == 'POST':

        srvlog.debug( request.body )

        taskReport = json.loads( request.body )
        queryResult = taskReport['result']

        DB.reportTask( taskReport )

        if queryResult['success'] > 0:
            DB.storeData( taskReport['receipt'] )

        guess = queryResult['guess']
        fails = queryResult['fail']
        curTask = taskReport['task'].copy()

        direction = curTask['direction']
        distance = curTask['distance']
        todo = curTask['todo']

        if guess > 0.2:
            change = True
        else:
            change = False

        if curTask['succ']*1.0/distance > 0.3:
            genNew = True
        else:
            genNew = False

        newDate = Helper.modifyDate(curTask['date'], 1*direction)
        newReceipt = Helper.modifyReceiptNum(curTask['receipt'], direction*distance)

        if change and genNew:
            newTask = curTask.copy()
            newTask['date'] = newDate
            newTask['fail_cnt'] = 0
            newTask['todo'] = []
            newTask['receipt'] = newReceipt
            DB.addTask(newTask)

            curTask['fail_cnt']+= 3
            curTask['todo']=','.join(fails)
            DB.updateTask(curTask)

            oldTask = curTask.copy()
            oldTask['date'] = newDate
            DB.addTask(oldTask)

        elif not change and genNew:
            newTask = curTask.copy()
            newTask['fail_cnt'] = 0
            newTask['todo'] = []
            newTask['receipt'] = newReceipt
            DB.addTask(newTask)

            curTask['fail_cnt']+= 2
            curTask['todo']=','.join(fails)
            DB.updateTask(curTask)

        elif change and not genNew:
            curTask['fail_cnt']+= 3
            curTask['todo']=','.join(fails)
            DB.updateTask(curTask)

            oldTask = curTask.copy()
            oldTask['date'] = newDate
            DB.addTask(oldTask)

        else: #not change and not genNew
            curTask['fail_cnt']+= 1
            curTask['todo']=','.join(fails)
            DB.updateTask(curTask)

        return HttpResponse('report recorded')

    else:
        srvlog.info( "a client send an invalid request {}".format( request.body ) )
        return HttpResponse( 'Invalid Request' )


