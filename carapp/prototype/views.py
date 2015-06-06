from django.http import *
from django.shortcuts import render
from django.conf.urls import url
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import *
from django.views.decorators.csrf import *
from prototype.models import *
from prototype.serializers import *
from datetime import datetime
from django.db.models.base import ObjectDoesNotExist
import random
import json
from views import *

TOKEN_LENGTH = 20

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

SUCCESS = "0"
UNKNOWN_OPERATION = "1"
AUTHENTICATION_FAIL = "2" 
DUPLICATE_KEY = "3"
EMPTY_COLUMN = "4"
NONEXIST_DATA = "5"

error_code = {
    SUCCESS: "Operation success",
    UNKNOWN_OPERATION: "Unknown operation",
    NONEXIST_DATA: "The requested record can not be found",
    AUTHENTICATION_FAIL: "authenticate", 
    DUPLICATE_KEY: "This username has been used",
    EMPTY_COLUMN: "You have empty column"
}

def get_json_data(request):
    if request.method == "GET":
        return request.GET["data"]
    else:
        return request.POST["data"]

def token_generator(length):
    """Generate a token with random letters with length"""

    token_list = \
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    s = []
    for i in range(length):
        s.append(random.choice(token_list))
    return "".join(s) 

# Create your views here.
@csrf_exempt
def login_require(request):
    if request.method == "GET":
        data = request.GET
    else:
        data = request.POST
    user = authenticate(username=data["username"], password=data["password"])
    if user and user.is_active:
        ret = Response(SUCCESS, error_code[SUCCESS])
    else:    
        ret = Response(AUTHENTICATION_FAIL, error_code[AUTHENTICATION_FAIL])
        return HttpResponse(ret.serialize())

    # Generate a token for authentication
    token = token_generator(30)
    try:
        user_token = Token.objects.get(username=data["username"])
        user_token.token = token
        user_token.start_time = datetime.now()
    except:    
        user_token = Token(token=token, username=data["username"])
    user_token.save()
    ret.set_ret("auth_token", token) 
    return HttpResponse(ret.serialize())

def authenticate_user(data):
    """This function is used to check whether the current
    user is authenticated or not"""
    
    try:
        auth_token = data["auth_token"]
        user_token = Token.objects.get(username=data["username"])
        if user_token.token == auth_token:
            return True
    except:
        return False
    return False

 
@csrf_exempt
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
        user = User.objects.get(username=parsed_data["username"])
        user_serializer = UserSerializer(user.appuser)
        ret = Response(SUCCESS, error_code[SUCCESS])
        ret.set_ret("data", user_serializer.serialize())        
    except:
        ret = Response(NONEXIST_DATA, error_code[NONEXIST_DATA]) 
        ret.set_ret("data", parsed_data)  
        return HttpResponse(ret.serialize())
    ret = Response(SUCCESS, error_code[SUCCESS])
    ret.set_ret("data", user_serializer.serialize())  
    return HttpResponse(ret.serialize()) 

@csrf_exempt
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
            last_name=parsed_data["last_name"],
            first_name=parsed_data["first_name"],
            email=parsed_data["email"])
        user.set_password(parsed_data["password"])
        user.save()
        appuser = AppUser.objects.create(
            user=user,
            usertype=parsed_data["usertype"],
            location=parsed_data["location"])
        appuser.save()
    except KeyError as e:
        ret = Response(EMPTY_COLUMN, error_code[EMPEY_COLUMN]) 
        return HttpResponse(ret.serialize())
    except:
        ret = Response(DUPLICATE_KEY, error_code[DUPLICATE_KEY])
        return HttpResponse(ret.serialize())
    ret = Response(SUCCESS, error_code[SUCCESS])
    return HttpResponse(ret.serialize()) 

@csrf_exempt
def edit_userprofile(request):
    """edit an user profile.
    This function needs to be authenticated"""
   
    data = get_json_data(request)
    try:
        parsed_data = json.loads(data) 
        # authentication
        if not authenticate_user(parsed_data):
            ret = Response(AUTHENTICATION_FAIL, error_code[AUTHENTICATION_FAIL])
            return HttpResponse(ret.serialize())
        user = User.objects.get(username=parsed_data["username"]) 
        user.appuser.location = parsed_data["location"]
        user.appuser.usertype = parsed_data["usertype"]
        user.last_name = parsed_data["last_name"]
        user.first_name = parsed_data["first_name"]
        user.email = parsed_data["email"]
        user.save()
        user.appuser.save()
    except KeyError as e:
        ret = Response(EMPTY_COLUMN, error_code[EMPEY_COLUMN]) 
        return HttpResponse(ret.serialize())
    except Exception as e:
        ret = Response(NONEXIST_DATA, error_code[NONEXIST_DATA])
        ret.set_ret("error", str(e))
        return HttpResponse(ret.serialize())
    ret = Response(SUCCESS, error_code[SUCCESS])
    return HttpResponse(ret.serialize()) 

@csrf_exempt
def add_car(request):
    """rest api to add car, login_required"""
    
    data = get_json_data(request)
    try:
        if not authenticate_user(parsed_data):
            ret = Response(AUTHENTICATION_FAIL, error_code[AUTHENTICATION_FAIL])
            return HttpResponse(ret.serialize())
        user = User.objects.get(username=parsed_data["username"])
        car = Car(user=user, 
            used=parsed_data["used"],
            model=parsed_data["model"],
            brand=parsed_data["brand"],
            location=parsed_data["location"],
            year=parsed_data["year"],
            price=parsed_data["price"],
            color=parsed_data["color"],
            title=parsed_data["title"],
            miles=parsed_data["miles"],
            description=parsed_data["description"] 
        )
        car.save()
        car_serializer = CarSerializer(car)
        ret = Response(SUCCESS, error_code[SUCCESS])
        ret.set_ret("data", car_serializer.serialize())
    except KeyError as e:
        ret = Response(EMPTY_COLUMN, error_code[EMPTY_COLUMN])
    except ObjectDoesNotExist as e:
        ret = Response(NONEXIST_DATA, error_code[NONEXIST_DATA])
    return HttpResponse(ret.serialize())

@csrf_exempt
def delete_car(request):
   
    data = get_json_data(request)
    try:
        parsed_data = json.loads(data)
        car = Car.objects.get(car_id=parsed_data["car_id"])
        car.delete()
        ret = Response(SUCCESS, error_code[SUCCESS])
    except ObjectDoesNotExist:
        ret = Response(NONEXIST_DATA, error_code[NONEXIST_DATA])
    return HttpResponse(ret.serialize())

