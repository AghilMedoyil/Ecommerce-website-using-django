from django.urls import path
from . import views


urlpatterns = [
        # Main profile view
    path('account/', views.profile_view, name='profile'),
    
    # Edit profile
    path('orders/list/', views.orders_list, name='orders_list'),
    path('view/order/<int:id>/', views.view_order, name='view_order'),
    path('request/cancel/<int:id>/',views.request_cancel, name='request_cancel'),
    
    path('order/<int:order_id>/invoice/',views.export_invoice, name='export_invoice'),

    
    # # Change password
    # path('change-password/', views.change_password, name='change_password'),
    
    # Address management
    path('address/', views.manage_address, name='manage_address'),
    path('password/change', views.change_pass, name='change_pass'),
    path('address/edit/<int:id>/', views.edit_address, name='edit_address'),
    path('address/add/', views.add_address, name='add_address'),
    path('address/delete/<int:id>/', views.delete_address, name='delete_address'),


    
    # # Order management
    # path('orders/', views.order_list, name='order_list'),
    # path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    # path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    
    # # Password reset (typically handled by Django's auth views, but included here for completeness)
    # path('password-reset/', views.password_reset_request, name='password_reset'),
  
   
]