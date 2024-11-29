from django.db import models

from django.contrib.auth.models import User

from PIL import Image
from decimal import Decimal


# Create your models here.
    
class Category(models.Model):
    LIVE=1
    DELETE=0
    DELETE_CHOICES=((LIVE,'live'),(DELETE,'delete'))
    delete_status=models.IntegerField(choices=DELETE_CHOICES,default=LIVE)
    Name=models.CharField(max_length=200)
    description=models.TextField()


    def soft_delete(self):
        self.delete_status= self.DELETE
        self.save()

        self.products.update(delete_status=self.DELETE)
    def restore(self):
            """Restore the category and its related products."""
            self.delete_status = self.LIVE
            self.save()
            
            
            # Restore all related products
            self.products.update(delete_status=self.LIVE)
    @property
    def products(self):
        return product.objects.filter(category=self)

    def __str__(self) -> str:
        return self.Name
    
class Brand(models.Model):
    LIVE=1
    DELETE=0
    DELETE_CHOICES=((LIVE,'live'),(DELETE,'delete'))
    delete_status=models.IntegerField(choices=DELETE_CHOICES,default=LIVE)
    Name=models.CharField(max_length=200)
    description=models.TextField()

    def __str__(self) -> str:
        return self.Name
    
class product(models.Model):
    LIVE=1
    DELETE=0
    DELETE_CHOICES=((LIVE,'live'),(DELETE,'delete'))
    title=models.CharField(max_length=200)
   
    description=models.TextField()
    brand=models.ForeignKey(Brand,on_delete=models.SET_NULL,null=True,related_name='Product')
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name='products',null=True)
    image=models.ImageField(upload_to='products/')
    delete_status=models.IntegerField(choices=DELETE_CHOICES,default=LIVE,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    sold_count = models.PositiveIntegerField(default=0)  # Tracks total units sold


    def soft_delete(self):
        self.delete_status=self.DELETE
        self.save()
    
    def restore(self):
        self.delete_status=self.LIVE
        self.save()

    def __str__(self) -> str:
        return self.title
    
    
    
class multiimage(models.Model):
    product=models.ForeignKey(product,on_delete=models.CASCADE)
    img=models.ImageField(upload_to='images/')

    
    
class ProductVarient(models.Model):
    products=models.ForeignKey(product,on_delete=models.CASCADE,related_name='varients')
    SIZE_CHOICES = [
        ('S','small'),
        ('M','meduim'),
        ('L','large'),

    ]
    size=models.CharField(max_length=2,choices=SIZE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)

    def get_discounted_price(self):
        if hasattr(self, 'offer') :
            return self.price - (self.price * self.offer.discount / Decimal(100))
        return self.price

class CategoryOffer(models.Model):
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    discount_percentage=models.FloatField(default=0)
    discount_price=models.FloatField(default=0,null=True,blank=True)
    
class ProductOffer(models.Model):
    Product=models.ForeignKey(product,on_delete=models.CASCADE)
    Varient=models.ForeignKey(ProductVarient,on_delete=models.CASCADE,related_name='offer')
    discount = models.DecimalField(max_digits=5, decimal_places=2, help_text="Discount percentage")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    discount_price=models.FloatField(default=0,null=True,blank=True)
    name=models.CharField(max_length=100)
    description=models.TextField()
    

  
