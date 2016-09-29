from Connector import Connector
from DBManager import DBManager
from TimeConvert import TimeConvert

import socket
import json
import logging as log
import sys
import re
import thread

class TaskSolver(object):
    def __init__(self):
        self.tasks = []
        self.dbmgr = DBManager()
        self.c = Connector()
        self.data = ""
        self.receipt_done = dict()
    def getTasks(self, task):
        """ getTasks """
        pass

    def Query(self, receipt, receipt_date):

        res = None

        errorCount = 10;

        while res is None and errorCount > 0:
            errorCount -= 1
            print errorCount
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

            with open("out.html" , "w") as outFd:
                outFd.write(self.c.body)

        if not self.c.info:
            return False
        else:
            print("===[Query Result]===")
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


        while (abs(start_receipt_num - current_receipt_num) < distance):

            success = self.Query(current_receipt, date)
            print "current " + current_receipt
            if success is True:
                current_receipt = self._modify_receipt_num(current_receipt,direction)
                current_receipt_num = int(current_receipt[2:10])
                success_count += 1
            elif success is False:
                break
            else:
                log.error('main loop unusually break')
                sys.exit(1)


        result = {
                'success':success_count,
                'error':distance-success_count,
                }
        receipt = self.receipt_done
        return_data = {'result':result,'receipt':self.receipt_done,'task':task_dict}

        return return_data

    def start_solver(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('127.0.0.1', 5555)
        print  'connecting to {} '.format(server_address)
        sock.connect(server_address)
        while True:
            task_str = sock.recv(512)
            task = json.loads(task_str)
            if task['action'] == "solve":
                task_dict = task['task']
                print "Recieve task : {}".format(task_dict)
                result = solver.solve_task(task_dict)
                print "send : \n{}".format(result)
                sock.sendall(json.dumps(result))
                print "Task done!!"
            elif task['action'] == "close":
                sock.close()
                break


if __name__ == '__main__':
    """ give a guess for id & date"""
    log.basicConfig(level=log.INFO)
    solver = TaskSolver()
    solver.start_solver()
    # solver.solve_task({'receipt':'KA13455018','date':'105/08/14','direction':1,'distance':100})

