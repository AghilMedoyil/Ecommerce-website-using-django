from django.contrib import admin

from . models import Orders,cart,cartitem,order_item,Coupons,coupon_usage,Wishlist,WishlistItem
# Register your models here.
admin.site.register(Orders)
admin.site.register(order_item)
admin.site.register(Coupons)
admin.site.register(coupon_usage)
admin.site.register(Wishlist)
admin.site.register(WishlistItem)



admin.site.register(cart)
admin.site.register(cartitem)
