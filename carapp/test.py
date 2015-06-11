from prototype.models import *
from prototype.views import *

# Create user
user = User(username="test1@gmail.com")
user.set_password("111")
user.save()
appuser = AppUser.objects.create(user=user, usertype="0", state="ca", city="mv", 
address="home")
appuser.save()

# Create token
token = Token(username="test1@gmail.com", token="1")
token.save()

# Create Car
car1 = Car(user=user, model="audi", brand="a4", state="ca", city="mv",
year="1991", price="100", color="black", title="manimabi", miles="123",
description="bbb", tag1=True, tag2=True)
car1.save()

car2 = Car(user=user, model="BWM", brand="s5", state="ca", city="sj",
year="1991", price="100", color="black", title="manimabi", miles="123",
description="bbb", tag1=True, tag3=True)
car2.save()

car3 = Car(user=user, model="tesla", brand="S", state="ca", city="sf",
year="1991", price="100", color="black", title="manimabi", miles="123",
description="bbb", tag1=True, tag4=True)
car3.save()



