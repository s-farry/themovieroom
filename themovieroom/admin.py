
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
            url(r'^update/$', self.admin_view(views.update), name='update'),
            url(r'^preview/(?P<review_id>[0-9]+)/$', self.admin_view(preview), name='preview')
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
        r_new = 630.0 / 400.0
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
    if new_width > 1000:
        new_im = new_im.resize( (1000, int(new_height * 1000 / new_width)), Image.ANTIALIAS)
    new_im.save(path)

from django import forms
from films.models import *
#from froala_editor.widgets import FroalaEditor
from tinymce.widgets import TinyMCE

LOCATION_CHOICES = (
    (0, 'Center'),
    (1, 'Left'),
    (2, 'Right'),
    (3, 'Top'),
    (4, 'Bottom'),
    (5, 'Top-Left'),
    (6, 'Top-Right'),
    (7, 'Bottom-Left'),
    (8, 'Bottom-Right'),
)
NCAST_CHOICES = (
    (0, '0'),
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
    (7, '7'),
    (8, '8'),
    (9, '9'),
    (10, '10'),
    (-1, 'ALL')
)




class ReviewAdminForm(forms.ModelForm):
    imdb = forms.CharField(max_length=9)
    #body = forms.CharField(max_length= 10000, widget = forms.Textarea(attrs = {'rows' : '50', 'cols' : '90'}), label='Review')
    #body = forms.CharField(max_length= 10000, widget = FroalaEditor(options={'toolbarInline': True, 'inlineMode' : True}), label='Review')
    body = forms.CharField(max_length= 10000, widget = TinyMCE(attrs = {'rows' : '30', 'cols' : '30', 'content_style' : "color:#FFFF00", 'body_class': 'review', 'body_id': 'review',}), label='Review')

    synopsis = forms.CharField(max_length= 1000, widget = forms.Textarea(attrs = {'rows' : '10', 'cols' : '90'}))
    quote = forms.CharField(max_length= 500, required = False, widget = forms.Textarea(attrs = {'rows' : '2', 'cols' : '90'}))
    img_crop = forms.ChoiceField(initial=0, choices=LOCATION_CHOICES)
    img_crop_small = forms.ChoiceField(initial=0, choices=LOCATION_CHOICES)
    ncast = forms.ChoiceField(initial=5, choices = NCAST_CHOICES, label='Cast to Show')

    class Meta:
        fields = ('imdb', 'ncast', 'synopsis', 'body', 'quote', 'rating', 'image', 'img_crop', 'image_small', 'img_crop_small')
        model = review

from django.utils import timezone

