from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db import models
from django.conf import settings
import datetime
import pytz
import time

from .models import Task,Group,Log
from .forms import UserForm,TaskForm,GroupForm,LogForm
# TODO 一旦デコレータなしで組んでみる
#from .decorators import unfinishedLogChecker

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
    
#    @unfinishedLogChecker
    def get_queryset(self):
        print("----------[TaskListView#get_queryset]start-----------")
        result = Task.objects.filter(user=self.request.user.id).order_by('finished', 'group',)

        # 「完了含む」を押したとき以外
        if self.request.GET.get('contain_fin') != "1":
            result = result.filter(finished = False)

        return result

# task登録画面
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm

    # @unfinishedLogChecker
    def get_form_kwargs(self):
        print("----------[TaskCreateView#get_form_kwargs]start-----------")
        kwargs = super(TaskCreateView, self).get_form_kwargs()
        kwargs['group_queryset'] = Group.objects.filter(user = self.request.user)
        return kwargs

    # @unfinishedLogChecker
    def form_valid(self, form):
        print("----------[TaskCreateView#form_valid]start-----------")
        task = form.save(commit=False)
        task.user = self.request.user
        task.save()
        # message
        msg = task.name + 'を登録しました。'
        messages.success(self.request, msg)
        return redirect('task_list')

# task更新画面
class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class=TaskForm
    success_url = reverse_lazy('task_list')

    # @unfinishedLogChecker
    def get_form_kwargs(self):
        print("----------[TaskUpdateView#get_form_kwargs]start-----------")
        kwargs = super(TaskUpdateView, self).get_form_kwargs()
        kwargs['group_queryset'] = Group.objects.filter(user = self.request.user)
        return kwargs

    # @unfinishedLogChecker
    def form_valid(self, form):
        print("----------[TaskUpdateView#form_valid]start-----------")
        task = form.save(commit=False)
        task.user = self.request.user
        task.save()
        # message
        msg = task.name + 'を更新しました。'
        messages.success(self.request, msg)
        return redirect('task_list')

# task削除画面
class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('task_list')

# task完了
@login_required
def task_finish(request, pk, flg):
    print("----------[#task_finish]start-----------")
    task = get_object_or_404(Task, pk=pk)
    if flg == 1:
        task.finished = True
        msg = task.name + 'を完了にしました。'
    else:
        task.finished = False
        msg = task.name + 'を未完了にしました。'    
    task.save()
    # message
    
    messages.success(request, msg)

# popup group登録画面
class PopupGroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm

    # @unfinishedLogChecker
    def form_valid(self, form):
        print("----------[PopupGroupCreateView#form_valid]start-----------")
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
# @unfinishedLogChecker
def log_update(request, pk):
    print("----------[#log_update]start-----------")
    print("request.method:" + request.method)
    # submit時
    if request.method == 'POST':
        log = Log.objects.filter(pk=request.POST['id']).first()
        log.started = datetime.datetime.strptime(request.POST['started'], '%Y-%m-%d %H:%M:%S')
        log.ended = datetime.datetime.strptime(request.POST['ended'], '%Y-%m-%d %H:%M:%S')
        log.logdate = log.started
        log.logdelta = (log.ended-log.started).seconds
        log.save()
        # message
        msg = log.task.name + 'のログを更新しました。'
        messages.success(request, msg)
        return redirect('log_list')
    # 画面表示時
    else:
        log = get_object_or_404(Log, pk=pk)
        form =LogForm(initial = { #初期値セット
            'id': log.id,
            'task': log.task.name,
            'started': log.started,
            'ended': log.ended,
        })
        return render(request, 'app/log_form.html', {'form': form})

def log_delete(request):
    print("----------[#log_delete]start-----------")
    log = get_object_or_404(Log, pk=request.POST['delLogId'])
    log.delete()
    msg = 'ログを削除しました。'
    messages.success(request, msg)
    return redirect('log_list')


