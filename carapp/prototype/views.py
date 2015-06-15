from django.http import *
from django.shortcuts import *
from django.conf.urls import url
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import *
from django.views.decorators.csrf import *
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from django.conf import settings
from PIL import Image
from prototype.models import *
from prototype.serializers import *
from datetime import datetime
from django.db.models.base import ObjectDoesNotExist
import random
import json
import os
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

# Index image size
WIDTH = 50
HEIGHT = 50


"""Error codes that are returned by APIs"""
SUCCESS = "0"
UNKNOWN_ERROR = "1"
AUTHENTICATION_FAIL = "2" 
DUPLICATE_KEY = "3"
EMPTY_COLUMN = "4"
NONEXIST_DATA = "5"
OVERFLOW = "6"
INPUT_FORMAT = "7"

# description of error codes 
error_code = {
    SUCCESS: "Operation success",
    UNKNOWN_ERROR: "Unknown Error",
    NONEXIST_DATA: "The requested record can not be found. Detail: {0}",
    AUTHENTICATION_FAIL: "authenticate", 
    DUPLICATE_KEY: "Primary key already exists. {0} ",
    EMPTY_COLUMN: "You have empty column {0}",
    OVERFLOW: "Request has exceeded current database size",
    INPUT_FORMAT: "Input should be a json object. HttpBody should contain data attribute"
}

