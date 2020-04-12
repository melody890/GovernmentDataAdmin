from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('delete/<int:id>/', views.user_delete, name='delete'),
    path('edit/<int:id>/', views.profile_edit, name='edit'),
    path('register/confirm/<str:code>', views.register_confirm, name='confirm2register'),
    path('reset/',views.reset_password,name='reset'),
    path('reset/confirm/<str:code>',views.reset_confirm,name='confirm2reset'),
]
