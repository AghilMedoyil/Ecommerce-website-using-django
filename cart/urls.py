from django.urls import path
from . import views


urlpatterns = [
     path('cart/', views.view_cart, name='cart'),
     path('addtocart/<int:id>', views.add_to_cart, name='addtocart'),
     path('removecart/<int:id>', views.remove_cartitem, name='removecart'),
     path('quantity/minus/<int:item_id>', views.quantity_minus, name='quantity_minus'),
     path('quantity/add/<int:item_id>', views.quantity_plus, name='quantity_plus'),

     path('checkout/', views.checkout, name='checkout'),
     path('apply/coupon/', views.apply_coupon, name='apply_coupon'),
     path('wishlist/', views.wishlist, name='wishlist'),
     path('add/to/wishlist/<int:id>/', views.add_to_wishlist, name='addtowishlist'),
     path('remove/wishlist/<int:id>', views.remove_wishitem, name='removewishlist'),
     path('wishlist/addtocart/<int:id>', views.add_to_wishlistcart, name='addtowishlistcart'),
     path('order/success/<int:id>', views.order_success, name='order_success'),

     path('payment/success', views.payment_success, name='payment-success'),
     path('payment/failed', views.payment_failed, name='payment-failed'),

     
]