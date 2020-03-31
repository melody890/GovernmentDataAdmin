from django.conf.urls import url
from . import views

app_name = 'kgraph'

urlpatterns = [
    url(r'^$', views.get_kgraph, name='kgraph'),
    url(r'^add/$', views.get_ajax, name='kgraphadd'),
]
