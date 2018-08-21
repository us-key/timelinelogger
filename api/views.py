import json
from collections import OrderedDict
from django.http import HttpResponse
from app.models import Task, Log

# Create your views here.

# responseをjsonで返却
def render_json_response(request, data, status=None):
    json_str = json.dumps(data, ensure_ascii=True, indent=2)
    callback = request.GET.get('callback')
    if not callback:
        # POSTでJSONPの場合
        callback = request.POST.get('callback')
    if callback:
        json_str = "%s(%s)" % (callback, json_str)
        response = HttpResponse(json_str, content_type='application/javascript; charset=UTF-8', status=status)
    else:
        response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=status)
    return response

# TASKの一覧を返却
def task_list(request):
    tasks = []
    q_tasks = Task.objects.filter(user=request.user.id).order_by('finished','group',)
    if request.GET['finishedTaskFlg'] == '0':
        q_tasks = q_tasks.filter(finished=0)
    for task in q_tasks:

        task_dict = OrderedDict([
            ('id', task.id),
            ('name', task.name),
            ('group', task.group.name),
            ('finished', '1' if task.finished else '0'),
            ])
        tasks.append(task_dict)

    data = OrderedDict([('tasks', tasks)])
    return render_json_response(request, data)

# TASKを削除する
def del_task(request):
    task = Task.objects.get(pk=request.GET['taskId'])
    returncode = 0
    msg = ""
    if task:
        task.delete()
        msg = task.name + "を削除しました。"

    else:
        # エラーを返却
        returncode = 1
        msg = "削除できませんでした。再実行してください。"

    data = {'returncode':returncode, 'msg':msg}
    return render_json_response(request, data)

# TASKを完了/未完了にする
def fin_task(request):
    task = Task.objects.get(pk=request.GET['taskId'])
    returncode = 0
    msg = ""
    if task:
        msg = task.name
        if request.GET['setFinished']=='1':
            task.finished = True 
            msg += " を完了にしました。"
        else:
            task.finished = False
            msg += " を未完了に戻しました。"
        task.save()

    else:
        # エラーを返却
        returncode = 1
        msg = "変更できませんでした。再実行してください。"

    data = {'returncode':returncode, 'msg':msg}
    return render_json_response(request, data)
