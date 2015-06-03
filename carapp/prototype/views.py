from django.http import *
from django.shortcuts import render
from django.conf.urls import url
from prototype.models import *
from prototype.serializers import *
import json
from views import *

class Response:
    """This class defines the return formats"""
    
    def __init__(self, status, reason):
        self.ret = {}
        self.ret["status"] = status
        self.ret["reason"] = reason
    
    def set_ret(self, key, value):
        self.ret[key] = value

    def serialize(self):
        return json.dumps(self.ret)

SUCCESS = 0
UNKNOWN_OPERATION = 1
AUTHENTICATION_FAIL = 2 
DUPLICATE_KEY = 3
EMPTY_COLUMN = 4
NONEXIST_DATA = 5

error_code = {
    SUCCESS: "Operation success",
    UNKNOWN_OPERATION: "Unknown operation",
    NONEXIST_DATA: "The requested record can not be found"
}

def get_json_data(request):
    if request.method == "GET":
        return request.GET["data"]
    else:
        return request.POST["data"]
    

# Create your views here.
def get_user(request):
    """User api, receive a json object
    {
        "username": chaopan@gmail.com,
        "last_name": chao,
        "first_name": pan,
        .....
    }
    return a json object which is the userprofile object"""
    
    data = get_json_data(request) 
    try:
        parsed_data = json.loads(data) 
        user = UserProfile.objects.get(username=parsed_data["username"]) 
        user_serializer = UserSerializer(user)
        ret = Response(SUCCESS, error_code[SUCCESS])
        ret.set_ret("data", user_serializer.serialize())        
    except:
        ret = Response(NONEXIST_DATA, error_code[NONEXIST_DATA]) 
        ret.set_ret("data", parsed_data)  
        return HttpResponse(ret.serialize())
    ret = Response(SUCCESS, error_code[SUCCESS])
    ret.set_ret("data", user_serializer.serialize())  
    return HttpResponse(ret.serialize()) 

def add_user(request): 
    """User api, receive a json object
    {
        "username": chaopan@gmail.com,
        "last_name": chao,
        "first_name": pan,
        .....
    }
    return a json object which is the userprofile object"""
 
    data = get_json_data(request)
    try:
        parsed_data = json.loads(data) 
        user = User(
            username=parsed_data["username"],
            password=parsed_data["password"],
            last_name=parsed_data["last_name"],
            first_name=parsed_data["first_name"],
            email=parsed_data["email"])
        userprofile = UserProfile(
            username=parsed_data["username"],
            user=user,
            usertype=parsed_data["usertype"],
            location=parsed_data["location"])
        userprofile.save()
    except KeyError as e:
        ret = Response(EMPTY_COLUMN, error_code[EMPEY_COLUMN]) 
        return HttpResponse(ret.serialize())
    except:
        ret = Response(DUPLICATE_KEY, error_code[DUPLICATE_KEY])
        return HttpResponse(ret.serialize())
    ret = Response(SUCCESS, error_code[SUCCESS])
    return HttpResponse(ret.serialize()) 

def edit_userprofile(request):
    """edit an user profile"""
   
    data = get_json_data(request)
    try:
        parsed_data = json.loads(data) 
        user = UserProfile.objects.get(username=json_data["username"]) 
        user.location = parsed_data["location"]
        user.usertype = parsed_data["usertype"]
        user.user.last_name = parsed_data["last_name"]
        user.user.first_name = parsed_data["first_name"]
        user.user.email = parsed_data["email"]
        user.save() 
    except KeyError as e:
        ret = Response(EMPTY_COLUMN, error_code[EMPEY_COLUMN]) 
        return HttpResponse(ret.serialize())
    except:
        ret = Response(DUPLICATE_KEY, error_code[DUPLICATE_KEY])
        return HttpResponse(ret.serialize())
    ret = Response(SUCCESS, error_code[SUCCESS])
    return HttpResponse(ret.serialize()) 

