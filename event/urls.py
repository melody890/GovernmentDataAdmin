from django.urls import path
from django.contrib import admin

from . import views

admin.autodiscover()

app_name = 'event'

urlpatterns = [
    path('post/', views.event_post, name='post'),
    path('list/', views.event_list, name='list'),
]
