from django import forms
from .models import Task,Group
from django.contrib.auth.models import User
from django.db.models.fields import CharField

class TaskForm(forms.ModelForm):
#     group = forms.ModelChoiceField(
#                     Group.objects,
#                     label='group',
#                     to_field_name='name',
#                     ),
#     user = forms.ModelChoiceField(
#                     User.objects,
#                     label='user',
#                     to_field_name='username',
#                     required=True,
#                     empty_label=None,
#                     ),

    class Meta:
        model = Task
        fields = ('name','group','remarks',)

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', )
