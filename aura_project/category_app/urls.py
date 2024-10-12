from django.urls import path
from . import views

app_name = 'category_app'

urlpatterns = [
    path('category/',views.category_view,name='category')
]