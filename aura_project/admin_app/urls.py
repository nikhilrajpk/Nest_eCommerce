from django.urls import path
from . import views
from .views import SalesReportView
app_name = 'admin_app'

urlpatterns = [
    path('admin_home/',views.admin_home,name='admin_home'),
    
    path('users/',views.users,name='users'),
    path('user_block/<id>/',views.user_block,name='user_block'),
    
    path('admin_category/',views.admin_category,name='admin_category'),
    path('category_listed/<id>',views.category_listed,name='category_listed'),
    path('add_category/',views.add_category,name='add_category'),
    path('edit_category/<id>/',views.edit_category,name='edit_category'),
    path('top_selling_category/',views.top_selling_category,name='top_selling_category'),
    
    path('admin_product/',views.admin_product,name='admin_product'),
    path('product_listed/<id>',views.product_listed,name='product_listed'),
    path('add_product/',views.add_product,name='add_product'),
    path('edit_product/<id>/',views.edit_product,name='edit_product'),
    path('add_stock/<int:product_id>/',views.add_stock,name='add_stock'),
    path('top_selling_products/',views.top_selling_products,name='top_selling_products'),
    
    path('admin_offer/',views.admin_offer,name='admin_offer'),
    path('add_offer/',views.add_offer,name='add_offer'),
    path('edit_offer/<id>/',views.edit_offer,name='edit_offer'),
    path('remove_offer/<id>/',views.remove_offer,name='remove_offer'),
    
    path('admin_banner/',views.admin_banner,name='admin_banner'),
    path('add_banner/',views.add_banner,name='add_banner'),
    path('edit_banner/<id>/',views.edit_banner,name='edit_banner'),
    path('remove_banner/<id>/',views.remove_banner,name='remove_banner'),
    
    path('admin_coupon/',views.admin_coupon,name='admin_coupon'),
    path('add_coupon/',views.add_coupon,name='add_coupon'),
    path('edit_coupon/<int:coupon_id>/',views.edit_coupon,name='edit_coupon'),
    path('remove_coupon/<int:coupon_id>/',views.remove_coupon,name='remove_coupon'),
    
    path('admin_orders/',views.admin_orders,name='admin_orders'),
    path('show_order/<int:order_id>/',views.show_order,name='show_order'),
    
    path('sales-report/', SalesReportView.as_view(), name='sales_report'),
]