from django.urls import path
from . import views

app_name = 'user_app'

urlpatterns = [
    path('',views.home,name='home'),
    path('account/',views.account,name='account'),
    path('add_address/',views.add_address,name='add_address'),
    path('edit_profile/',views.edit_profile,name='edit_profile'),
    path('edit_address/<int:address_id>/',views.edit_address,name='edit_address'),
    path('delete_address/<int:address_id>/',views.delete_address,name='delete_address'),
]