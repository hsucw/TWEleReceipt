from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from utils.Exceptions import TaskAlreadyExistsError, DateOverFlowError
from django.conf import settings

import logging as log
import DB
import json
import Helper
import urlparse
import datetime
import traceback
import sys



log.basicConfig(level=log.DEBUG)


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

    #date_max = date + datetime.timedelta( days=settings.DATE_RANGE )
    #date_min = date - datetime.timedelta( days=settings.DATE_RANGE )
    #retTask[ 'date_max' ] = date_max.strftime("%Y/%m/%d")
    #retTask[ 'date_min' ] = date_min.strftime("%Y/%m/%d")

    log.debug( "{}, {} has been received".format( retTask['receipt'] , retTask['date'] ) )

    return retTask



# add task by client submitted qr code
def addTask( request ):

    try:
        if request.method == 'POST':

            task = urlparse.parse_qs( request.body )
            log.debug(task)
            task = __repackTask__( task )

            log.debug(task)
            DB.addTaskWithTwoDirection( task )

    except DateOverFlowError:
        log.error( 'date out of range' )
        return HttpResponse( 'date out of range' )
    except TaskAlreadyExistsError:
        log.error( 'receipt already in record' )
        return HttpResponse( 'receipt already in record' )
    except Exception, e:
        log.error( str(e) )
        traceback.print_exc(file=sys.stdout)
        return HttpResponse( 'add Task Failed' )


    return HttpResponse( 'add Task Success' )





# receive task report from client
@csrf_exempt
def reportTask( request ):
    if request.method == 'POST':

        log.debug( request.body )

        taskReport = json.loads( request.body )
        queryResult = taskReport['result']

        DB.reportTask( taskReport )
        if queryResult['success'] > 0:
            DB.storeData( taskReport['receipt'] )

        trend = queryResult['guess']
        fails = queryResult['fail']
        task = taskReport['task'].copy()
        """
        if task['fail_cnt'] < 3:
            if abs(trend) > 0.5:
                if trend >= 0:#query this, next
                    genTask(,)
                else:# query this
                    genTask()

            else:#many slice
                print "sad"
        else:
        """


        # continue the next chunk
        if queryResult['success'] == 100:
            DB.storeData( taskReport['receipt'] )

            task = taskReport['task'].copy()
            task['fail_cnt'] = 0
            task['receipt'] = Helper.modifyReceiptNum(
                queryResult['lastSuccessReceipt'],
                task['direction']
            )
            DB.addTask( task )
        else:

            if taskReport['task']['fail_cnt'] == 0:

                originTask = taskReport['task'].copy()
                task = taskReport['task'].copy()
                task['fail_cnt'] += 1
                task['date_guess'] = 1
                task['date'] = Helper.modifyDate(originTask['date'], 1)
                task['receipt'] = Helper.modifyReceiptNum(queryResult['lastSuccessReceipt'], task['direction'])
                DB.addTask( task )

                task = taskReport['task'].copy()
                task['fail_cnt'] += 1
                task['date_guess'] = -1
                task['date'] = Helper.modifyDate(originTask['date'], -1)
                task['receipt'] = Helper.modifyReceiptNum(queryResult['lastSuccessReceipt'], task['direction'])
                DB.addTask( task )

            elif taskReport['task']['fail_cnt'] > 5:
                log.info( 'a task was terminated due to fail_cnt limit exceed')

            else:
                task = taskReport['task'].copy()
                task['fail_cnt'] += 1
                task['date'] = Helper.modifyDate(
                    task['date'],
                    task['date_guess']
                )
                DB.addTask( task )

        return HttpResponse('report recorded')

    else:
        log.info( "a client send an invalid request {}".format( request.body ) )
        return HttpResponse( 'Invalid Request' )


