from django.urls import path
from .views import TaskListView,TaskCreateView,TaskUpdateView,TaskDeleteView,PopupGroupCreateView

urlpatterns = [
    # task一覧画面
    path('task/', TaskListView.as_view(), name='index'),
    # task登録画面
    path('task/create/', TaskCreateView.as_view(), name='task_create'),
    # task更新画面
    path('task/update/<int:pk>', TaskUpdateView.as_view(), name='task_update'),
    # task削除画面
    path('task/delete/<int:pk>', TaskDeleteView.as_view(), name='task_delete'),

    # (popup)group作成
    path('popup/group/create/', PopupGroupCreateView.as_view(), name='popup_group_create'),

    ]