# popup stopwatch画面
@login_required
def task_stopwatch(request, mode, pk):
    print("----------[#task_stopwatch]start-----------")
    unfinished_log = None #初期化しておく
    type = None
    if request.method == "POST":
        log = Log.objects.filter(pk=request.POST['task_pk']).first()
        now = datetime.datetime.now()
        print("log.logdate: " + str(log.logdate))
        print("datetime.datetime.now().date(): " + str(now.date()))
        # 終了が日をまたいでいた場合、2日分にログを分ける
        if log.logdate != now.date():
            if (now.date() - log.logdate).days >= 2:
                # TODO
                unfinished_log = log
                type = 1
                print("error")
            else:
                # 開始日の分
                tz = timezone.get_default_timezone()
                log.ended = tz.localize(datetime.datetime(
                    log.logdate.year,
                    log.logdate.month,
                    log.logdate.day,
                    23,59,59,0
                ))
                log.logdelta = (log.ended-log.started).seconds
                log.save()
                # 終了日分
                today_log = Log.objects.create(task=log.task)
                today_log.started = tz.localize(datetime.datetime(
                    timezone.now().year,
                    timezone.now().month,
                    timezone.now().day,
                    0,0,0,0
                ))
                today_log.ended = timezone.now()
                today_log.logdelta = (today_log.ended-today_log.started).seconds
                today_log.save()
        else:
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
        if mode == 'c':
            # log作成
            log = Log.objects.create(task=task)
            started =timezone.now()
        elif mode == 'u':
            # log取得
            # ログを再取得していてすごく無駄な処理なので要改修
            log = Log.objects.filter(task=task, ended__isnull=True).order_by('task', '-started').first()
            started = log.started
            now = timezone.now()
            delta = (now-started).total_seconds()

        return render(request, 'app/task_stopwatch.html', {'task': task, 'log': log, 'started': started})

