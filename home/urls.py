from django.conf.urls import url
from . import views

app_name = 'home'

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url("error/", views.error_page, name="error"),
]
