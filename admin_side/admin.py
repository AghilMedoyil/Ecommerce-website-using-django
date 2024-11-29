from django.contrib import admin
from . models import product,Category,Brand,multiimage,ProductVarient,ProductOffer
# Register your models here.
admin.site.register(product)
admin.site.register(ProductVarient)
admin.site.register(ProductOffer)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(multiimage)


