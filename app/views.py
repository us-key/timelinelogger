from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.contrib.auth.models import User

from .models import Task,Group
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
        return Task.objects.filter(finished=False, user=self.request.user.id).order_by('group')


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

# task削除画面
class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('task_list')

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
