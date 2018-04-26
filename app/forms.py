from django import forms
from .models import Task,Group
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

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', )
