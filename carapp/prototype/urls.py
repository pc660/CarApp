from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^api/get_user$', views.get_user, name='index'),
]

