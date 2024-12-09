from django.contrib import admin
from . models import Notification,Wallet,WalletTransaction
# Register your models here.
admin.site.register(Notification)
admin.site.register(Wallet)
admin.site.register(WalletTransaction)


