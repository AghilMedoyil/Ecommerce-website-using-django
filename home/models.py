from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now



# Create your models here.
class customers(models.Model):
    pass
    
class banners(models.Model):
    banner=models.ImageField(upload_to='media/banner/')
    caption=models.TextField()

class products(models.Model):
    pass

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    head = models.TextField()
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
    
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.transaction_type} - ${self.amount} ({self.wallet.user.username})"
