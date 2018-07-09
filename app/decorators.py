from django.shortcuts import render, redirect, get_object_or_404
from .models import Log, Task

# 完了していないログがあった場合、ストップウォッチ画面を開く
def unfinishedLogChecker(function):

    def inner(request, *args, **kwargs):

        log = Log.objects.filter(task__user=request.request.user.id, ended__isnull=True).order_by('task', '-started')
        print(log)
        if len(log) == 0:
            return function(request, *args, **kwargs)
        else:
            log = log.first()
            print(log)
            kwargs['log'] = log
            return function(request, *args, **kwargs)
    
    return inner
    
