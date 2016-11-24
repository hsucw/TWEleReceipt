from __future__ import unicode_literals

from django.db import models

class Receipt( models.Model ):
    receipt = models.TextField()
    date = models.TextField()
    money = models.IntegerField()
    taxid = models.IntegerField()

    class Meta:
        unique_together = ["receipt", "date", "taxid"]



class Task( models.Model ):
    receipt = models.TextField()
    date = models.TextField()
    date_max = models.TextField()
    date_min = models.TextField()
    date_guess = models.IntegerField()
    direction = models.IntegerField()
    distance = models.IntegerField(default=100)
    fail_cnt = models.IntegerField(default=0)
    solved = models.BooleanField(default=False)
    queued = models.BooleanField(default=False)
    hash   = models.TextField(default="NULL")
    def as_json(self):
        return dict(
            {
                "id": self.id,
                "receipt": self.receipt,
                "date": self.date,
                "date_guess": self.date_guess,
                "direction": self.direction,
                "distance": self.distance,
                "fail_cnt": self.fail_cnt,
                "solved": self.solved,
                "queued": self.queued
            }
        )
    class Meta:
        unique_together = ["receipt", "date", "date_guess", "direction", "distance" ]

class TaskStatistics( models.Model ):
    task = models.ForeignKey( Task )
    time = models.FloatField()
    rps = models.FloatField( default=0.0 )
    success = models.IntegerField()
    error = models.IntegerField()
    distance = models.IntegerField()

class ClientRequests( models.Model ):
    token = models.TextField()
    date = models.TextField()
    valid = models.BooleanField()
    taxId = models.TextField()


