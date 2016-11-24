from __future__ import unicode_literals

from django.apps import AppConfig

class TaskserverConfig(AppConfig):
    name = 'taskServer'


    def ready(self):
        try:
            Task = self.get_model("Task")
            for task in Task.objects.filter(solved=False, queued=True):
                task.queued = False
                task.save()
        except:
            return
