from django.urls import path
from . import views

app_name = 'order_app'

urlpatterns = [
    path('confirm_order/',views.confirm_order,name='confirm_order'),
    path('order_view/',views.order_view,name='order_view'),
    path('order_details/<int:order_id>/',views.order_details,name='order_details'),
    path('submit_review/<int:product_id>/',views.submit_review,name='submit_review'),
    path('cancel_order/<int:order_id>/',views.cancel_order,name='cancel_order'),
    path('return_item/<int:item_id>/',views.return_item,name='return_item'),
    path('return_confirm/<int:item_id>/<int:order_id>/',views.return_confirm,name='return_confirm'),
    path('order/<int:order_id>/download-invoice/', views.download_invoice_pdf, name='download_invoice_pdf'),
]