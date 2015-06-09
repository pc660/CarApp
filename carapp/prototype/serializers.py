from django.contrib.auth.models import User, Group
from prototype.models import *

def get_attr_recursively(instance, key):
        if not key:
            return instance
        
        next_instance = getattr(instance, key[0])
        return get_attr_recursively(next_instance, key[1:])


class Serializer:
    def __init__(self):
        self.fields = []

    def serialize(self):
        json_ret = {}
        for key in self.fields:
            key_list = key.split(".")
            value = get_attr_recursively(self.instance, key_list) 
            json_ret[key] = str(value)
        return json.dumps(json_ret)        

class UserSerializer(Serializer):
    """Serialize class to serialize UserProfile"""

    def __init__(self, instance):
        self.fields = [
            "user.username",
            "user.last_name",
            "user.first_name",
            "usertype",
            "location"
        ]
        self.instance = instance

class CarSerializer(Serializer):
    """Serialize class to serialize Car model""" 

    def __init__(self, instance):
        self.fields = [
            "user.username",
            "car_id",
            "vin",
            "used",
            "model",
            "brand",
            "location",
            "year",
            "price",
            "color",
            "title",
            "miles",
            "description"  
        ]
        self.instance = instance
    
