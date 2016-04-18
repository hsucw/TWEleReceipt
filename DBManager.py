#!/usr/local/bin python
import json
import ssl


def checkAlive(func):
    def check_alive(*args, **kargs):
        #check somthing
        res = func(*args, **kargs)
        return res
    return check_alive

class DBManager(object):
    def __init__(self, role='client'):
        self.role = role
        pass

    def _conn(self):
        """ server: build socket & listen """
        pass

    def conn(self):
        """ client: connect to the server """
        pass

    @checkAlive
    def regSeeds(self, seeds):
        """ client: send seeds to server """
        pass

    @checkAlive
    def _regSeeds(self, seeds):
        """ server: save seeds into DB """
        pass

    @checkAlive
    def getTasks(self):
        """ client: get unfinished tasks from server """
        pass

    @checkAlive
    def _getTasks(self):
        """ server: get unfinished tasks from DB"""
        pass

    @checkAlive
    def putReports(self, reports):
        """ client: send reports to server """
        pass

    @checkAlive
    def _putReport(self, reports):
        """ server: store the reports to DB """
        pass

    @checkAlive
    def _putTasks(self, tasks):
        """ server: store the unfinished tasks to DB """
        pass

if __name__ == "__main__":
    pass