from django.utils.html import format_html

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'show_link']
    list_filter = [ 'status' ]
    search_fields = [ 'title' ]
    actions = ['make_published']
    
    form = ReviewAdminForm
    def make_published(self, request, queryset):
        rows_updated = queryset.update(status='p')
        for obj in queryset:
            obj.status='p'
            obj.published_data = timezone.now
        if rows_updated == 1:
            message_bit = "1 review was"
        else:
            message_bit = "%s reviews were" % rows_updated
        self.message_user(request, "%s successfully marked as published." % message_bit)
    make_published.short_description = "Mark selected reviews as published"

    def show_link(self, obj):
        if obj.status == 'p' :
            return format_html('<a href="/reviews/{id}">See Here</a>', id=obj.id)
        elif obj.status == 'd' :
            return format_html('<a href="/admin_site/preview/{id}">See Here</a>', id=obj.id)            
    show_link.short_description="Link"

    def get_form(self, request, obj=None, **kwargs):
        form = super(ReviewAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['ncast'].initial = len(obj.cast.all())
        return form


    def get_readonly_fields(self, request, obj=None):
        if obj: #This is the case when obj is already created i.e. it's an edit
            return ['imdb']
        else:
            return []



    def add_people(self, movie, request, ncast=5):
        cast = []
        director = []
        tmdb_cast = movie.credits()['cast']
        tmdb_crew = movie.credits()['crew']
        if ncast == -1:
            ncast = len(tmdb_cast)
        for i in range(min(len(tmdb_cast), ncast)):
            c = tmdb_cast[i]
            pid = c['id']
            tmdb_person = tmdb.People(pid).info()
            if len(person.objects.filter(imdb = tmdb_person['imdb_id'])) > 0:
                pp = person.objects.get(imdb = tmdb_person['imdb_id'])
                cast += [ pp ]
            else:
                names = tmdb_person['name'].split()
                #let's make a guess on this...
                if len(names) == 2:
                    first_name=names[0]
                    last_name=names[1]
                if len(names) == 3:
                    first_name=names[0] + " " + names[1]
                    last_name = names[2]
                elif len(names) == 4:
                    first_name=names[0] + " " + names[1]
                    last_name = names[2] + " " + names[3]
                else:
                    #don't have a better idea but this
                    first_name = names[0]
                    last_name = names[1]
                    for i in range(len(names)-2):
                        lastname += " "+names[i+2]
                dob='1990-01-01'
                if 'birthday' in tmdb_person.keys() and tmdb_person['birthday'] is not None:
                    dob = tmdb_person['birthday']
                g = 'M'
                if tmdb_person['gender'] == 1: g = 'F'
                pp = person(first_name = first_name, last_name = last_name, date_of_birth = dob, gender = g, imdb = tmdb_person['imdb_id'])
                if 'deathday' in tmdb_person.keys() and tmdb_person['deathday'] is not None:
                    pp.date_of_death = tmdb_person['deathday']
                pp.save()
                #self.message_user(request, 'added %s'%(pp.name()))
                cast += [ pp ]
        
        for i in range(len(tmdb_crew)):
            c = tmdb_crew[i]
            if c['job'] != 'Director' : continue
            pid = c['id']
            tmdb_person = tmdb.People(pid).info()
            
            if len(person.objects.filter(imdb = tmdb_person['imdb_id'])) > 0:
                pp = person.objects.get(imdb = tmdb_person['imdb_id'])
                director += [ pp ]
            else:
                names = tmdb_person['name'].split()
                #let's make a guess on this...
                if len(names) == 2:
                    first_name=names[0]
                    last_name=names[1]
                if len(names) == 3:
                    first_name=names[0] + names[1]
                    last_name = names[2]
                elif len(names) == 4:
                    first_name=names[0] + names[1]
                    last_name = names[2] + names[3]
                else:
                    #don't have a better idea but this
                    first_name = names[0]
                    last_name = names[1]
                    for i in range(len(names)-2):
                        lastname += " "+names[i+2]

                dob = '1990-01-01'
                if 'birthday' in tmdb_person.keys() and tmdb_person['birthday'] is not None:
                    dob = tmdb_person['birthday']
                g = 'M'
                if tmdb_person['gender'] == 1: g = 'F'
                pp = person(first_name = first_name, last_name = last_name, date_of_birth = dob, gender = g, imdb = tmdb_person['imdb_id'])
                if 'deathday' in tmdb_person.keys() and tmdb_person['deathday'] is not None:
                    pp.date_of_death = tmdb_person['deathday']
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
        ncast = int(request.POST.get('ncast'))
        img_crop_small = int(request.POST.get('img_crop_small'))
        img_crop = int(request.POST.get('img_crop'))
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
            self.cast, self.director = self.add_people(self.tmdb_movie, request, ncast)
            for c in self.cast: obj.cast.add(c)
            for d in self.director: obj.director.add(d)
        if change and ncast > len(obj.cast.all()):
            if 'tt' in obj.imdb: obj.imdb = obj.imdb.strip('tt')
            f = tmdb.Find('tt'+obj.imdb)
            m = f.info(external_source = "imdb_id")['movie_results'][0]
            self.tmdb_movie = tmdb.Movies(m['id'])
            self.cast, self.director = self.add_people(self.tmdb_movie, request, ncast)
            for c in self.cast:
                if len(obj.cast.filter(imdb=c.imdb)) == 0:
                    obj.cast.add(c)
        if change and ncast < len(obj.cast.all()):
            for i,c in enumerate(obj.cast.all()):
                if i >= ncast:
                    obj.cast.remove(c)

            
        if not change or 'image_small' in form.changed_data:
            if obj.image_small:
                crop_image(obj.image_small.path, home_page = True)
        if not change or 'image' in form.changed_data:
            if obj.image:
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
