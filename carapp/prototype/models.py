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
    location = models.CharField(max_length=50)
          
class Token(models.Model):
    """ This is used for authentication"""
    
    username = models.CharField(primary_key=True, max_length=50)
    token = models.CharField(max_length=50)
    start_time = models.DateTimeField(default=datetime.now)

class Car(models.Model):
    
    user = models.ForeignKey(User)
    car_id = models.IntegerField(primary_key=True, default=uuid.uuid4)
    used = models.BooleanField(default=1)
    model = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    year = models.IntegerField()
    price = models.IntegerField()
    color = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    miles = models.IntegerField()
    description = models.CharField(max_length=999999, blank=True)

class ImageModel(models.Model):
    
    mainimage = models.ImageField(upload_to='img', null = True)
    image = models.ForeignKey(Car)

class logging(models.Model):
    """ This class is used to record all user operations,
    Remeber that we might have performance issues if we
    do not do it in parallel. But we ignore this for the
    prototype.
    """

    operation = models.CharField(max_length=50)
    time = models.DateTimeField()    
    comments = models.CharField(max_length=99999)


