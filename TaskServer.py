import socket
import json
import sys
import Queue
import logging as log
import thread
import time
import random
import json
import datetime

from TimeConvert import TimeConvert
from DBManager import DBManager, TaskDBManager

server_addr = ('127.0.0.1',5555)
log.basicConfig(level=log.DEBUG)

class TaskServer(object):
    def __init__(self):
        self.dbmanager = DBManager()
        self.taskdbmanager = TaskDBManager()
        self.current = Queue.Queue()
        self.task_queue = Queue.Queue()
        self.task_queue.put({'receipt':'KR66318287','date':'105/09/29','date_guess':-1,
            'direction':1,'distance':25, 'fail_cnt':0})

        self.task_queue.put({'receipt': 'KR66306250', 'date': '105/09/22', 'date_guess': -1,
                         'direction': -1, 'distance': 25, 'fail_cnt': 0})
    def send_and_receive(self, task_dict, clientsock):
        db = DBManager()
        try:
            action = {"action":"solve","task":task_dict}
            clientsock.sendall(json.dumps(action))
            print "task send {}".format(task_dict)


            task_report_json = clientsock.recv(65536)
        except socket.error as e:
            print "shit happened {}".format(e)
            time.sleep(60)

        task_report = json.loads(task_report_json)
        print task_report
        query_result = task_report['result']
        # some is success
        if query_result['success'] >0:
            db.StoreData(task_report['receipt'])

            print("some of them success")
            task = task_report['task'].copy()
            task['fail_cnt'] = 0
            task['receipt'] = self._modify_receipt_num(query_result['lastSuccessReceipt'],task['direction'])
            self.task_queue.put(task)

        # nothing is success(error at first)
        else:
            if task_report['task']['fail_cnt'] == 0:
                origin_task = task_report['task'].copy()
                task = task_report['task'].copy()
                task['fail_cnt'] += 1
                task['date_guess'] = 1
                task['date'] = self._modify_date(origin_task['date'],1)
                task['receipt'] = self._modify_receipt_num( query_result['lastSuccessReceipt'], task['direction'] )
                self.task_queue.put(task)

                task = task_report['task'].copy()
                task['fail_cnt'] += 1
                task['date_guess'] = -1
                task['date'] = self._modify_date(origin_task['date'],-1)
                task['receipt'] = self._modify_receipt_num( query_result['lastSuccessReceipt'], task['direction'] )
                self.task_queue.put(task)
            elif task_report['task']['fail_cnt'] > 5:
                log.debug( 'a task was terminated due to fail_cnt limit exceed' )
                return
            else:
                origin_task = task_report['task'].copy()
                task = task_report['task'].copy()
                task['fail_cnt'] += 1
                task['date'] = self._modify_date(origin_task['date'],1*origin_task['date_guess'])
                self.task_queue.put(task)



    def _modify_receipt_num(self, receipt, delta):
        receipt_eng = receipt[0:2]
        receipt_num = int(receipt[2:10])
        receipt_num += int(delta)
        return receipt_eng+str(receipt_num)

    def _modify_date(self, date, delta):
        year, month, day = date.split('/')
        iso_date = datetime.date(int(year)+1911, int(month), int(day))
        iso_date += datetime.timedelta(int(delta))
        date_return = u"{0}/{1:02d}/{2:02d}".format(iso_date.year-1911,iso_date.month,iso_date.day)
        return date_return


    def task_manager(self, clientsock):
        db = DBManager()

        while True:
        #while not self.task_queue.empty():
            task = self.task_queue.get()
            self.send_and_receive(task, clientsock)

        clientsock.sendall(json.dumps({"action":"close"}))
        print("task is empty")

    def check_task_db(self):
        task_db = TaskDBManager()
        db = DBManager()
        while True:
            data = task_db.GetData()
            task_db.Clear()
            for i in data:
                self.task_queue.put({
                    'receipt': i[0].encode('ascii','ignore'),
                    'date': i[1].encode('ascii','ignore'),
                    'date_guess': i[2],
                    'direction': i[3],
                    'distance': i[4],
                    'fail_cnt': i[5],
                    })
            time.sleep(60)

    def run(self):
        print 'Server Start'
        thread.start_new_thread(self.check_task_db,() )
        try:

            serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
            serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            serversock.bind(server_addr)
            serversock.listen(5)
            while 1:
                print 'waiting for connection...'
                clientsock, addr = serversock.accept()
                print '...connected from:', addr

                thread.start_new_thread(self.task_manager, (clientsock,) )
        except KeyboardInterrupt:
            serversock.close()
            L = []
            while not self.current.empty():
                L.append(self.current.get())
            while not self.task_queue.empty():
                L.append(self.task_queue.get())
            print L

            self.taskdbmanager.store_task_list(L)
            print "=====Task Saved====="

if __name__ == '__main__':
    # log.basicConfig(level = log.DEBUG)
    T = TaskServer()
    T.run()

