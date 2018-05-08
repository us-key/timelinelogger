from django.urls import path
from django.contrib.auth import views as auth_views
from .views import UserCreateView,UserDeleteView,TaskListView,TaskCreateView,TaskUpdateView,TaskDeleteView,PopupGroupCreateView,LogListView
from . import views

urlpatterns = [
    # index
    path('', TaskListView.as_view(), name='task_list'),
    # login
    path('login/', auth_views.login, {'template_name': 'app/login.html'}, name='login'),
    # logout
    path('logout/', auth_views.logout, {'template_name': 'app/logged_out.html'}, name='logout'),
    # user登録画面
    path('user/create/', UserCreateView.as_view(), name='user_create'),
    # user削除画面
    path('user/delete/<int:pk>', UserDeleteView.as_view(), name='user_delete'),

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

    # log作成(stopwatch)
    path('task_stopwatch/<int:pk>/', views.task_stopwatch, name='task_stopwatch'),
    # log一覧画面
    path('log/', LogListView.as_view(), name='log_list'),

    ]