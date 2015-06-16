from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^auth/login', views.login_require),
    url(r'^api/get_user$', views.get_user),
    url(r'^api/add_user$', views.add_user),
    url(r'^api/edit_userprofile$', views.edit_userprofile),
    url(r'^api/add_car$', views.add_car),
    url(r'^api/delete_car$', views.delete_car),
    url(r'^api/edit_car$', views.edit_car),
    url(r'^api/get_cars$', views.get_cars),
    url(r'^api/get_recent_cars', views.get_recent_cars),
    url(r'^api/search_cars', views.search_car_by_brand_model),
    url(r'^api/add_car_index_image', views.add_car_index_image),
    url(r'^api/add_car_image', views.add_car_image),
    url(r'^api/delete_image', views.delete_image), 
    url(r'^api/get_car_images', views.get_car_images),
    url(r'^api/edit_car', views.edit_car),
]

