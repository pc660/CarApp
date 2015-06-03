from django.db import models
from django.contrib.auth.models import User
import json

# Create your models here.
class UserType:
    ADMIN = 0
    CAR_SELLER = 1
    CAR_BUYER = 2

class UserProfile(models.Model):
    """ This is the user profile class"""

    username = models.CharField(max_length=100, primary_key=True)
    user = models.OneToOneField(User)
    usertype = models.IntegerField()
    location = models.CharField(max_length=50)
           

class logging(models.Model):
    """ This class is used to record all user operations,
    Remeber that we might have performance issues if we
    do not do it in parallel. But we ignore this for the
    prototype.
    """

    operation = models.CharField(max_length=50)
    time = models.DateTimeField()    
    comments = models.CharField(max_length=99999)


