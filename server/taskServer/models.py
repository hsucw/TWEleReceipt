from __future__ import unicode_literals

from django.db import models

class Receipt( models.Model ):
    receipt = models.TextField(unique=True,max_length=10)
    date = models.TextField()
    money = models.IntegerField()
    taxid = models.IntegerField()

    class Meta:
        unique_together = ["receipt", "date"]



class Task( models.Model ):
    receipt = models.TextField()
    date = models.TextField()
    direction = models.IntegerField()
    distance = models.IntegerField(default=100)
    fail_cnt = models.IntegerField(default=0)
    solved = models.BooleanField(default=False)
    queued = models.BooleanField(default=False)
    todo = models.TextField(null=True)
    succ = models.IntegerField(default=0)
    def as_json(self):
        return dict(
            {
                "id": self.id,
                "receipt": self.receipt,
                "date": self.date,
                "direction": self.direction,
                "distance": self.distance,
                "fail_cnt": self.fail_cnt,
                "solved": self.solved,
                "todo": self.todo,
                "succ": self.succ,
                "queued": self.queued
            }
        )
    class Meta:
        unique_together = ["receipt", "date"]

class TaskStatistics( models.Model ):
    task = models.ForeignKey( Task )
    time = models.FloatField()
    rps = models.FloatField( default=0.0 )
    success = models.IntegerField()
    error = models.IntegerField()
    distance = models.IntegerField()
    taxId = models.IntegerField()

class ClientRequests( models.Model ):
    token = models.TextField()
    receipt = models.TextField()
    date = models.TextField()




