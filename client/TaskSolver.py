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

class TaskSolver(object):
    def __init__(self):
        self.tasks = []
        self.server = "http://140.113.87.26:8000"
        self.getTaskUrl = "/api/getTask/"
        self.c = Connector()
        self.data = ""
        self.receipt_done = dict()
    def getTasks(self, task):
        """ getTasks """
        pass

    def Query(self, receipt, receipt_date):

        res = None

        noneCnt = 0

        while res is None and noneCnt < 30:
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
            noneCnt+=1
            with open("out.html" , "w") as outFd:
                outFd.write(self.c.body)



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

    def solve_task(self, task_dict):

        self.receipt_done = {}

        distance = task_dict['distance']
        date = task_dict['date']
        direction = task_dict['direction']
        receipt = task_dict['receipt']

        start_receipt = receipt
        start_receipt_num = int(start_receipt[2:10])
        current_receipt = start_receipt
        current_receipt_num = int(current_receipt[2:10])
        success_count = 0
        lastSuccessReciept = self._modify_receipt_num( current_receipt, -direction )

        while (abs(start_receipt_num - current_receipt_num) < distance):
            log.info("task solving..." + str( abs(start_receipt_num - current_receipt_num) + 1 ) +  '/' + str( distance ))
            success = self.Query(current_receipt, date)
            if success is True:
                current_receipt = self._modify_receipt_num(current_receipt,direction)
                current_receipt_num = int(current_receipt[2:10])
                success_count += 1
                lastSuccessReciept = current_receipt
            else:
                current_receipt = self._modify_receipt_num(current_receipt,direction)
                current_receipt_num = int(current_receipt[2:10])


        result = {
                'success':success_count,
                'error':distance-success_count,
                'lastSuccessReceipt': lastSuccessReciept
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

            log.info( "\n=====================statistics===================\n" )
            receiptHasdata = result['result']['success']
            receiptFailed = result['result']['error']
            log.info( "receipt / s : {}\n".format( task_dict['distance']/time_delta ) )
            log.info( "average time consume for each receipt : {}s\n".format( time_delta/task_dict['distance'] ) )
            log.info( "hit rate ( receipt has data / total receipt ) : {}%\n".format( receiptHasdata / task_dict['distance']  * 100) )
            log.info( "correct receipt / sec : {}\n".format( receiptHasdata/time_delta ) )
            log.info( "missing rate : {}%\n".format( receiptFailed/task_dict['distance'] ) )
            log.info( "\n==================================================\n" )

            log.debug( "send : \n{}".format(result) )
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

