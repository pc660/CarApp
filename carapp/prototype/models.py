from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import json

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
 
class logging(models.Model):
    """ This class is used to record all user operations,
    Remeber that we might have performance issues if we
    do not do it in parallel. But we ignore this for the
    prototype.
    """

    operation = models.CharField(max_length=50)
    time = models.DateTimeField()    
    comments = models.CharField(max_length=99999)


