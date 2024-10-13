from django.urls import path
from . import views

app_name = 'admin_app'

urlpatterns = [
    path('admin_home/',views.admin_home,name='admin_home'),
    path('users/',views.users,name='users'),
    path('user_block/<id>/',views.user_block,name='user_block'),
]