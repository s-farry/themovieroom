# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import *
# Register your models here.
admin.site.register(film)
admin.site.register(review)
admin.site.register(person)
admin.site.register(feature)
