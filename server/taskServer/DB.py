from models import Task, Receipt, TaskStatistics
import logging as log
import json
import thread
import time
from datetime import datetime, timedelta, date
import hashlib
from utils.Exceptions import DateOverFlowError, TaskAlreadyExistsError, DateOutOfRangeError

def taskTimeOut( delay, id ):
    time.sleep( delay )
    task = Task.objects.filter( id=id )
    if task:
        task[0].queued = False
        task[0].save()

def updateTask(targetTask):
    res = Task.objects.filter(id=targetTask['id'])
    if len(res)==1:
        task = res[0]
        task.queued = False
        task.todo = targetTask['todo']
        task.date = targetTask['date']
        task.succ = targetTask['succ']
        task.fail_cnt = targetTask['fail_cnt']
        if task.succ == task.distance or \
            task.fail_cnt >= 5:
            task.solved = True
        task.save()
        log.info("update task:{}".format(task))
    else:
        log.info("cannot find target task")

def getTask():

    tasks = Task.objects.filter( queued=False )

    log.info( "Tasks remain : {}" .format( len( tasks ) ))

    if Task.objects.filter(solved=False, queued=False):

        task = Task.objects.filter(solved=False, queued=False)[0]
        task.queued = True
        task.save()
        thread.start_new_thread( taskTimeOut, (30, task.id))
        task = task.as_json()
        task['result'] = 'success'
        log.info( "task send to client : {}".format(task) )

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
        log.info("Cannot add task, dateOverToday:{}".format(tskDate.date()))
        return

    #if len( Task.objects.filter(receipt = task['receipt']) ) == 0 :
    try:
        Task.objects.create(
            receipt = task['receipt'],
            date = task['date'],
            date_guess = task['date_guess'],
            direction = task['direction'],
            distance = task['distance'],
        )
    except Exception, e:
        log.error( str(e) )
        #traceback.print_exc(file=sys.stdout)
        log.info("Cannot add Task")
        # should not use error
        #raise TaskAlreadyExistsError(task)

    return

def reportTask( taskReport ):
    task = taskReport['task']
    updateTask(task)

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

    for receipt, vals in receipts.iteritems():
        Receipt.objects.create(
            receipt = receipt,
            date =  vals[0],
            money = vals[1],
            taxid = vals[2]
        )

    return

log.basicConfig(level=log.DEBUG)

