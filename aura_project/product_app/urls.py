from django.urls import path
from . import views

app_name = 'product_app'

urlpatterns = [
    path('products_view/<id>/',views.display_products,name='products_view'),
    path('single_product/<id>',views.single_product_view,name='single_product'),
]