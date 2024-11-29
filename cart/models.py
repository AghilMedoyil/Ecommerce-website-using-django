from django.db import models
from django.contrib.auth.models import User
from admin_side.models import product,ProductVarient
from userprofile.models import addresses, customer
from django.utils import timezone
from django.utils.timezone import now


# Create your models here.
class cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    products=models.ManyToManyField(product,through='cartitem')
    created_at=models.DateTimeField(auto_now=True)

class cartitem(models.Model):
    Product=models.ForeignKey(product,on_delete=models.CASCADE)
    varient=models.ForeignKey(ProductVarient,on_delete=models.CASCADE,null=True,blank=True)
    quantity=models.PositiveIntegerField(default=1)
    price=models.DecimalField(default=0.00,max_digits=10,decimal_places=2)
    Cart=models.ForeignKey(cart,on_delete=models.CASCADE)

class Orders(models.Model):
    ORDER_STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
    ('Refund', 'Refund'),
    ('Dispatch', 'Dispatch'),
    ('Return','Return') 
    ]
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')
    cancellation_requested = models.BooleanField(default=False)
    CANCELLATION_PENDING = 'Pending'
    CANCELLATION_APPROVED = 'Approved'
    CANCELLATION_REJECTED = 'Rejected'

    CANCELLATION_STATUS_CHOICES = [
        (CANCELLATION_PENDING, 'Pending'),
        (CANCELLATION_APPROVED, 'Approved'),
        (CANCELLATION_REJECTED, 'Rejected'),
    ]

    cancellation_status = models.CharField(
        max_length=10,
        choices=CANCELLATION_STATUS_CHOICES,
        default=CANCELLATION_PENDING,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_time = models.DateTimeField(auto_now_add=True)
    user_mobile = models.ForeignKey(customer, on_delete=models.SET_NULL, null=True, blank=True)
    user_address = models.TextField()
    total_price = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    grand_total = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    shipping_price= models.DecimalField(max_digits=10,decimal_places=2,default=30.00)
    tax= models.DecimalField(max_digits=10,decimal_places=2,default=10.00)
    discount=models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    cancellation_reason=models.TextField(null=True, blank=True)
    payment_method=models.CharField(max_length=20,null=True,blank=True)
    
class order_item(models.Model):
    order=models.ForeignKey(Orders,related_name='items',on_delete=models.CASCADE)
    product_quantity = models.PositiveIntegerField(null=True, blank=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(product, on_delete=models.CASCADE,null=True,blank=True,related_name='orderitems')
    varient=models.ForeignKey(ProductVarient,on_delete=models.CASCADE,null=True,blank=True)
    
class Coupons(models.Model):
    code=models.CharField(max_length=50,unique=True)
    discount_percentage=models.FloatField(default=0)
    discount_price=models.FloatField(default=0,null=True,blank=True)
    valid_from = models.DateTimeField(null=True)
    valid_to = models.DateTimeField(null=True)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    maximum_usage_count = models.PositiveIntegerField(default=5)
    minimum_cart_value = models.DecimalField(max_digits=10, decimal_places=2, default=300)  # Add this field
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, default=2000, null=True)
    def __str__(self):
        return self.code
    
    def check_and_update_expiry(self):
        if self.valid_to < now():
            self.is_active = False
            self.save()
    
class coupon_usage(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    coupon=models.ForeignKey(Coupons,on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ['user', 'coupon']

    def __str__(self):
        return f"{self.user.username} - {self.coupon.code}"


class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    products=models.ManyToManyField(product,through='WishlistItem')
    created_at=models.DateTimeField(auto_now_add=True)

class WishlistItem(models.Model):
    wishlist=models.ForeignKey(Wishlist,on_delete=models.CASCADE)
    Product=models.ForeignKey(product,on_delete=models.CASCADE)
    size = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    variant_stock_quantity = models.PositiveIntegerField(default=0)
    

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]

    order = models.OneToOneField(Orders, on_delete=models.CASCADE, related_name='payment')
    transaction_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=20, default='PayPal')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order {self.order.order_id} - {self.payment_status}"

