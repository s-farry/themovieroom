"""themovieroom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import views
from .admin import *

def get_admin_urls(urls):
    def get_urls():
        my_urls = [
            url(r'^my_view/$', admin.site.admin_view(views.update))
        ]
        return my_urls + urls
    return get_urls

admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search/$', views.SearchListView, name='SearchListView'),
    url(r'^person/(?P<person_id>[0-9]+)/$', views.persons, name='persons'),
    url(r'^admin/', admin_site.urls),
    url(r'^admin/update', views.update, name='update'),
    url(r'^films/', include('films.urls')),
]
