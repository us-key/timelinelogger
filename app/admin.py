from django.contrib import admin
from .models import Task,Group,Log
# Register your models here.
admin.site.register(Task)
admin.site.register(Group)
admin.site.register(Log)