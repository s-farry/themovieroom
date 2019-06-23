# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from datetime import date
from math import floor, ceil
import ast

STATUS_CHOICES = (
    ('d', 'Draft'),
    ('p', 'Published'),
    ('w', 'Withdrawn'),
)


# Create your models here.
class person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField(default='1990-01-01')
    date_of_death = models.DateField(blank=True, null=True)

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    imdb = models.CharField(max_length = 7, default='')
    image = models.ImageField(blank=True, upload_to = 'images')
    tmdb = models.IntegerField(default = 0, blank = True)
    def age(self):
        today = date.today()
        if self.date_of_death:
            today = self.date_of_death
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    def name(self):              # __unicode__ on Python 2
        return "%s %s" % (self.first_name, self.last_name)
    def reviewed_films(self):
        films = []
        for f in self.cast.all():
            if f.review and f.review.status=='p':
                films += [ f ]
        for f in self.director.all():
            if f.review and f.review not in self.cast.all() and f.review.status=='p':
                films += [ f ]
        
        return films

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
    quote = models.CharField(max_length = 500, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(null = True)
    link_title = models.CharField(max_length = 40, default = '')
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
    image = models.ImageField(blank=True, upload_to = 'images')
    image_small = models.ImageField(blank=True, upload_to = 'images')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='d')

    def __str__(self):
        return self.title
    def short_title(self):
        short = self.title.lower.replace(' ','_')
        return short

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
    image = models.ImageField(blank=True, upload_to = 'images')
    image_small = models.ImageField(blank=True, upload_to = 'images')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='d')
    published_date = models.DateTimeField(auto_now=True, null = True)


    def name(self):              # __unicode__ on Python 2
        return "%s" % (self.title)
    def __str__(self):              # __unicode__ on Python 2
        return "%s" % (self.title)
