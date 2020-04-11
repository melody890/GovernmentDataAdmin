from django.urls import path
from django.contrib import admin

from . import views

admin.autodiscover()

app_name = 'event'

urlpatterns = [
    path('post/', views.event_post, name='post'),
    path('list/', views.event_list, name='list'),
    path('recent/', views.event_recent, name='recent'),
    path('query/', views.query, name='query'),
]
