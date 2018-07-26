# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views

app_name = 'films'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<review_id>[0-9]+)/$', views.detail, name='detail'),
    # ex: /polls/5/results/
]
