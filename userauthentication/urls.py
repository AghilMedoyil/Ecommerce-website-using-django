from django.urls import path,include
from . import views


urlpatterns = [
    path('signup/',views.signup_view,name='signup'),
    path('',views.signin_view,name='signin'),
    path('logout/',views.signout,name='logout'),

    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('forgot/verify/otp/<int:id>/', views.verify_forgot_otp, name='verify_forgot_otp'),
    path('password/reset/<int:id>/', views.password_reset, name='password_reset'),


    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('reset/resend/otp/', views.reset_resend_otp, name='reset_resend_otp'),

    path('forgot/password', views.forgotten_password, name='forgot'),
    path('demo-login/',views.demo_login, name='demo_login'),
   


]