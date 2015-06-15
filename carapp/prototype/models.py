from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import json
import uuid

# Create your models here.
class UserType:
    ADMIN = 0
    CAR_SELLER = 1
    CAR_BUYER = 2

class AppUser(models.Model):
    """ This is the user profile class"""

    user = models.OneToOneField(User)
    usertype = models.IntegerField(default=UserType.CAR_SELLER)
    state = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=50, null=True)
    phone = models.CharField(max_length=10)
       
 
class Token(models.Model):
    """ This is used for authentication"""
    
    username = models.CharField(primary_key=True, max_length=50)
    token = models.CharField(max_length=50)
    start_time = models.DateTimeField(default=datetime.now)

class Car(models.Model):
    
    user = models.ForeignKey(User)
    car_id = models.AutoField(primary_key=True)
    vin = models.CharField(max_length=50, null=True)
    model = models.CharField(max_length=50, null=True)
    brand = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    year = models.IntegerField(null=True)
    price = models.IntegerField(null=True)
    color = models.CharField(max_length=50, null=True)
    title = models.CharField(max_length=100, null=True)
    miles = models.IntegerField(null=True)
    description = models.CharField(max_length=999999, null=True)
    last_edit = models.DateTimeField(default=datetime.now)
    image_url = models.CharField(max_length=100, null=True)
    tag0 = models.BooleanField(default=False)
    tag1 = models.BooleanField(default=False)
    tag2 = models.BooleanField(default=False)
    tag3 = models.BooleanField(default=False)
    tag4 = models.BooleanField(default=False)
    tag5 = models.BooleanField(default=False)
    tag6 = models.BooleanField(default=False)
    tag7 = models.BooleanField(default=False)
    
class CarImage(models.Model):
    
    mainimage = models.FileField(upload_to='imgs')
    car = models.ForeignKey(Car)
    image_id = models.AutoField(primary_key=True)

class logging(models.Model):
    """ This class is used to record all user operations,
    Remeber that we might have performance issues if we
    do not do it in parallel. But we ignore this for the
    prototype.
    """

    operation = models.CharField(max_length=50)
    time = models.DateTimeField()    
    comments = models.CharField(max_length=99999)
