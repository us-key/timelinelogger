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
    for task in Task.objects.filter(user=request.user.id).order_by('group'):
        task_dict = OrderedDict([
            ('id', task.id),
            ('name', task.name),
            ('group', task.group.name),
            ])
        tasks.append(task_dict)

    data = OrderedDict([('tasks', tasks)])
    return render_json_response(request, data)
