from django.shortcuts import render

from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView

# Create your views here.
class CommentNoticeUpdateView(View):
    """更新通知状态"""
    # 处理 get 请求
    def get(self, request):
        # 获取未读消息
        notice_id = request.GET.get('notice_id')
        # 更新单条通知
        if notice_id:
            request.user.notifications.get(id=notice_id).mark_as_read()
            return redirect('user:edit',id=request.user.id)
        # 更新全部通知
        else:
            request.user.notifications.mark_all_as_read()
            return redirect('user:edit',id=request.user.id)