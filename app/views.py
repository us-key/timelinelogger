from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.conf import settings
import datetime
import pytz
import time

from .models import Task,Group,Log
from .forms import UserForm,TaskForm,GroupForm,LogForm

# Create your views here.

# user登録画面
class UserCreateView(CreateView):
    template_name='app/user_form.html'
    model = User
    form_class = UserForm
    success_url = reverse_lazy('login')

# user削除画面
class UserDeleteView(LoginRequiredMixin, DeleteView):
    template_name='app/user_confirm_delete.html'
    model = User
    success_url = reverse_lazy('login')

# task一覧画面
class TaskListView(LoginRequiredMixin, ListView):
    model = Task

    def get_queryset(self):
        result = Task.objects.filter(user=self.request.user.id).order_by('finished', 'group',)

        # 「完了含む」を押したとき以外
        if self.request.GET.get('contain_fin') != "1/":
            result = result.filter(finished = False)

        return result

# task登録画面
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm

    def get_form_kwargs(self):
        kwargs = super(TaskCreateView, self).get_form_kwargs()
        kwargs['group_queryset'] = Group.objects.filter(user = self.request.user)
        return kwargs

    def form_valid(self, form):
        task = form.save(commit=False)
        task.user = self.request.user
        task.save()
        return redirect('task_list')

# task更新画面
class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class=TaskForm
    success_url = reverse_lazy('task_list')

    def get_form_kwargs(self):
        kwargs = super(TaskUpdateView, self).get_form_kwargs()
        kwargs['group_queryset'] = Group.objects.filter(user = self.request.user)
        return kwargs

    def form_valid(self, form):
        task = form.save(commit=False)
        task.user = self.request.user
        task.save()
        return redirect('task_list')

# task削除画面
class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('task_list')

