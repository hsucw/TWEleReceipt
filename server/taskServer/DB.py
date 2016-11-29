from models import Task, Receipt, TaskStatistics
import logging
import json
import thread
import time
from datetime import datetime, timedelta, date
import hashlib
from utils.Exceptions import DateOverFlowError, TaskAlreadyExistsError, DateOutOfRangeError
from django.db import IntegrityError
import random

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

    tasks = Task.objects.filter( queued=False, solved = False ).order_by('-fail_cnt')
    dblog.info( "Tasks remain : {}" .format( len( tasks ) ))

    if tasks:
        task = tasks[0]
        task.queued = True
        task.save()
        thread.start_new_thread( taskTimeOut, (30, task.id))
        task = task.as_json()
        task['result'] = 'success'
        dblog.debug( "task send to client : {}".format(task) )

        return json.dumps( task )
    else:
        return json.dumps( { "result":"error" } )

def addTaskWithTwoDirection( task ):

    addTask( task )
    task['direction'] = -task['direction']
    task['receipt']= task['receipt'][:2]+str(int(task['receipt'][2:])+task['direction']*task['distance'])
    addTask( task )

    return

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

def reportTask( taskReport ):
    task = taskReport['task']

    statistics = taskReport['result']
    t = Task.objects.filter( id=task['id'] )
    if t:
        t=t[0]
        TaskStatistics.objects.create(
            task = t,
            time = statistics['time'],
            success = statistics['success'],
            error = statistics['error'],
            distance = taskReport['task']['distance'],
            rps = taskReport['task']['distance']/statistics['time']
        )

    return

def storeData( receipts ):
    dblog.debug("store data: {}".format(receipts))
    for receipt, vals in receipts.iteritems():
        Receipt.objects.get_or_create(
            receipt = receipt,
            date =  vals[0],
            money = vals[1],
            taxid = vals[2]
        )
    return

