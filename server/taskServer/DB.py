from models import Task, Receipt, TaskStatistics
import logging as log
import json
import thread
import time
import datetime
import hashlib
from utils.Exceptions import DateOverFlowError, TaskAlreadyExistsError, DateOutOfRangeError

def taskTimeOut( delay, id ):
    time.sleep( delay )
    task = Task.objects.filter( id=id )
    if task:
        task[0].queued = False
        task[0].save()

def getTask():

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
    addTask( task )

    return

def addTask( task ):

    date = datetime.date( 1911+int(task['date'][:3]), int(task['date'][4:6]), int(task['date'][7:9]) )

    if date > datetime.date.today():
        raise DateOverFlowError(date)

    hash = hashlib.sha1()
    hash.update( (task['receipt']/100) + task['date'] + task['direction'] )
    hashString = hash.digest()

    if len( Task.objects.filter (
                               hash = hashString
                           ) ) == 0 :
        Task.objects.create(
            receipt = task['receipt'],
            date = task['date'],
            date_guess = task['date_guess'],
            direction = task['direction'],
            distance = task['distance'],
            hash = hashString
        )
    else:
        raise TaskAlreadyExistsError(task)

    return

def reportTask( taskReport ):
    task = taskReport['task']
    statistics = taskReport['result']
    task = Task.objects.filter( id=task['id'] )
    if task:
        task = task[0]
        task.solved = True
        task.save()
        TaskStatistics.objects.create(
            task = task,
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