# log一覧画面
@login_required
# @unfinishedLogChecker
def log_list(request):
    # 時間軸で表示するため、時間軸全体に対するパーセンテージを取得
    # ログ毎に取る値：開始時間、終了時間、開始時間の%、時間幅の%
    # 同じグループ、同じタスクのログはまとめる
    # ブラウザ問わずCSSは小数点2桁まで認識するようなので、3桁目で四捨五入する
    # 8秒以下のログは0.01%以下のため表示されない
    # {'sum': '03:03:03',
    #  'group_arr':[
    #   {'group':11,
    #    'name':'testgroup',
    #    'sum':'02:02:02',
    #    'task_arr':
    #    [{'task':22,
    #      'name':'testtask',
    #      'sum': '01:01:01',
    #      'log_arr': [{'log':33, started_str':'09:01:15', 'ended_str':'09:31:15', 'delta_str':'00:30:00', 'started_percent': '37.59', 'delta_percent': '2.08'},
    #                  {...}]
    #     },{...}]
    #   },{...}]
    # }
    print("----------[#log_list]start-----------")
    unfinished_log, type = __unfinishedLogCheck(request)
        
    # 日付で絞る
    d = timezone.now() # デフォルトは今日
    log_date_str = request.GET.get('log_date')
    if (log_date_str != None):
        dt = datetime.datetime.strptime(log_date_str, '%Y-%m-%d')
        d = datetime.date(dt.year, dt.month, dt.day)

    log = Log.objects.filter(task__user=request.user.id, logdate=d, ended__isnull=False)
    # 時間軸の幅は最初の開始時刻～最後の終了時刻までにする
    fi_started = 24*60*60-1 # 最初の開始時刻(秒) 初期値は23時59分59秒
    la_ended = 0 # 最後の終了時刻(秒)

    ret_dic = {}
    group_arr = [] # 返却用配列：グループごとのdicを詰める
    ret_dic['group_arr'] = group_arr

    hour_dic = {}

    # 返却内容を詰める処理はlogが取れた場合のみ実施
    if len(log) != 0:
        
        # TODO 期間ごとの表示の作りにする(その方がシンプル)
        log_detail = log.order_by('task__group', 'task', '-started')
        # 総合計:使わないがsumを取るためにtask__userで絞る
        sum_total = log.values('task__user').annotate(sum=models.Sum('logdelta'))
        sum_grp = log.values('task__group').annotate(sum=models.Sum('logdelta'))
        sum_task = log.values('task').annotate(sum=models.Sum('logdelta'))

        # 時間軸の設定    
        # 設定ファイルからタイムゾーンを取る
        settings_tz = settings.TIME_ZONE

        for l in log_detail:
            default_timezone = pytz.timezone(settings_tz)
            l.started = default_timezone.normalize(l.started.astimezone(default_timezone))
            l.ended = default_timezone.normalize(l.ended.astimezone(default_timezone))

            st_sec = (l.started.hour*60+l.started.minute)*60+l.started.second
            ed_sec = (l.ended.hour*60+l.ended.minute)*60+l.ended.second
            if fi_started > st_sec:
                fi_started = st_sec
            if la_ended < ed_sec:
                la_ended = ed_sec

        sec_delta = la_ended - fi_started # 時間軸の幅の基準になる秒数
        print("fi_started:" + str(fi_started) + " la_ended:" + str(la_ended) + " sec_delta:" + str(sec_delta))

        # ヘッダに表示する時間軸。時と時間軸中のパーセンテージ
        # 例: {'10': '1.25', '11': '55.25'}
        # 時間軸が6時間未満 ：1時間刻み
        #        12時間未満：2時間刻み
        #        18時間未満：3時間刻み
        #        それ以上：4時間刻み
        hour_span = (sec_delta // (6*60*60)) + 1

        for x in range(0,24,hour_span):
            if fi_started <= x*3600 & x*3600 <= la_ended:
                hour_dic[x] = round(float(x*3600-fi_started)/sec_delta, 4)*100

        ret_dic['sum'] = __sec_to_hhmmss_str(sum_total[0]['sum'])
        # グループ単位でループを回す
        for g in sum_grp:
            grp = Group.objects.get(pk=g['task__group'])
            group_dic = {}
            group_arr.append(group_dic)
            group_dic['group'] = grp.id
            group_dic['name'] = grp.name
            group_dic['sum'] = __sec_to_hhmmss_str(g['sum'])
            task_arr = []
            group_dic['task_arr'] = task_arr
            # タスク単位でループを回す
            for t in sum_task:
                tsk = Task.objects.get(pk=t['task'])
                if grp.id == tsk.group.id:
                    task_dic = {}
                    task_arr.append(task_dic)
                    task_dic['task'] = tsk.id
                    task_dic['name'] = tsk.name
                    task_dic['sum'] = __sec_to_hhmmss_str(t['sum'])
                    log_arr = []
                    task_dic['log_arr'] = log_arr
                    for log in log_detail:
                        if t['task'] == log.task.id:
                            log_dic = {}
                            log_arr.append(__create_log_dic(log_dic, log, fi_started, la_ended, sec_delta))

        # group_dic = {} # グループごとのdic
        # task_arr = [] # タスクごとのdicを詰める
        # task_dic = {} # タスクごとのdic(その日のログを詰める)
        # group_sum = 0 # グループごとの秒数の合計(文字列ではなく秒数。dicに詰める際に文字列変換)
        # task_sum = 0 # タスクごとの秒数の合計(文字列ではなく秒数。dicに詰める際に文字列変換)
        # log_arr = [] # その日のタスクのログ
        # group_id = None
        # task_id = None

        # for l in log:
        #     # グループが前のログと異なる(=タスクが前のログと異なる)
        #     if group_id != l.task.group.id:
        #         # 2件目以降のグループの場合
        #         if len(group_arr) > 0:
        #             # 前のグループ分のサマリを文字列に変換して詰める
        #             prev_group_dic = group_arr[-1]
        #             prev_group_dic['sum'] = __sec_to_hhmmss_str(group_sum)
        #             # 前のタスク分のサマリを文字列に変換して詰める
        #             tmp_task_arr = prev_group_dic['task_arr']
        #             prev_task_dic = tmp_task_arr[-1]
        #             prev_task_dic['sum'] = __sec_to_hhmmss_str(task_sum)

        #         group_id = l.task.group.id
        #         # group_dicを新たに作る
        #         group_sum = l.logdelta # logdeltaも計算しなおし
        #         group_dic = {}
        #         group_dic['no'] = len(group_arr)
        #         group_dic['group'] = l.task.group.id
        #         group_dic['name'] = l.task.group

        #         # task_arrを新たに作る
        #         task_arr = []
        #         group_dic['task_arr'] = task_arr
        #         task_sum = l.logdelta # logdeltaも計算しなおし
        #         task_id = l.task.id
        #         task_dic = {}
        #         task_dic['no'] = len(task_arr)
        #         task_dic['task'] = l.task.id
        #         task_dic['name'] = l.task

        #         # log_arrを新たに作る
        #         log_arr = []
        #         log_dic = {}
        #         log_arr.append(__create_log_dic(log_dic, l, fi_started, la_ended, sec_delta))
        #         task_dic['log_arr'] = log_arr
        #         # 作ったtask_dicを詰める
        #         task_arr.append(task_dic)
        #         # 作ったgroup_dicを詰める
        #         group_arr.append(group_dic)

        #     # 前回とグループが同じ場合
        #     else:
        #         group_sum += l.logdelta
        #         task_arr = group_arr[-1]['task_arr']
        #         if task_id != l.task.id:
        #             # 前回と異なるタスクの場合
        #             # 前のタスク分のサマリを文字列に変換して詰める
        #             if len(task_arr) > 0:
        #                 prev_task_dic = task_arr[-1]
        #                 prev_task_dic['sum'] = __sec_to_hhmmss_str(task_sum)
        #             task_id = l.task
        #             # task_dicを新たに作る
        #             task_sum = l.logdelta # logdeltaも計算しなおし
        #             task_dic = {}
        #             task_dic['no'] = len(task_arr)
        #             task_dic['task'] = l.task.id
        #             task_dic['name'] = l.task

        #             # log_arrを新たに作る
        #             log_arr = []
        #             log_dic = {}
        #             log_arr.append(__create_log_dic(log_dic, l, fi_started, la_ended, sec_delta))
        #             task_dic['log_arr'] = log_arr
        #             # 作ったtask_dicを詰める
        #             task_arr.append(task_dic)
        #         else:
        #             # idが前回と同じ場合、task_arrの最後の要素を取り出し、
        #             # log_arrのappendのみ実施して詰めなおす
        #             task_sum += l.logdelta
        #             task_dic = task_arr[-1]
        #             log_arr = task_dic['log_arr']
        #             log_dic = {}
        #             log_arr.append(__create_log_dic(log_dic, l, fi_started, la_ended, sec_delta))
        #             task_dic['log_arr'] = log_arr
        #             # TODO この詰めなおしって要るんだっけ？
        #             task_arr[-1] = task_dic
        # # 最後のタスクの合計がセットされない
        # if len(group_arr) > 0:
        #     prev_group_dic = group_arr[-1]
        #     prev_group_dic['sum'] = __sec_to_hhmmss_str(group_sum)
        #     prev_task_dic = prev_group_dic['task_arr'][-1]
        #     prev_task_dic['sum'] = __sec_to_hhmmss_str(task_sum)

    print(str(ret_dic))
    print(str(hour_dic))
    return render(request, 'app/log_list.html', {'ret_dic': ret_dic, 'hour_dic': hour_dic, 'unfinished_log': unfinished_log, 'type': type,})

# log一覧画面(期間指定)
@login_required
# @unfinishedLogChecker
def log_list_period(request):
    # 同じグループ、タスクのログはまとめる
    # {'sum':'1000',
    #  'sum_str':'01:40:00',
    #  'sum_arr': [{'logdate':'2018/05/24', 'sum':'500', 'sum_str':'00:50:00'},
    #              {'logdate':...}
    #         ],
    #  'group_arr': [
    #  {'group':11,
    #   'name':'testgroup',
    #   'sum_arr': [{'logdate':'2018/05/24', 'sum':'200', 'sum_str': '00:03:20'},
    #               {'logdate':'2018/05/25', 'sum':'250', 'sum_str': '00:04:10'},
    #         ],
    #   'task_arr':[
    #    {'task':22,
    #     'name':'testtask',
    #     'log_arr': [{'logdate':'2018/05/24', 'sum':'100', 'sum_str':'00:01:40'},
    #                 {'logdate':'2018/05/25', 'sum':'120', 'sum_str':'00:02:00'},
    #         ]
    #    },{...}]
    # }]
    # }
    print("----------[#log_list_period]start-----------")
    unfinished_log, type = __unfinishedLogCheck(request)

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

    ret_dic = {} # 返却用dic
    group_arr = [] # ログ一覧に表示するグループごとのdicを詰める箱
    ret_dic['group_arr'] = group_arr
    sum_arr = []
    ret_dic['sum_arr'] = sum_arr

    # 日付でフィルタ
    log = Log.objects.filter(task__user=request.user.id, logdate__gte=df, logdate__lte=dt, ended__isnull=False)#.order_by('task__group')
    
    # Logが0件の場合は取得結果を詰める処理を省略
    if len(log) != 0:

        # サマリはSQLで実施
        # 総合計:使わないがsumを取るためにtask__userで絞る
        sum_total = log.values('task__user').annotate(sum=models.Sum('logdelta'))
        # 日付毎
        sum_total_date = log.values('logdate').annotate(sum=models.Sum('logdelta'))
        # 期間中のグループごとの集計
        sum_grp = log.values('task__group').annotate(sum=models.Sum('logdelta'))
        # 期間中のグループ・日付毎の集計
        sum_grp_date = log.values('task__group','logdate').annotate(sum=models.Sum('logdelta'))
        # タスク・期間中の集計
        sum_task = log.values('task').annotate(sum=models.Sum('logdelta'))
        # タスク・日付毎に集計
        sum_task_date = log.values('task','logdate').annotate(sum=models.Sum('logdelta'))
        
        # 総合計
        sum_total_dic = {}
        sum_arr.append(sum_total_dic)
        sum_total_dic['logdate'] = 'SUM'
        sum_total_dic['sum'] = sum_total[0]['sum']
        sum_total_dic['sum_str'] = __sec_to_hhmmss_str(sum_total[0]['sum'])

        # 総合計の日付レコード
        for s_d in sum_total_date:
            sum_dic = {}
            sum_arr.append(sum_dic)
            sum_dic['logdate'] = s_d['logdate'].strftime('%Y/%m/%d')
            sum_dic['sum'] = s_d['sum']
            sum_dic['sum_str'] =  __sec_to_hhmmss_str(s_d['sum'])
        print(str(sum_arr))
        # グループ単位でループを回す
        for g in sum_grp:
            grp = Group.objects.get(pk=g['task__group'])
            group_dic = {}
            group_arr.append(group_dic)
            group_dic['group'] = grp.id
            group_dic['name'] = grp.name
            sum_arr = []
            group_dic['sum_arr'] = sum_arr
            # グループのサマリ行
            grp_sum_dic = {}
            sum_arr.append(grp_sum_dic)
            grp_sum_dic['logdate'] = 'SUM'
            grp_sum_dic['sum'] = g['sum']
            grp_sum_dic['sum_str'] = __sec_to_hhmmss_str(g['sum'])
            # グループのサマリ行の日付レコード(日数分の件数)
            for l_g in sum_grp_date:
                if l_g['task__group'] == grp.id:
                    grp_log_dic = {}
                    sum_arr.append(grp_log_dic)
                    grp_log_dic['logdate'] = l_g['logdate'].strftime('%Y/%m/%d')
                    grp_log_dic['sum'] = l_g['sum']
                    grp_log_dic['sum_str'] = __sec_to_hhmmss_str(l_g['sum'])
            task_arr = []
            group_dic['task_arr'] = task_arr
            for t in sum_task:
                task = Task.objects.get(pk=t['task'])
                # グループに属するタスクに対して処理
                if task.group.id == grp.id:

                    task_dic = {}
                    task_arr.append(task_dic)
                    task_dic['task'] = task.id
                    task_dic['name'] = task.name
                    log_arr = []
                    task_dic['log_arr'] = log_arr
                    # タスクのサマリ行
                    task_sum_dic = {}
                    log_arr.append(task_sum_dic)
                    task_sum_dic['logdate'] = 'SUM'
                    task_sum_dic['sum'] = t['sum']
                    task_sum_dic['sum_str'] = __sec_to_hhmmss_str(t['sum'])
                    # タスクの日付毎レコード(日数分の件数)
                    for l_t in sum_task_date:
                        if l_t['task'] == task.id:
                            task_log_dic = {}
                            log_arr.append(task_log_dic)
                            task_log_dic['logdate'] = l_t['logdate'].strftime('%Y/%m/%d')
                            task_log_dic['sum'] = l_t['sum']
                            task_log_dic['sum_str'] = __sec_to_hhmmss_str(l_t['sum'])    


    # 日付表示対象の日付
    log_date = df
    date_arr = ['SUM']
    date_arr.append(log_date.strftime('%Y/%m/%d'))
    while log_date != dt:
        log_date = log_date + datetime.timedelta(days=1)
        date_arr.append(log_date.strftime('%Y/%m/%d'))
    
    return render(request, 'app/log_list_period.html', {'ret_dic': ret_dic, 'date_arr': date_arr, 'unfinished_log': unfinished_log, 'type': type,})

# ログ1件分の情報を作成する
def __create_log_dic(log_dic, l, fi_started, la_ended, sec_delta):
    log_dic['log'] = l.id
    log_dic['started_str'] = l.started.strftime('%H:%M:%S')
    log_dic['ended_str'] = l.ended.strftime('%H:%M:%S')
    log_dic['delta_str'] = __sec_to_hhmmss_str(l.logdelta)
    # 開始時刻の全体に対するパーセンテージを取得
    st_sec = (l.started.hour*60+l.started.minute)*60+l.started.second - fi_started
    log_dic['started_percent'] = round(float(st_sec)/sec_delta,4)*100
    
    log_dic['delta_percent'] = round(float(l.logdelta)/sec_delta,4)*100

    return log_dic

# 秒数から時分秒の文字列を作成する
def __sec_to_hhmmss_str(total_sec):
    l = __sec_to_hhmmss_list(total_sec)
    ret_str = str(l[0]).zfill(2) + ":" + str(l[1]).zfill(2) + ":" + str(l[2]).zfill(2)
    return ret_str

# 秒数から時分秒をlistで返す
def __sec_to_hhmmss_list(total_sec):
    sec = total_sec % 60
    min = (total_sec // 60) % 60
    hour = total_sec // 3600
    return [hour,min,sec]

# 未完了のままになっているログがないかチェック
def __unfinishedLogCheck(request):
    log = Log.objects.filter(task__user=request.user.id, ended__isnull=True).order_by('task', '-started')
    if len(log) == 0:
        return None,0
    else:
        log = log.first()
        # 開始から2日以上経過している場合：手で編集させる
        # 開始が前日：再開or編集
        if (timezone.now().date()-log.logdate).days >= 2:
            return log,1
        else:
            return log,2
