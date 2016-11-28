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

def updateTask(targetTask):
    t = Task.objects.get(id=targetTask['id'])
    #res = Task.objects.filter(id=targetTask['id'])
    #if len(res)==1:
    if t is not None:
        t.queued = False
        t.todo = targetTask['todo']
        t.date = targetTask['date']
        t.succ = targetTask['succ']
        t.fail_cnt = targetTask['fail_cnt']
        if t.succ >= t.distance or \
            t.fail_cnt >= 5:
            t.solved = True
        try:
            t.save()
            dblog.info("update task:{} {} {} {}".format(t.id,t.receipt,t.date, t.fail_cnt))
        except IntegrityError:
            t.delete()
            dblog.info("delete task because of duplicated")

    else:
        addTask(targetTask)
        dblog.info("cannot find target task")

def getTask():

    tasks = Task.objects.filter( queued=False, solved = False )

    dblog.info( "Tasks remain : {}" .format( len( tasks ) ))

    if Task.objects.filter(solved=False, queued=False):

        task_list = Task.objects.filter(solved=False, queued=False)
        pick_index = random.randint(0,len(task_list)-1)
        task = task_list[pick_index]
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
        dblog.info("Cannot add task, dateOverToday:{}".format(tskDate.date()))
        return
    if task['fail_cnt'] >= 5:
        dblog.info("Cannot add task, fail count limit")
        return

    #if len( Task.objects.filter(receipt = task['receipt']) ) == 0 :
    try:
        Task.objects.get_or_create(
            receipt = task['receipt'],
            date = task['date'],
            date_guess = task['date_guess'],
            direction = task['direction'],
            distance = task['distance'],
            fail_cnt = task['fail_cnt'],
        )
    except Exception, e:
        dblog.error( str(e) )
        #traceback.print_exc(file=sys.stdout)
        dblog.info("Cannot add Task, already exists")
        # should not use error
        #raise TaskAlreadyExistsError(task)

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
    dblog.info("store data: {}".format(receipts))
    for receipt, vals in receipts.iteritems():
        Receipt.objects.get_or_create(
            receipt = receipt,
            date =  vals[0],
            money = vals[1],
            taxid = vals[2]
        )
    return

