# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from datetime import date
from math import floor, ceil
import ast

# Create your models here.
class person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField(default='1990-01-01')
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    imdb = models.CharField(max_length = 7, default='')
    image = models.ImageField(blank=True, upload_to = 'static/images')
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    def name(self):              # __unicode__ on Python 2
        return "%s %s" % (self.first_name, self.last_name)
    def __str__(self):              # __unicode__ on Python 2
        return "%s %s" % (self.first_name, self.last_name)

class film(models.Model):
    title = models.CharField(max_length=200)
    release_date = models.DateField('Release Date', null = True)
    runtime = models.IntegerField(default = 0)
    director = models.ManyToManyField(person, related_name='director')
    cast = models.ManyToManyField(person, related_name='cast')
    imdb = models.CharField(max_length = 7, default='')
    tmdb = models.IntegerField(default = 0)
    def __str__(self):
        return self.title

class review(film):
    body = models.CharField(max_length= 10000)
    synopsis = models.CharField(max_length = 1000, null=True, blank = True, default = '')
    quote = models.CharField(max_length = 500, default = '', null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    RATING_CHOICES = (
        (0, 0),
        (1, 0.5),
        (2, 1),
        (3, 1.5),
        (4, 2),
        (5, 2.5),
        (6, 3.0),
        (7, 3.5),
        (8, 4.0),
        (9, 4.5),
        (10, 5.0),
    )
    rating = models.IntegerField(choices = RATING_CHOICES)
    image = models.ImageField(blank=True, upload_to = 'static/images')
    image_small = models.ImageField(blank=True, upload_to = 'static/images')
    def __str__(self):
        return self.title
    def stars(self):
        starred = []
        if (self.rating <= 10):
            rating = self.rating / 2.0
            for i in range(int(floor(rating))):
                starred += [ 1 ]
            if rating%1 == 0.5:
                starred += [ 0.5]
            for i in range(int(5 - ceil(rating))):
                starred += [ 0 ]
        return starred
    def print_review(self):
        return self.body

class feature(models.Model):
    title = models.CharField(max_length = 200, default = "Feature")
    text = models.CharField(max_length = 10000)
    synopsis = models.CharField(max_length = 1000, default = '')
    image = models.ImageField(blank=True, upload_to = 'static/images')
    image_small = models.ImageField(blank=True, upload_to = 'static/images')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    def name(self):              # __unicode__ on Python 2
        return "%s" % (self.title)
    def __str__(self):              # __unicode__ on Python 2
        return "%s" % (self.title)
