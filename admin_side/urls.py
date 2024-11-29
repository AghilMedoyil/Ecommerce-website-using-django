from django.urls import path
from . import views


urlpatterns = [
     path('list', views.product_management, name='product_list'),
     path('product/add',views.add_product,name='add_product'),
     path('product/edit/<int:id>/',views.update_product,name='edit_product'),
     path('product/delete/<int:id>/',views.delete_product,name='delete_product'),
     path('category/list',views.category_management,name='category_list'),
     path('category/add',views.add_category,name='add_category'),
     path('category/edit/<int:id>/',views.update_category,name='edit_category'),
     path('category/delete/<int:id>/',views.delete_category,name='delete_category'),
     path('brand/list',views.brand_mangement,name='brand_list'),
     path('brand/add',views.add_brand,name='add_brand'),
     path('brand/edit/<int:id>/',views.update_brand,name='edit_brand'),
     path('brand/delete/<int:id>/',views.delete_brand,name='delete_brand'),
     path('user/activate/<int:id>/',views.user_activate,name='user_active'),
     path('block_user/<int:id>/',views.block_user, name='block_user'),
     path('unblock_user/<int:id>/',views.unblock_user, name='unblock_user'),
     path('block_category/<int:id>/',views.block_category, name='block_category'),
     path('unblock_category/<int:id>/',views.unblock_category, name='unblock_category'),
     path('order/',views.order_management, name='order_management'),
     path('edit/orders/<int:id>/',views.edit_orders, name='edit_orders'),
      path('cancel/orders/<int:id>/',views.cancel_orders, name='cancel_orders'),
      path('approve/denied/<int:id>/',views.approve_denied, name='approve_denied'),
      path('view/orders/<int:id>/',views.view_orders, name='view_orders'),
     path('offer/',views.productOffer, name='product_offer'),
     path('add/offer/',views.add_offer, name='add_offer'),
     path('coupon/',views.coupons, name='coupons'),
     path('add/coupon/',views.add_coupon, name='add_coupon'),
     path('dashboard/',views.dashboard, name='dashboard'),

    






     path('users/',views.user_management,name='users'),



]