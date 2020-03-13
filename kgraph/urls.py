from django.conf.urls import url
from . import views

app_name = 'kgraph'

urlpatterns = [
    url(r'^$', views.get_kgraph, name='kgraph'),
]
