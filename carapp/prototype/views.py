from django.http import *
from django.shortcuts import *
from django.conf.urls import url
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import *
from django.views.decorators.csrf import *
from django.core.urlresolvers import reverse

from prototype.forms import *
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
        # Remove duplicate / before "
        cur_str = json.dumps(self.ret)
        return cur_str 


"""Error codes that are returned by APIs"""
SUCCESS = "0"
UNKNOWN_OPERATION = "1"
AUTHENTICATION_FAIL = "2" 
DUPLICATE_KEY = "3"
EMPTY_COLUMN = "4"
NONEXIST_DATA = "5"
OVERFLOW = "6"

# description of error codes 
error_code = {
    SUCCESS: "Operation success",
    UNKNOWN_OPERATION: "Unknown operation",
    NONEXIST_DATA: "The requested record can not be found",
    AUTHENTICATION_FAIL: "authenticate", 
    DUPLICATE_KEY: "This username has been used",
    EMPTY_COLUMN: "You have empty column",
    OVERFLOW: "Request has exceeded current database size"
}

def get_json_data(request):
    """get data from request"""

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
"""All apis will receive a json object and return a json object,
Input format:
data = 
{
    arg1 = value1,
    arg2 = value2,
    ...
}
output format:
{
    status: error_code,
    reason: error_description,
    data: json_data
}
"""


