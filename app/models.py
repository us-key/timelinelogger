from django.db import models
from django.core import validators
from django.utils import timezone

# Create your models here.
class Task(models.Model):
    name = models.CharField(
        max_length=200,
        )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        null=True,
        )
    remarks = models.TextField(
        max_length=300,
        blank=True,
        )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True
        )
    finished = models.BooleanField(
        null=False,
        default=False,
        )

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(
        max_length=200,
        )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,)


    def __str__(self):
        return self.name

class Log(models.Model):
    task = models.ForeignKey(
        'Task',
        on_delete=models.CASCADE,)
    logdate = models.DateField(
        default=timezone.now,
        )
    started = models.DateTimeField(
        default=timezone.now,
        )
    ended = models.DateTimeField(
        blank=True,
        null=True,
        )
    # datetime.timedeltaをsumするのが困難なため、
    # numberでDBに保持する
    logdelta = models.IntegerField(
        null=True,
        )

    def __str__(self):
        return self.task.name + " " + str(self.started)

    def logdelta_str(self):
        sec = min = hour = 0
        if self.logdelta is not None:
            sec = self.logdelta % 3600
            min = (self.logdelta // 60) % 60
            hour = self.logdelta // 3600
        return str(hour) + ":" + str(min) + ":" + str(sec)

