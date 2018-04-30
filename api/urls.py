from django.urls import path
from api import views

app_name = 'api'
urlpatterns = [
    # tasks
    path('v1/tasks/', views.task_list, name='api_task_list'), # 一覧
    ]