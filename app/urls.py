from django.urls import path
from django.contrib.auth import views as auth_views
from .views import UserCreateView,UserDeleteView,TaskListView,TaskCreateView,TaskUpdateView,TaskDeleteView,PopupGroupCreateView
from . import views

urlpatterns = [
    # index
    path('', views.log_list, name='index'),
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
    # task完了
    path('task/finish/<int:pk>/<int:flg>', views.task_finish, name='task_finish'),

    # (popup)group作成
    path('popup/group/create/', PopupGroupCreateView.as_view(), name='popup_group_create'),

    # log作成(stopwatch)
    path('task_stopwatch/<str:mode>/<int:pk>/', views.task_stopwatch, name='task_stopwatch'),
    # log更新画面
    path('log/update/<int:pk>', views.log_update, name='log_update'),
    # log削除
    path('log/delete', views.log_delete, name='log_delete'),
    # log一覧画面(日付指定)
    path('log/', views.log_list, name='log_list'),
    # log一覧表示(期間指定)
    path('log/period/', views.log_list_period, name='log_list_period'),

    ]