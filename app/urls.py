from django.urls import path
from django.contrib.auth import views as auth_views
from .views import TaskListView,TaskCreateView,TaskUpdateView,TaskDeleteView,PopupGroupCreateView

urlpatterns = [
    # index
    path('', TaskListView.as_view(), name='task_list'),
    # login
    path('login/', auth_views.login, {'template_name': 'app/login.html'}, name='login'),
    # logout
    path('logout/', auth_views.logout, {'template_name': 'app/logged_out.html'}, name='logout'),


    # task一覧画面
    path('task/', TaskListView.as_view(), name='task_list'),
    # task登録画面
    path('task/create/', TaskCreateView.as_view(), name='task_create'),
    # task更新画面
    path('task/update/<int:pk>', TaskUpdateView.as_view(), name='task_update'),
    # task削除画面
    path('task/delete/<int:pk>', TaskDeleteView.as_view(), name='task_delete'),

    # (popup)group作成
    path('popup/group/create/', PopupGroupCreateView.as_view(), name='popup_group_create'),




    ]