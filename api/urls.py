from django.urls import path
from api import views

app_name = 'api'
urlpatterns = [
    # tasks
    path('v1/tasks/', views.task_list, name='api_task_list'), # 一覧
    path('v1/task/del/', views.del_task, name='api_del_task'), # 削除
    path('v1/task/fin/', views.fin_task, name='api_fin_task'), # 完了
    ]