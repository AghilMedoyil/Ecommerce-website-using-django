from django.urls import path
from . import views


urlpatterns = [
    path('home/',views.index,name='home'),
   

    path('products/',views.products,name='products'),
    path('search/',views.searchbar,name='searchbar'),
    path('wallet/',views.wallet,name='wallet'),

    path('remove-notification/<int:notification_id>/', views.remove_notification, name='remove_notification'),

    path('productDetails/<int:id>/<str:varient>/',views.product_details,name='productsdetail'),
   
]