def get_json_data(request):
    """get data from request"""

    if request.method == "GET":
        return json.loads(request.GET["data"])
    else:
        return json.loads(request.POST["data"])

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
        .....
    }
    return {status, error_code, data(user_info)}
    """ 
    try:
        parsed_data = get_json_data(request) 
        user = User.objects.get(username=parsed_data["username"])
        user_serializer = UserSerializer(user.appuser)
        ret = Response(SUCCESS, error_code[SUCCESS])
        ret.set_ret("data", user_serializer.serialize())        
    except ObjectDoesNotExist as e:
        ret = Response(NONEXIST_DATA, error_code[NONEXIST_DATA].format(e.message)) 
    except ValueError as e:
        ret = Response(INPUT_FORMAT, error_code[INPUT_FORMAT])
    except:
        ret = Response(UNKNOWN_ERROR, error_code[UNKNOWN_ERROR])
    return HttpResponse(ret.serialize()) 

@csrf_exempt
def add_user(request): 
    """User api, receive a json object
    data = 
    {
        "username": chaopan@gmail.com,
        .....
    }
    return {status, error_code, data(user_info)}"""
 
    try:
        parsed_data = get_json_data(request)
        user = User(
            username=parsed_data["username"],
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
        ret = Response(EMPTY_COLUMN, error_code[EMPTY_COLUMN].format(e.message)) 
        return HttpResponse(ret.serialize())
    except IntegrityError as e:
        ret = Response(DUPLICATE_KEY, error_code[DUPLICATE_KEY].format(e.message))
    except ValueError as e:
        ret = Response(INPUT_FORMAT, error_code[INPUT_FORMAT])
    except:
        ret = Response(UNKNOWN_ERROR, error_code[UNKNOWN_ERROR])
    return HttpResponse(ret.serialize()) 

@csrf_exempt
def edit_userprofile(request):
    """edit an user profile.
    This function needs to be authenticated.
    receive a json object
    data = 
    {
        "username": chaopan@gmail.com,
        .....
    }
    update the user profile according to the input.
    return {status, error_code, data(user_info)}"""
   
    try:
        parsed_data = get_json_data(request) 
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
        user.save()
        user.appuser.save()
        ret = Response(SUCCESS, error_code[SUCCESS])
    except KeyError as e:
        ret = Response(EMPTY_COLUMN, error_code[EMPTY_COLUMN].format(e.message)) 
    except ObjectDoesNotExist as e:
        ret = Response(NONEXIST_DATA, error_code[NONEXIST_DATA].format(e.message))
    except ValueError as e:
        ret = Response(INPUT_FORMAT, error_code[INPUT_FORMAT])
    except:
        ret = Response(UNKNOWN_ERROR, error_code[UNKNOWN_ERROR])
    return HttpResponse(ret.serialize()) 

@csrf_exempt
def delete_image(request):
    """Api to delete images"""
    
    try:
        parsed_data = get_json_data(request)
        if not authenticate_user(parsed_data):
            ret = Response(AUTHENTICATION_FAIL, error_code[AUTHENTICATION_FAIL])
            return HttpResponse(ret.serialize())
        image = CarImage(image_id=parsed_data["image_id"])
        image.delete()
    except ObjectDoesNotExist as e:
        ret = Response(NONEXIST_DATA, error_code[NONEXIST_DATA].format(e.message))
    except:
        ret = Response(INPUT_FORMAT, error_code[INPUT_FORMAT])
    return HttpResponse(ret.serialize()) 

@csrf_exempt
def add_car_image(request):
    """Api to add images to the car"""

    try:
        parsed_data = get_json_data(request)
        car_id = parsed_data["car_id"]
        car = Car.objects.get(car_id=car_id)
        # First store the image
        carimage = CarImage(mainimage=request.FILES["image"], car=car)
        carimage.save()
        ret = Response(SUCCESS, error_code[SUCCESS])
    except ObjectDoesNotExist as e:
        ret = Response(NONEXIST_DATA, error_code[NONEXIST_DATA].format(e.message))
    except ValueError as e:
        ret = Response(INPUT_FORMAT, error_code[INPUT_FORMAT])
    except Exception as e:
        ret = Response(UNKNOWN_ERROR, error_code[UNKNOWN_ERROR])
    return HttpResponse(ret.serialize()) 

@csrf_exempt
def add_car_index_image(request):
    """Api to add the introduction image to the car"""

    try:
        parsed_data = get_json_data(request)
        car_id = parsed_data["car_id"]
        car = Car.objects.get(car_id=car_id)
        # First store the image
        carimage = CarImage(mainimage=request.FILES["image"], car=car)
        carimage.save()
        # Next store an index image
        # check img format
        ext = carimage.mainimage.path.split(".")[1]
        # resize
        bigimage = Image.open(carimage.mainimage.path)  
        smallimage = bigimage.resize((WIDTH, HEIGHT), Image.ANTIALIAS)  
        root_path = os.path.join(settings.MEDIA_ROOT, "index")
        if not os.path.exists(root_path):
            os.mkdir(root_path)  
        image_name = "car_{0}_index.{1}".format(car_id, ext)
        image_path = os.path.join(root_path, image_name)
        smallimage.save(image_path)
        # update car
        car.image_url = os.path.join("/media/index/", image_name)
        car.save()
        ret = Response(SUCCESS, error_code[SUCCESS])
    except ObjectDoesNotExist as e:
        ret = Response(NONEXIST_DATA, error_code[NONEXIST_DATA].format(e.message))
    except ValueError as e:
        ret = Response(INPUT_FORMAT, error_code[INPUT_FORMAT])
    except:
        ret = Response(UNKNOWN_ERROR, error_code[UNKNOWN_ERROR])
    return HttpResponse(ret.serialize()) 

@csrf_exempt
def get_car_images(request):
    """Api that get all images of a certain car_id"""
       
    try:
        parsed_data = get_json_data(request)
        car = Car.objects.get(car_id=parsed_data["car_id"])
        images = CarImage.objects.filter(car=car)
        image_path = []
        for image in images:
            image_path.append(ImageSerializer(image).serialize())
        ret = Response(SUCCESS, error_code[SUCCESS])
        ret.set_ret("data", image_path)
    except ObjectDoesNotExist as e:
        ret = Response(NONEXIST_DATA, error_code[NONEXIST_DATA].format(e.message))
    except ValueError as e:
        ret = Response(INPUT_FORMAT, error_code[INPUT_FORMAT])
    except:
        ret = Response(UNKNOWN_ERROR, error_code[UNKNOWN_ERROR])
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
    
    try:
        parsed_data = get_json_data(request)
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
            state=parsed_data["state"],
            city=parsed_data["city"],
            year=parsed_data["year"],
            price=parsed_data["price"],
            color=parsed_data["color"],
            title=parsed_data["title"],
            miles=parsed_data["miles"],
            description=parsed_data["description"], 
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
        ret = Response(EMPTY_COLUMN, error_code[EMPTY_COLUMN].format(e.message))
    except ObjectDoesNotExist as e:
        ret = Response(NONEXIST_DATA, error_code[NONEXIST_DATA].format(e.message))
    except ValueError as e:
        ret = Response(INPUT_FORMAT, error_code[INPUT_FORMAT])
    except Exception as e:
        ret = Response(UNKNOWN_ERROR, error_code[UNKNOWN_ERROR])
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
 
    try:
        parsed_data = get_json_data(request)
        car = Car.objects.get(car_id=parsed_data["car_id"])
        car.delete()
        ret = Response(SUCCESS, error_code[SUCCESS])
    except ObjectDoesNotExist as e:
        ret = Response(NONEXIST_DATA, error_code[NONEXIST_DATA].format(e.message))
    except ValueError as e:
        ret = Response(INPUT_FORMAT, error_code[INPUT_FORMAT])
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
 
    try:
        parsed_data = get_json_data(request)
        if not authenticate_user(parsed_data):
            ret = Response(AUTHENTICATION_FAIL, error_code[AUTHENTICATION_FAIL])
            return HttpResponse(ret.serialize())
        car = Car.objects.get(car_id=parsed_data["car_id"])
        car.vin = parsed_data["vin"],
        car.model = parsed_data["model"]
        car.brand = parsed_data["brand"],
        car.state = parsed_data["state"],
        car.city = parsed_data["city"],
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
        ret = Response(EMPTY_COLUMN, error_code[EMPTY_COLUMN].format(e.message))
    except ObjectDoesNotExist as e:
        ret = Response(NONEXIST_DATA, error_code[NONEXIST_DATA].format(e.message))
    except ValueError as e:
        ret = Response(INPUT_FORMAT, error_code[INPUT_FORMAT])
    except:
        ret = Response(UNKNOWN_ERROR, error_code[UNKNOWN_ERROR]) 
    return HttpResponse(ret.serialize())

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
   
    try:
        parsed_data = get_json_data(request)
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
    except ValueError as e:
        ret = Response(INPUT_FORMAT, error_code[INPUT_FORMAT])
    except:
        ret = Response(UNKNOWN_ERROR, error_code[UNKNOWN_ERROR])
    return HttpResponse(ret.serialize())

@csrf_exempt
def search_car_by_brand_model(request):
    
    try:
        parsed_data = get_json_data(request)
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
    except ValueError as e:
        ret = Response(INPUT_FORMAT, error_code[INPUT_FORMAT])
    except:
        ret = Response(UNKNOWN_ERROR, error_code[UNKNOWN_ERROR])
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
 
    try:
        parsed_data = get_json_data(request)
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
    except ValueError as e:
        ret = Response(INPUT_FORMAT, error_code[INPUT_FORMAT])
    except:
        ret = Response(UNKNOWN_ERROR, error_code[UNKNOWN_ERROR])
    return HttpResponse(ret.serialize())


