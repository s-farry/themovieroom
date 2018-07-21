# -*- coding: utf-8 -*-

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from django.contrib.postgres.search import SearchVector

from films.models import review, film, person, feature
from django.db.models import Q
from .forms import UpdateHome

import tmdbsimple as tmdb
import os
tmdb.API_KEY = os.environ['TMDB_API_KEY']


def index(request):
    return render(request, 'index.html', {'reviews' : review.objects.order_by('-created_date')[:5], 'features' : feature.objects.order_by('-created_date')[:3]})

def persons(request, person_id):
    f = get_object_or_404(person, id=person_id)
    return render(request, 'person.html', {'person': f})

def SearchListView(request):
    query = request.GET.get('search')
    film_results = film.objects.all().filter(title__icontains=query)
    query2 = Q(first_name__icontains=query)
    query2.add(Q(last_name__icontains = query), Q.OR)
    names = query.split()
    if len(names) > 1:
        first = names[0]
        last  = names[1]
        query2.add(Q(first_name__icontains = first, last_name__icontains = last), Q.OR) 
        query2.add(Q(first_name__icontains = last, last_name__icontains = first), Q.OR)   
    person_results = person.objects.filter(query2)
    
    return render(request, 'films.html', {'films':film_results, 'persons': person_results})

from .forms import UpdateHome

def print_movie(f,m):
    out = ""
    if review.objects.filter(tmdb=m['id']).exists():
        r = review.objects.get(tmdb=m['id'])
        f.write("<tr><td> <a href=\"{% url 'films:detail' "+str(r.id)+" %}\">"+m["title"]+"</a>&nbsp;&nbsp;")
        for star in r.stars():
            if star == 1: f.write("★")
            elif star == 0.5: f.write("1/2")
        f.write("</tr></td>")
    else:
        f.write("<tr><td> "+m['title']+"</tr></td>")
    return out

def update(request):
    if request.method == 'POST':
        film = request.POST.get("film", "")
        print film
        a = tmdb.movies.Movies()
        f = open('templates/index.html', 'w')
        outnow = [c for c in a.now_playing(region='GB')['results']][0:8]
        coming = [d for d in a.upcoming(region='GB')['results']][0:8]
        f.write('''
        {% extends "base.html" %}')
        f.write('{% load static %}')
        
        
        {% block title %}My amazing blog{% endblock %}


        {% block sidebar %}

        <table id = "t01"><tbody>
        <tr><th><img height=18px src = {% static 'images/incinema.png' %}>&nbsp;&nbsp;In Cinemas Now</th></tr>
        '''
        )
        for m in outnow:
            print_movie(f,m)
        f.write('''
        <tr><th><img height=18px src = {% static 'images/comingsoon.png' %}>&nbsp;&nbsp;Coming Soon</th></tr>
        ''')
        for m in coming:
            print_movie(f,m)
        f.write('''
        </tbody></table>
        {% endblock %}

        
        {% block image %}
        {% endblock %}
        
        {% block body %}
        ''')

        r = review.objects.get(pk=film)
        f.write("<div class = \"mainsynopsis\">")
        r = review.objects.get(id=film)
        f.write("<a href=\"{% url 'films:detail' "+str(r.id)+" %}\">")
        f.write("<figure class = \"preview\"><img src = "+r.image_small.url+"><br>")
        f.write("""
        <figcaption id = "title"> <h1> %s (%s) </h1>
        """%(r.title,str(r.release_date.year)))
        for star in r.stars():
            if star == 1: f.write("★")
            elif star == 0.5: f.write("1/2")
        f.write("""
        </figcaption>
        <figcaption id = "synopsis">
        %s
        </figcaption>
        """%(r.synopsis.encode("utf8")))
        f.write("</figure>")
        f.write("</a>")
    
        f.write('''
        </div>

        <div class = "synopsis">
        {% for review in reviews %}
        {% if review.id != ''')
        f.write(str(r.pk))
        f.write(''' %}
        <a href = "{% url 'films:detail' review.id %}">
        <figure>
        <img src = "{{review.image_small}}">
        <figcaption>
        {{review.title}} ({{review.release_date.year}})<br>
        {% for star in review.stars  %}
        {% if star == 1 %} ★
        {% elif star == 0.5 %} 1/2
        {% endif %}
        {% endfor %}
        </figcaption>
        </figure>
        </a>
        {% endif %}
        {% endfor %}

        </div>
        <footer class="more"><a href="#">Read More &raquo;</a></footer>
        ''')
        f.write('''
        <div class = "features">
        {% for feature in features %}
        <div class = "feature">
        <h1>{{feature.title}}</h1>
        {{feature.text}}
        </div>
        {% endfor %}
        </div>
        {% endblock %}
        ''')
        f.close()
        return render(request, 'create_home_page.html', {'review' : r})
    else:
        return render(request, 'create_home_page.html', {'form' : UpdateHome})
