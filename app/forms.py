from django import forms
from .models import Task,Group,Log
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models.fields import CharField
from datetimewidget.widgets import DateTimeWidget

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
    id = forms.CharField(widget=forms.HiddenInput)
    task = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'readonly':True}
        ))
    
    dateOptions = {
        'format': 'yyyy-mm-dd HH:ii:ss',
        'autoclose': True,
        'showMeridian': True,
    }

    started = forms.DateTimeField(
        widget=DateTimeWidget(
            options=dateOptions, attrs={
                'class': 'chk_required chk_format_datetime',
                'readonly':False}
        ))
    ended = forms.DateTimeField(widget=DateTimeWidget(options=dateOptions, attrs={'readonly':False}))
