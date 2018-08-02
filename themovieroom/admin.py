from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User


from . import views
from films.views import *

class MyAdminSite(AdminSite):
    header = 'The Movie Room'
    def get_urls(self):
        from django.conf.urls import url
        urls = super(MyAdminSite, self).get_urls()
        # Note that custom urls get pushed to the list (not appended)
        # This doesn't work with urls += ...
        urls = [
            url(r'^update/$', self.admin_view(views.update), name='update')
        ] + urls
        return urls

import tmdbsimple as tmdb
import os
tmdb.API_KEY = os.environ['TMDB_API_KEY']
from PIL import Image

def crop_image(path, home_page = False, loc = 0):
    im = Image.open(path)
    width, height = im.size   # Get dimensions

    #print "Current width and height: ", width, height
    new_width = width
    new_height = height
    r = 1.0
    if home_page:
        r_new = 630.0 / 466.0
    else:
        r_new = 2.1
    r = float(width) / height

    #print "ratio is ",r, ",will convert to ",r_homepage

    if  r > r_new:
        new_width = height * r_new
    elif r < r_new:
        new_height = width / r_new

    #print "New dimensions ", new_width, new_height
    #default is centre
    left = (width - new_width)/2
    top = (height - new_height)/2
    right = (width + new_width)/2
    bottom = (height + new_height)/2
    
    if loc == '1':
        #print 'cropping to left'
        left = 0
        right = new_width
    elif loc == '2':
        #print 'cropping to right'
        left = width - new_width
        right = width
    elif loc == '3':
      #print "cropping to top"
        top = 0
        bottom = new_height
    elif loc == '4':
      #print 'cropping to bottom'
        top = height - new_height
        bottom = height
    elif loc == '5' :
      #print "cropping to  top left"
        left = 0
        top  = 0
        right =  new_width
        bottom = new_height
    elif loc == '6':
      #print 'cropping to top right'
        left = width - new_width
        right = width
        top = 0
        bottom = new_height
    elif loc == '7' :
    #print "cropping to  bottom left"
        left = 0
        top  = height - new_height
        right =  new_width
        bottom = height
    elif loc == '8':
      #print 'cropping to bottom right'
        left = width - new_width
        right = width
        top = height - new_height
        bottom = height

    new_im = im.crop((left, top, right, bottom))
    if new_width > 600:
        new_im = new_im.resize( (600, int(new_height * 600 / new_width)), Image.ANTIALIAS)
    new_im.save(path)

from django import forms
from films.models import *
#from froala_editor.widgets import FroalaEditor
from tinymce.widgets import TinyMCE


class ReviewAdminForm(forms.ModelForm):
    imdb = forms.CharField(max_length=9)
    #body = forms.CharField(max_length= 10000, widget = forms.Textarea(attrs = {'rows' : '50', 'cols' : '90'}), label='Review')
    #body = forms.CharField(max_length= 10000, widget = FroalaEditor(options={'toolbarInline': True, 'inlineMode' : True}), label='Review')
    body = forms.CharField(max_length= 10000, widget = TinyMCE(attrs = {'rows' : '30', 'cols' : '30'}), label='Review')

    
    synopsis = forms.CharField(max_length= 1000, widget = forms.Textarea(attrs = {'rows' : '10', 'cols' : '90'}))
    quote = forms.CharField(max_length= 500, widget = forms.Textarea(attrs = {'rows' : '2', 'cols' : '90'}))
    class Meta:
        
        fields = ['imdb', 'synopsis', 'body', 'quote', 'rating', 'image', 'image_small']
        model = review

class ReviewAdmin(admin.ModelAdmin):
    
    form = ReviewAdminForm

    def add_people(self, movie, request):
        cast = []
        director = []
        tmdb_cast = movie.credits()['cast']
        tmdb_crew = movie.credits()['crew']
        for i in range(min(len(tmdb_cast), 5)):
            c = tmdb_cast[i]
            pid = c['id']
            tmdb_person = tmdb.People(pid).info()
            try:
                pp = person.objects.get(imdb = tmdb_person['imdb_id'])
                cast += [ pp ]
            except:
                names = tmdb_person['name'].split()
                dob='1990-01-01'
                if 'birthday' in tmdb_person.keys() and tmdb_person['birthday'] is not None:
                    dob = tmdb_person['birthday']
                g = 'M'
                if tmdb_person['gender'] == 1: g = 'F'
                pp = person(first_name = names[0], last_name = names[1], date_of_birth = dob, gender = g, imdb = tmdb_person['imdb_id'])
                pp.save()
                self.message_user(request, 'added %s'%(pp.name()))
                cast += [ pp ]
        
        for i in range(len(tmdb_crew)):
            c = tmdb_crew[i]
            if c['job'] != 'Director' : continue
            pid = c['id']
            tmdb_person = tmdb.People(pid).info()
            
            try:
                pp = person.objects.get(imdb = pid)
                director += [ pp ]
            except:
                names = tmdb_person['name'].split()
                dob = '1990-01-01'
                if 'birthday' in tmdb_person.keys() and tmdb_person['birthday'] is not None:
                    dob = tmdb_person['birthday']
                g = 'M'
                if tmdb_person['gender'] == 1: g = 'F'
                pp = person(first_name = names[0].decode('utf-8'), last_name = names[1].decode('utf-8'), date_of_birth = dob, gender = g, imdb = pid)
                pp.save()
                director += [ pp ]
        return [cast, director]

    def save_form(self, request, form, change):
        #request.GET = request.GET.copy()
        #imdb = request.GET['imdb']
        #if 'tt' in imdb:
        #    request.GET['imdb'] = imdb.strip('tt')
        return super(ReviewAdmin,self).save_form(request,form,change)


    def save_model(self, request, obj, form, change):
        if not change:
            if 'tt' in obj.imdb: obj.imdb = obj.imdb.strip('tt')
            f = tmdb.Find('tt'+obj.imdb)
            m = f.info(external_source = "imdb_id")['movie_results'][0]
            self.tmdb_movie = tmdb.Movies(m['id'])
            obj.title = m['title']
            obj.tmdb = m['id']
            obj.runtime = self.tmdb_movie.info()['runtime']
            obj.release_date = m['release_date']
            self.message_user(request, 'Saving imdb id tt%s as %s'%(obj.imdb,obj.title))
        super(ReviewAdmin, self).save_model(request, obj, form, change)
        if not change:
            self.cast, self.director = self.add_people(self.tmdb_movie, request)
            for c in self.cast: obj.cast.add(c)
            for d in self.director: obj.director.add(d)
        if not change or 'image_small' in form.changed_data:
            crop_image(obj.image_small.path, home_page = True)
        if not change or 'image' in form.changed_data:
            crop_image(obj.image.path, home_page = False)

admin_site = MyAdminSite()
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from films.models import *
# Register your models here.
admin_site.register(User)
admin_site.register(Group)
admin_site.register(film)
admin_site.register(review, ReviewAdmin)
admin_site.register(person)
admin_site.register(feature)
