from django.urls import path
from . import views

app_name = 'authentication_app'

urlpatterns = [
    path('sign_up/',views.register_view,name = 'sign_up'),
    path('login/',views.login_view,name='login'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('resend_otp/',views.resend_otp_view,name='resend_otp'),
    path('logout/',views.logout_view,name='logout'),
    path('forgot_password/',views.forgot_password_view,name='forgot_password'),
    path('reset_password_otp/',views.verify_otp_reset_password,name='reset_password_otp'),
    path('reset_password_resend_otp/',views.reset_pass_resend_otp,name='reset_password_resend_otp'),
    path('reset_password',views.reset_password_view,name='reset_password'),
    
]