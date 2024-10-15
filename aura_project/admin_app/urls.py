from django.urls import path
from . import views

app_name = 'admin_app'

urlpatterns = [
    path('admin_home/',views.admin_home,name='admin_home'),
    path('users/',views.users,name='users'),
    path('user_block/<id>/',views.user_block,name='user_block'),
    path('admin_category/',views.admin_category,name='admin_category'),
    path('category_listed/<id>',views.category_listed,name='category_listed'),
    path('add_category/',views.add_category,name='add_category'),
    path('edit_category/<id>/',views.edit_category,name='edit_category'),
    path('admin_product/',views.admin_product,name='admin_product'),
    path('product_listed/<id>',views.product_listed,name='product_listed'),
    path('add_product/',views.add_product,name='add_product'),
    path('edit_product/<id>/',views.edit_product,name='edit_product'),
]