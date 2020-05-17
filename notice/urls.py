from django.urls import path
from . import views

app_name = 'notice'

urlpatterns = [
    # 更新通知状态
    path('update/', views.CommentNoticeUpdateView.as_view(), name='update'),
]
