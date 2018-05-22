from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

from .models import Task,Group,Log
from .forms import UserForm,TaskForm,GroupForm

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
#     success_url = reverse_lazy('index')

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

# popup stopwatch画面
def task_stopwatch(request, pk):
    if request.method == "POST":
        log = Log.objects.filter(pk=request.POST['task_pk']).first()
        log.ended = timezone.now()
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
class LogListView(LoginRequiredMixin, ListView):
    model = Log

    def get_queryset(self):
        # 日付で絞る
        d = timezone.now() # デフォルトは今日
        log_date_str = self.request.GET.get('log_date')
        if (log_date_str != None):
            dt = datetime.datetime.strptime(log_date_str, '%Y-%m-%d')
            d = datetime.date(dt.year, dt.month, dt.day)
        log = Log.objects.filter(task__user=self.request.user.id, logdate=d, ended__isnull=False).order_by('task', '-started')

        return log

# log一覧画面(期間指定)
class LogListPeriodView(LoginRequiredMixin, ListView):
    model = Log
    template_name="app/log_list_period.html"

    def get_queryset(self):
        # 日付で絞る
        # TODO 集計
        df = timezone.now()
        dt = timezone.now()
        log_from_str = self.request.GET.get('log_from')
        log_to_str = self.request.GET.get('log_to')
        if (log_from_str != None):
            dtf = datetime.datetime.strptime(log_from_str, '%Y-%m-%d')
            df = datetime.date(dtf.year, dtf.month, dtf.day)
        if (log_to_str != None):
            dtt = datetime.datetime.strptime(log_to_str, '%Y-%m-%d')
            dt = datetime.date(dtt.year, dtt.month, dtt.day)
        log = Log.objects.filter(task__user=self.request.user.id, logdate__gte=df, logdate__lte=dt, ended__isnull=False).order_by('task', '-started')

        return log

