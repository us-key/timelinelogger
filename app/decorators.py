from .models import Log 

# 完了していないログがあった場合、ストップウォッチ画面を開く
def unfinishedLogChecker(function):

    def inner(request, *args, **kwargs):

        log = Log.objects.filter(task__user=request.request.user.id, ended__isnull=True).order_by('task', '-started')
        print(log)
        if len(log) == 0:
            return function(request, *args, **kwargs)
        else:
            print(log.first())
            return function(request, *args, **kwargs)
    
    return inner
    