# task完了
@login_required
def task_finish(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.finished = True
    task.save()
    return redirect('task_list')

# popup group登録画面
class PopupGroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm

    def form_valid(self, form):
        group = form.save(commit=False)
        group.user = self.request.user
        group.save()
        context = {
            'object_name': str(group),
            'object_pk': group.pk,
            'function_name':'add_group',
            }
        return render(self.request, 'app/close.html', context)

# ログ編集画面
def log_update(request, pk):
    # submit時
    if request.method == 'POST':
        log = Log.objects.filter(pk=request.POST['id']).first()
        log.started = request.POST['started']
        log.ended = request.POST['ended']
        log.logdelta = (log.ended-log.started).seconds
        log.save()
        return redirect('log_list')
    # 画面表示時
    else:
        log = get_object_or_404(Log, pk=pk)
        print(log)
        form =LogForm()
        form.id = log.id
        form.task = log.task.name
        form.started = log.started
        form.ended = log.ended
        print(form)
        return render(request, 'app/log_form.html', {'form': form})

# popup stopwatch画面
@login_required
def task_stopwatch(request, pk):
    if request.method == "POST":
        log = Log.objects.filter(pk=request.POST['task_pk']).first()
        log.ended = timezone.now()
        log.logdelta = (log.ended-log.started).seconds
        log.save()
        context = {
            'object_name': "",
            'object_pk': "",
            'function_name': 'add_log',
            }
        return render(request, 'app/close.html', context)
    else:
        #urlで指定されたkeyからタスクを取得、なければ404
        task = get_object_or_404(Task, pk=pk)
        # log作成
        log = Log.objects.create(task=task)

        return render(request, 'app/task_stopwatch.html', {'task': task, 'log': log})

# log一覧画面
@login_required
def log_list(request):
    # 日付で絞る
    d = timezone.now() # デフォルトは今日
    log_date_str = request.GET.get('log_date')
    if (log_date_str != None):
        dt = datetime.datetime.strptime(log_date_str, '%Y-%m-%d')
        d = datetime.date(dt.year, dt.month, dt.day)

    log = Log.objects.filter(task__user=request.user.id, logdate=d, ended__isnull=False).order_by('task', '-started')
    print(log)
    
    # 時間軸で表示するため、時間軸全体に対するパーセンテージを取得
    # ログ毎に取る値：開始時間、終了時間、開始時間の%、時間幅の%
    # 同じタスクのログはまとめる
    # ブラウザ問わずCSSは小数点2桁まで認識するようなので、3桁目で四捨五入する
    # 8秒以下のログは0.01%以下のため表示されない
    # [{'task':22,
    #  'name':'testtask',
    #  'group:'testgroup',
    #  'sum': '01:01:01'
    #  'log_arr': [{'log':33, started_str':'09:01:15', 'ended_str':'09:31:15', 'delta_str':'00:30:00', 'started_percent': '37.59', 'delta_percent': '2.08'},
    #              {...}
    #        ]
    # },{...}]

    # 時間軸の幅は最初の開始時刻～最後の終了時刻までにする
    fi_started = 24*60*60-1 # 最初の開始時刻(秒) 初期値は23時59分59秒
    la_ended = 0 # 最後の終了時刻(秒)

    # 設定ファイルからタイムゾーンを取る
    settings_tz = settings.TIME_ZONE

    for l in log:
        default_timezone = pytz.timezone(settings_tz)
        l.started = default_timezone.normalize(l.started.astimezone(default_timezone))
        print(l.started)
        l.ended = default_timezone.normalize(l.ended.astimezone(default_timezone))
        print(l.ended)

        st_sec = (l.started.hour*60+l.started.minute)*60+l.started.second
        ed_sec = (l.ended.hour*60+l.ended.minute)*60+l.ended.second
        if fi_started > st_sec:
            fi_started = st_sec
        if la_ended < ed_sec:
            la_ended = ed_sec

    sec_delta = la_ended - fi_started # 時間軸の幅の基準になる秒数
    print("fi_started:" + str(fi_started) + " la_ended:" + str(la_ended) + " sec_delta:" + str(sec_delta))
    
    task_arr = [] # タスクごとの配列を詰める
    task_dic = {} # タスクごとの配列(その日のログを詰める)
    task_sum = 0 # タスクごとの秒数の合計(文字列ではなく秒数。dicに詰める際に文字列変換)
    log_arr = [] # その日のタスクのログ
    task_id = None
    for l in log:
        if task_id != l.task:
            # 前のタスク分のサマリを文字列に変換して詰める
            if len(task_arr) > 0:
                prev_task_dic = task_arr[-1]
                prev_task_dic['sum'] = __sec_to_hhmmss_str(task_sum)
                print(prev_task_dic['sum'])
                # TODO この詰めなおしが必要かどうか要確認
                #task_arr[-1] = prev_task_dic
            task_id = l.task
            task = Task.objects.get(pk=l.task.id)
            # idが前回と異なる場合task_dicを新たに作る
            task_sum = l.logdelta # logdeltaも計算しなおし
            task_dic = {}
            task_dic['no'] = len(task_arr)
            task_dic['task'] = l.task.id
            task_dic['name'] = task
            task_dic['group'] = task.group
            # log_arrを新たに作る
            log_arr = []
            log_dic = {}
            log_arr.append(__create_log_dic(log_dic, l, fi_started, la_ended, sec_delta))
            task_dic['log_arr'] = log_arr
            # 作ったtask_dicを詰める
            task_arr.append(task_dic)
        else:
            # idが前回と同じ場合、task_arrの最後の要素を取り出し、
            # log_arrのappendのみ実施して詰めなおす
            task_sum += l.logdelta
            task_dic = task_arr[-1]
            log_arr = task_dic['log_arr']
            log_dic = {}
            log_arr.append(__create_log_dic(log_dic, l, fi_started, la_ended, sec_delta))
            task_dic['log_arr'] = log_arr

            task_arr[-1] = task_dic
    # 最後のタスクの合計がセットされない
    if len(task_arr) > 0:
        prev_task_dic = task_arr[-1]
        prev_task_dic['sum'] = __sec_to_hhmmss_str(task_sum)
        # TODO この詰めなおしが必要かどうか要確認
        #task_arr[-1] = prev_task_dic

    # ヘッダに表示する時間軸。時と時間軸中のパーセンテージ
    # 例: {'10': '1.25', '11': '55.25'}
    # 時間軸が6時間未満 ：1時間刻み
    #        12時間未満：2時間刻み
    #        18時間未満：3時間刻み
    #        それ以上：4時間刻み
    hour_dic = {}
    hour_span = (sec_delta // (6*60*60)) + 1

    for x in range(0,24,hour_span):
        if fi_started <= x*3600 & x*3600 <= la_ended:
            hour_dic[x] = round(float(x*3600-fi_started)/sec_delta, 4)*100

    return render(request, 'app/log_list.html', {'task_arr': task_arr, 'hour_dic': hour_dic})

# log一覧画面(期間指定)
@login_required
def log_list_period(request):

    # 日付で絞る
    df = timezone.localdate(timezone.now())+datetime.timedelta(days=-6)
    dt = timezone.localdate(timezone.now())
    log_from_str = request.GET.get('log_from')
    log_to_str = request.GET.get('log_to')
    if (log_from_str != None):
        dtf = datetime.datetime.strptime(log_from_str, '%Y-%m-%d')
        df = datetime.date(dtf.year, dtf.month, dtf.day)
    if (log_to_str != None):
        dtt = datetime.datetime.strptime(log_to_str, '%Y-%m-%d')
        dt = datetime.date(dtt.year, dtt.month, dtt.day)
    # 日付でフィルタ
    log = Log.objects.filter(task__user=request.user.id, logdate__gte=df, logdate__lte=dt, ended__isnull=False)
    # 日付毎に集計
    log = log.values('task','logdate').annotate(sum=models.Sum('logdelta'))
    
    task_arr = [] # ログ一覧に表示するタスクごとの配列を詰める箱
    task_dic = {} # タスクごとの配列(日毎のログを詰める)
    log_arr = [] # 日毎のログ
    task_id = None
    for l in log:
        # 合計時間のhh:mm:ss表示
        l['sum_str'] = __sec_to_hhmmss_str(l['sum'])
        # logdateは文字列変換して渡す
        l['logdate'] = l['logdate'].strftime('%Y/%m/%d')
        if task_id != l['task']:
            task_id = l['task']
            task = Task.objects.get(pk=l['task'])
            # idが前回と異なる場合、task_dicを新たに作る
            task_dic = {}
            task_dic['task'] = l['task']
            task_dic['name'] = task
            task_dic['group'] = task.group
            # log_arrを新たに作る
            log_arr = []
            log_arr.append(l)
            task_dic['log_arr'] = log_arr
            # 作ったtask_dicを詰める
            task_arr.append(task_dic)
        else:
            # idが前回と同じ場合、task_arrの最後の要素を取り出し、
            # log_arrのappendのみ実施して詰めなおす
            task_dic = task_arr[-1]
            log_arr = task_dic['log_arr']
            log_arr.append(l)
            task_dic['log_arr'] = log_arr
            task_arr[-1] = task_dic
           
    print(task_arr)

    # 同じタスクのログはまとめる
    # [{'task':22,
    #  'name':'testtask',
    #  'group:'testgroup',
    #  'log_arr': [{'logdate':'2018/05/24', 'sum':'100', 'sum_str':'00:01:40'},
    #          {'logdate':'2018/05/26', 'sum':'120', 'sum_str':'00:02:00'},
    #         ]
    # },{...}]

    # 日付表示対象の日付
    log_date = df
    date_arr = [log_date.strftime('%Y/%m/%d')]
    while log_date != dt:
        log_date = log_date + datetime.timedelta(days=1)
        date_arr.append(log_date.strftime('%Y/%m/%d'))

    print(date_arr)

    return render(request, 'app/log_list_period.html', {'task_arr': task_arr, 'date_arr': date_arr})

# ログ1件分の情報を作成する
def __create_log_dic(log_dic, l, fi_started, la_ended, sec_delta):
    log_dic['log'] = l.id
    log_dic['started_str'] = l.started.strftime('%H:%M:%S')
    log_dic['ended_str'] = l.ended.strftime('%H:%M:%S')
    log_dic['delta_str'] = __sec_to_hhmmss_str(l.logdelta)
    print(log_dic['started_str'])
    print(log_dic['ended_str'])
    print(log_dic['delta_str'])
    # 開始時刻の全体に対するパーセンテージを取得
    st_sec = (l.started.hour*60+l.started.minute)*60+l.started.second - fi_started
    log_dic['started_percent'] = round(float(st_sec)/sec_delta,4)*100
    print(log_dic['started_percent'])
    
    log_dic['delta_percent'] = round(float(l.logdelta)/sec_delta,4)*100
    print(log_dic['delta_percent'])

    return log_dic

# 秒数から時分秒の文字列を作成する
def __sec_to_hhmmss_str(total_sec):
    print(str(total_sec))
    sec = total_sec % 60
    min = (total_sec // 60) % 60
    hour = total_sec // 3600
    ret_str = str(hour).zfill(2) + ":" + str(min).zfill(2) + ":" + str(sec).zfill(2)
    print(ret_str)
    return ret_str
