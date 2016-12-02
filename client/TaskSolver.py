from Connector import Connector
import socket
import json
import logging as log
import sys

import re
import thread
import time
import requests

DEBUG_LEVEL = log.DEBUG

def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s (%s/%s)\r' % (bar, percents, '%', suffix, count, total))
    sys.stdout.flush()  # As suggested by Rom Ruben


class TaskSolver(object):
    def __init__(self):
        self.tasks = []
        self.server = "http://192.168.0.234:8000"
        self.getTaskUrl = "/api/getTask/"
        self.c = Connector()
        self.data = ""
        self.receipt_done = dict()
    def getTasks(self, task):
        """ getTasks """
        pass

    def Query(self, receipt, receipt_date):

        res = None
        while res is None:
            if not self.c.session_valid:
                #del self.c
                #self.c = Connector()
                self.c.resolveImg()
            self.c.setPostData(receipt, receipt_date )
            self.c.postForm( self.c.postPath )
            res = self.c.getInfo()
            with open("out.html" , "w") as outFd:
                outFd.write(self.c.body)

        if not self.c.info:
            return False
        else:
            #log.info("===[Query Result]===")
            receipt = self.c.info
            receipt['money'] = receipt['money'].replace(',','')
            #for k,r in receipt.iteritems():
            #    print k+":\t\t"+r

            self.receipt_done[self.c.info['id']] = (receipt['date'],receipt['money'],receipt['taxid'])
            return True

    def _modify_receipt_num(self, receipt, delta):
        receipt_eng = receipt[0:2]
        receipt_num = int(receipt[2:10])
        receipt_num += delta
        return receipt_eng+str(receipt_num)


    def solve_task(self, task_dict):

        self.receipt_done = {}
        density = []
        fails = []
        distance = task_dict['distance']
        date = task_dict['date']
        direction = task_dict['direction']
        receipt = task_dict['receipt']

        log.debug(task_dict)

        if task_dict['todo'] == None:
            log.info("resolve new task")
            init_alpha = receipt[:2]
            number = int(receipt[2:])
            if direction == 1:
                num_list = range(number,number+direction*distance)
            elif direction == -1:
                # XX12345600, -1  -> ~600, 599, 598, 597
                num_list = list(reversed(range(number, number+distance)))
            else:
                log.error("Unknown distance")
                exit(1)

            receipt_queue = [init_alpha+"{:08d}".format(x) for x in num_list]
        else: # do todo_list
            log.info("redo todo list")
            receipt_queue = task_dict['todo'].split(",")

        lastSuccessReciept = ""
        total = len(receipt_queue)

        for query_rcpt in receipt_queue:
            #log.debug("{}".format(query_rcpt))
            progress(cnt, total, query_rcpt)
            res = self.Query(query_rcpt, date)
            if res is not True:
                fails.append(query_rcpt)



        result = {
                'success': len(receipt_queue) - len(fails),
                'error':len(fails),
                'fail':fails,
                }
        receipt = self.receipt_done
        return_data = {'result':result,'receipt':self.receipt_done,'task':task_dict}

        return return_data


    def start_solver(self):

        while True:
            try:
                task = requests.get(self.server+self.getTaskUrl)
            except :
                log.error( "connection to server failed... retry after 10 secs" )
                continue

            log.debug( "Recieve task : {}".format ( task.text ) )
            time_start = time.time()
            task_dict = json.loads( task.text )

            if task_dict['result'] == 'error':
                log.error( 'Server currently down or no tasks, wait 10 secs' )
                time.sleep( 10 )
                continue


            result = solver.solve_task(task_dict)

            time_delta = time.time() - time_start
            result['result']['time'] = time_delta

            #log.info( "\n=====================statistics===================\n" )
            receiptHasdata = result['result']['success']
            receiptFailed = result['result']['error']
            #log.info( "receipt / s : {}\n".format( task_dict['distance']/time_delta ) )
            #log.info( "average time consume for each receipt : {}s\n".format( time_delta/task_dict['distance'] ) )
            #log.info( "hit rate ( receipt has data / total receipt ) : {}%\n".format( receiptHasdata / task_dict['distance']  * 100) )
            #log.info( "correct receipt / sec : {}\n".format( receiptHasdata/time_delta ) )
            #log.info( "missing rate : {}%\n".format( receiptFailed/task_dict['distance'] ) )
            #log.info( "\n==================================================\n" )

            log.info( "send : \n{}".format(result) )
            requests.post(self.server+'/api/reportTask/', data=json.dumps( result ))




if __name__ == '__main__':


    debugLevel = 'INFO'

    for argv in sys.argv:
        if argv[:5] == '--log':
            debugLevel = argv[5:]

    debugLevel = debugLevel.lower()

    if debugLevel == 'warn':
        DEBUG_LEVEL = log.WARN
    elif debugLevel == 'debug':
        DEBUG_LEVEL = log.DEBUG
    elif debugLevel == 'info':
        DEBUG_LEVEL = log.INFO
    elif debugLevel == 'error':
        DEBUG_LEVEL = log.ERROR

    if DEBUG_LEVEL == log.INFO:
        print ( "DEBUG LEVEL: INFO" )
    elif DEBUG_LEVEL == log.WARN:
        print ( "DEBUG LEVEL: WARN" )
    elif DEBUG_LEVEL == log.DEBUG:
        print ("DEBUG LEVEL: DEBUG")
    elif DEBUG_LEVEL == log.ERROR:
        print ("DEBUG LEVEL: ERROR")

    log.basicConfig(level=DEBUG_LEVEL)
    solver = TaskSolver()
    solver.start_solver()
    # solver.solve_task({'receipt':'KA13455018','date':'105/08/14','direction':1,'distance':100})

