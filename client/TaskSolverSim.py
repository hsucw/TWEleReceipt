from Connector import Connector
import socket
import json
import logging as log
import sys

import re
import thread
import time
import requests
import random

DEBUG_LEVEL = log.DEBUG

class TaskSolver(object):
    def __init__(self):
        self.tasks = []
        self.server = "http://127.0.0.1:8000"
        self.getTaskUrl = "/api/getTask/"
        self.c = Connector()
        self.data = ""
        self.testsim = []
        self.receipt_done = dict()
    def getTasks(self, task):
        """ getTasks """
        pass

    def Query(self, receipt, receipt_date):

        res = None
        while res is None:
            if not self.c.session_valid:
                del self.c
                self.c = Connector()
                self.c.imgRslr.reportFail(self.c.imgCode, self.c.imgSHA)
                self.c.resolveImg()
            #log.info('[{}]Get Image {}:{}'.format(self.c.res.reason, self.c.tmp_file, self.c.imgCode))
            #log.info('{} and {}'.format(receipt , receipt_date))
            self.c.setPostData(receipt, receipt_date )
            self.c.postForm( self.c.postPath )
            #log.info('[{} {}]Post data'.format(self.c.res.status,self.c.res.reason))
            res = self.c.getInfo()


        if not self.c.info:
            return False
        else:
            log.info("===[Query Result]===")
            receipt = self.c.info
            receipt['money'] = receipt['money'].replace(',','')
            for k,r in receipt.iteritems():
                print k+":\t\t"+r

            self.receipt_done[self.c.info['id']] = (receipt['date'],receipt['money'],receipt['taxid'])
            return True

    def _modify_receipt_num(self, receipt, delta):
        receipt_eng = receipt[0:2]
        receipt_num = int(receipt[2:10])
        receipt_num += delta
        return receipt_eng+str(receipt_num)

    # Using success density
    def resultAnalysis(self, suc_density):
        # |max|>|min|: mostly success, otherwise, fail
        # 0 ~ 1: confidence

        min_den = min(suc_density)
        max_den = max(suc_density)
        total = len(suc_density)
        cov = max_den - min_den

        if suc_density[-1] > 0:
            p = 0.0
        else:
            p = 1.0

        return (p*cov/total)**2


    def genSimData(self,length):
        allpass = [1]*length
        allfail = [0]*length
        halftailfail = [1]*(length/2)+[0]*(length-(length/2))
        halfheadfail = [0]*(length/2)+[1]*(length-(length/2))

        listall = [allpass, allfail, halftailfail, halfheadfail]
        i = random.randint(0,3)

        return listall[i]


    def solve_task(self, task_dict):

        self.receipt_done = {}
        density = []
        fails = []
        distance = task_dict['distance']
        date = task_dict['date']
        direction = task_dict['direction']
        receipt = task_dict['receipt']

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

            receipt_queue = [init_alpha+str(x) for x in num_list]
        else: # do todo_list
            log.info("redo todo list")
            receipt_queue = task_dict['todo'].split(",")

        total = len(receipt_queue)
        cnt = 0

        self.testsim=self.genSimData(total)

        print receipt_queue

        for query_rcpt in receipt_queue:
            #log.info("task solving...{}/{}".format(cnt+1, total))

            # simulate
            if self.testsim[cnt] == 1:
                res = True
                self.receipt_done[query_rcpt] = (date,10,2)
            else:
                res = False

            if res is True:
                if len(density) != 0 and density[-1] > 0:
                    density.append(density[-1]+1)
                else:
                    density.append(1)
                lastSuccessReciept = query_rcpt
            else: # False Query
                fails.append(query_rcpt)
                if len(density) != 0 and density[-1] < 0:
                    density.append(density[-1]-1)
                else:
                    density.append(-1)
            cnt+=1

        if task_dict['todo'] == None:
            trend = self.resultAnalysis(density)
        else:
            trend = 0

        result = {
                'success':len(filter(lambda i:i > 0, density)),
                'error':len(filter(lambda i:i < 0, density)),
                'fail':fails,
                'guess':trend
                }
        task_dict['todo'] = None
        receipt = self.receipt_done
        task_dict['succ']+=result['success']
        return_data = {'result':result,'receipt':self.receipt_done,'task':task_dict}
        #time.sleep(3)
        return return_data


    def start_solver(self):

        while True:

            task = requests.get(self.server+self.getTaskUrl)
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

            log.info( "\n=====================statistics===================\n" )
            receiptHasdata = result['result']['success']
            receiptFailed = result['result']['error']
            log.info( "receipt / s : {}\n".format( task_dict['distance']/time_delta ) )
            log.info( "average time consume for each receipt : {}s\n".format( time_delta/task_dict['distance'] ) )
            log.info( "hit rate ( receipt has data / total receipt ) : {}%\n".format( receiptHasdata / task_dict['distance']  * 100) )
            log.info( "correct receipt / sec : {}\n".format( receiptHasdata/time_delta ) )
            log.info( "missing rate : {}%\n".format( receiptFailed/task_dict['distance'] ) )
            log.info( "\n==================================================\n" )

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

