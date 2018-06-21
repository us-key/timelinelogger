from django import forms
from .models import Task,Group,Log
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models.fields import CharField

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','email', 'password1', 'password2',)

class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ('name','group','remarks',)

    def __init__(self, *args, **kwargs):
        self.base_fields['group'].queryset = self.get_group_list(kwargs)
        super(TaskForm, self).__init__(*args, **kwargs)

    def get_group_list(self, kwargs):
        return kwargs.pop('group_queryset')

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', )

class LogForm(forms.Form):
    # class Meta:
    #     model = Log
    #     fields = ('task','logdate','started','ended',)
    #     widgets = {'task': forms.Select(attrs={'disabled':True})}
    id = forms.CharField()
    task = forms.TextInput()
    started = forms.DateTimeInput()
    ended = forms.DateTimeInput()
