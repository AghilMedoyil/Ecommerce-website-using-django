from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class customer(models.Model):
    LIVE=1
    DELETE=0
    DELETE_CHOICES=((LIVE,'live'),(DELETE,'delete'))
    delete_status=models.IntegerField(choices=DELETE_CHOICES,default=LIVE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)

    
    phone=models.IntegerField(null=True)
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='customer_profile')

class addresses(models.Model):
    LIVE=1
    DELETE=0
    DELETE_CHOICES=((LIVE,'live'),(DELETE,'delete'))
    delete_status=models.IntegerField(choices=DELETE_CHOICES,default=LIVE)
    name=models.CharField(max_length=100)
    address1=models.TextField(null=True)
    address2=models.TextField(null=True)

    city=models.CharField(max_length=200)
    
    district=models.CharField(max_length=200)
    state=models.CharField(max_length=200)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    pincode=models.IntegerField()



