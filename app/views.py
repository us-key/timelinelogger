from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView,UpdateView,DeleteView

from .models import Task,Group
from .forms import TaskForm,GroupForm

# Create your views here.

# task一覧画面
class TaskListView(LoginRequiredMixin, ListView):
    model = Task

    def get_queryset(self):
        return Task.objects.filter(finished=False, user=self.request.user.id).order_by('group')


# task登録画面
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
#     success_url = reverse_lazy('index')

    def form_valid(self, form):
        task = form.save(commit=False)
        task.user = self.request.user
        task.save()
        return redirect('index')

# task更新画面
class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class=TaskForm
    success_url = reverse_lazy('index')

# task削除画面
class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('index')

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