@csrf_exempt
def login_require(request):
    """Login api.
    Require username and password.
    return {stats, error_code, data(user info), auth_token}"""

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
    user = User.objects.get(username=data["username"])
    ret.set_ret("data", UserSerializer(user.appuser).serialize())
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
    data = 
    {
        "username": chaopan@gmail.com,
        "last_name": chao,
        "first_name": pan,
        .....
    }
    return {status, error_code, data(user_info)}
    """ 
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
    return HttpResponse(ret.serialize()) 

@csrf_exempt
def add_user(request): 
    """User api, receive a json object
    data = 
    {
        "username": chaopan@gmail.com,
        "last_name": chao,
        "first_name": pan,
        .....
    }
    return {status, error_code, data(user_info)}"""
 
    data = get_json_data(request)
    try:
        parsed_data = json.loads(data) 
        user = User(
            username=parsed_data["username"],
            last_name=parsed_data["last_name"],
            first_name=parsed_data["first_name"],
        )
        user.set_password(parsed_data["password"])
        user.save()
        appuser = AppUser.objects.create(
            user=user,
            usertype=parsed_data["usertype"],
            phone=parsed_data["phone"],
            state=parsed_data["state"],
            city=parsed_data["city"],
            address=parsed_data["address"]
        )
        appuser.save()
        # Generate response
        ret = Response(SUCCESS, error_code[SUCCESS])
        user_serializer = UserSerializer(appuser)
        ret.set_ret("data", user_serializer.serialize())        
        
        # Generate a token for authentication
        token = token_generator(30)
        user_token = Token(token=token, username=user.username)
        user_token.save()
        ret.set_ret("auth_token", token)
    except KeyError as e:
        ret = Response(EMPTY_COLUMN, error_code[EMPEY_COLUMN]) 
        return HttpResponse(ret.serialize())
    except:
        ret = Response(DUPLICATE_KEY, error_code[DUPLICATE_KEY])
        return HttpResponse(ret.serialize())
    return HttpResponse(ret.serialize()) 

@csrf_exempt
def edit_userprofile(request):
    """edit an user profile.
    This function needs to be authenticated.
    receive a json object
    data = 
    {
        "username": chaopan@gmail.com,
        "last_name": chao,
        "first_name": pan,
        .....
    }
    update the user profile according to the input.
    return {status, error_code, data(user_info)}"""
   
    data = get_json_data(request)
    try:
        parsed_data = json.loads(data) 
        # authentication
        if not authenticate_user(parsed_data):
            ret = Response(AUTHENTICATION_FAIL, error_code[AUTHENTICATION_FAIL])
            return HttpResponse(ret.serialize())
        user = User.objects.get(username=parsed_data["username"]) 
        user.appuser.phone = parsed_data["phne"],
        user.appuser.state = parsed_data["state"],
        user.appuser.city = parsed_data["city"],
        user.appuser.address = parsed_data["address"],
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
        return HttpResponse(ret.serialize())
    ret = Response(SUCCESS, error_code[SUCCESS])
    return HttpResponse(ret.serialize()) 

@csrf_exempt
def add_car(request):
    """api to add car
    This function needs to be authenticated
    data = 
    {
        "username": chaopan@gmail.com,
        "used": 0,
        "model": "audi",
        .....
    }
    add a car into user with username=username
    return {status, error_code, data(car_info)}
    """
    
    data = get_json_data(request)
    try:
        parsed_data = json.loads(data)
        if not authenticate_user(parsed_data):
            ret = Response(AUTHENTICATION_FAIL, error_code[AUTHENTICATION_FAIL])
            return HttpResponse(ret.serialize())
        user = User.objects.get(username=parsed_data["username"])
        tags = parsed_data["tags"].split(",")
        tag_list = [False for i in range(8)]  
        for i in tags:
            tag_list[int(i)] = True
        car = Car(user=user, 
            vin=parsed_data["vin"],
            model=parsed_data["model"],
            brand=parsed_data["brand"],
            location=parsed_data["location"],
            year=parsed_data["year"],
            price=parsed_data["price"],
            color=parsed_data["color"],
            title=parsed_data["title"],
            miles=parsed_data["miles"],
            state=parsed_data["state"],
            city=parsed_data["city"],
            description=parsed_data["description"] 
            tag0=tag_list[0],
            tag1=tag_list[1],
            tag2=tag_list[2],
            tag3=tag_list[3],
            tag4=tag_list[4],
            tag5=tag_list[5],
            tag6=tag_list[6],
            tag7=tag_list[7]
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
    """Delete the car with the car_id
    receive a json object
    data = 
    {
        car_id = "1"
    }
    return {status, error_code}
    """  
 
    data = get_json_data(request)
    try:
        parsed_data = json.loads(data)
        car = Car.objects.get(car_id=parsed_data["car_id"])
        car.delete()
        ret = Response(SUCCESS, error_code[SUCCESS])
    except ObjectDoesNotExist:
        ret = Response(NONEXIST_DATA, error_code[NONEXIST_DATA])
    return HttpResponse(ret.serialize())

@csrf_exempt
def edit_car(request):
    """Edit the car info given car_id
    receive a json object
    data = 
    {
        car_id = "1",
        used = "2",
        model = "3",
        .....
    }
    return {status, error_code, data(car_info)}
    """  
 
    data = get_json_data(request)
    try:
        parsed_data = json.loads(data)
        if not authenticate_user(parsed_data):
            ret = Response(AUTHENTICATION_FAIL, error_code[AUTHENTICATION_FAIL])
            return HttpResponse(ret.serialize())
        car = Car.objects.get(car_id=parsed_data["car_id"])
        car.vin = parsed_data["vin"],
        car.model = parsed_data["model"]
        car.brand = parsed_data["brand"],
        car.location = parsed_data["location"],
        car.year = parsed_data["year"],
        car.price = parsed_data["price"],
        car.color = parsed_data["color"],
        car.title = parsed_data["title"],
        car.miles = parsed_data["miles"],
        car.state = parsed_data["state"],
        car.city = parsed_data["city"],
        car.description = parsed_data["description"] 
        tags = parsed_data["tags"].split(",")
        tag_list = [False for i in range(8)]  
        for i in tags:
            tag_list[int(i)] = True
        car.tag0 = tag_list[0],
        car.tag1 = tag_list[1],
        car.tag2 = tag_list[2],
        car.tag3 = tag_list[3],
        car.tag4 = tag_list[4],
        car.tag5 = tag_list[5],
        car.tag6 = tag_list[6],
        car.tag7 = tag_list[7]
          
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
def test_image(request):
    if request.method == 'POST':
        import pdb
        pdb.set_trace()
        newdoc = Document(docfile = request.FILES['userfile'])
        newdoc.save()
        return HttpResponse(str(request.FILES))
    else:
        form = DocumentForm()
    documents = Document.objects.all()
    return render_to_response(
        'prototype/list.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )

@csrf_exempt
def get_cars(request):
    """Get all cars from user
    receive a json object
    data = 
    {
       username = "username" 
    }
    return {status, error_code, data([car1_info, car2_info, ...])}
    """
   
    data = get_json_data(request)
    
    try:
        parsed_data = json.loads(data)
        if not authenticate_user(parsed_data):
            ret = Response(AUTHENTICATION_FAIL, error_code[AUTHENTICATION_FAIL])
            return HttpResponse(ret.serialize())
        ret_list = []
        user = User.objects.get(username=parsed_data["username"])
        cars = Car.objects.filter(user=user)
        sorted_cars = sorted(cars, key=lambda x: x.last_edit, reverse=True)
        ret = Response(SUCCESS, error_code[SUCCESS])
        for car in sorted_cars:
            car_serial = CarSerializer(car)
            ret_list.append(car_serial.serialize())
        ret.set_ret("data", ret_list) 
    except IndexError as e:
        ret = Response(OVERFLOW, error_code[OVERFLOW])
    return HttpResponse(ret.serialize())

@csrf_exempt
def search_car_by_brand_model(request):
    
    data = get_json_data(request)
    try:
        parsed_data = json.loads(data)
        brand = parsed_data["brand"]
        model = parsed_data["model"]
       
        set1 = None
        set2 = None 
        if brand:
            set1 = set(Car.objects.filter(brand=brand))
        if model:
            set2 = set(Car.objects.filter(model=model))
        if set1 and set2:
            ret_set = set1 & set2
        elif set1:
            ret_set = set1
        else:
            ret_set = set2
        ret = Response(SUCCESS, error_code[SUCCESS])
        ret_list = []
        car_list = list(ret_set)
        start = int(parsed_data["start"])
        end = int(parsed_data["end"])
        end = min(end, len(car_list) - 1)
        car_list = car_list[start : end + 1]
        sorted_cars = sorted(car_list, key=lambda x: x.last_edit, reverse=True)
        for car in sorted_cars:
            car_serial = CarSerializer(car)
            ret_list.append(car_serial.serialize())
        ret.set_ret("data", ret_list) 
    except IndexError as e:
        ret = Response(OVERFLOW, error_code[OVERFLOW])
    return HttpResponse(ret.serialize())


@csrf_exempt
def get_recent_cars(request):
    """Get the most recent posted cars
    receive a json object
    data = 
    {
        start = 1, 
        end = 2
    }
    return {status, error_code, data(sorted_cars[start:end])}
    """   
 
    data = get_json_data(request)
    try:
        parsed_data = json.loads(data)
        ret_list = []
        cars = Car.objects.all()
        sorted_cars = sorted(cars, key=lambda x: x.last_edit, reverse=True)
        start = int(parsed_data["start"])
        end = int(parsed_data["end"])
        end = min(end, len(sorted_cars) - 1)
        car_list = sorted_cars[start : end + 1]
        ret = Response(SUCCESS, error_code[SUCCESS])
        for car in car_list:
            car_serial = CarSerializer(car)
            ret_list.append(car_serial.serialize())
        ret.set_ret("data", ret_list) 
    except IndexError as e:
        ret = Response(OVERFLOW, error_code[OVERFLOW])
    return HttpResponse(ret.serialize())


