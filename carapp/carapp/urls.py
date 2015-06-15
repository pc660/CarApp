from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.models import User
from prototype import views

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'carapp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^car/', include('prototype.urls')),
    url(r'^media/(?P<path>.*)','django.views.static.serve',{'document_root':'/Users/chaopan/Documents/workspace/new_carapp/carapp/'}),
)
