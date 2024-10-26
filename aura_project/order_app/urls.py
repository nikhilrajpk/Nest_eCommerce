from django.urls import path
from . import views

app_name = 'order_app'

urlpatterns = [
    path('confirm_order/',views.confirm_order,name='confirm_order'),
    path('order_view/',views.order_view,name='order_view'),
    path('order_details/<int:order_id>/',views.order_details,name='order_details'),
    path('submit_review/<int:product_id>/',views.submit_review,name='submit_review'),
    path('cancel_order/<int:order_id>/',views.cancel_order,name='cancel_order'),
]