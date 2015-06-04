from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^auth/login', views.login_require),
    url(r'^api/get_user$', views.get_user),
    url(r'^api/add_user$', views.add_user),
    url(r'^api/edit_userprofile$', views.edit_userprofile),
]

