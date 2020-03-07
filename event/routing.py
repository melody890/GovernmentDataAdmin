from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/event/post/$', consumers.PostDataConsumer),
    re_path(r'ws/event/list/$', consumers.ListDataConsumer),
]
