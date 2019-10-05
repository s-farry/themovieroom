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
    return render(request, 'index.html', {'reviews' : review.objects.filter(status='p').order_by('-published_date')[:5], 'features' : feature.objects.order_by('-published_date')[:3]})

def persons(request, person_id):
    f = get_object_or_404(person, id=person_id)
    return render(request, 'person.html', {'person': f})
def feature_view(request, feature_id):
    f = get_object_or_404(feature, id=feature_id)
    return render(request, 'feature.html', {'feature': f})

def features_view(request):
    return render(request, 'features.html', {'features': feature.objects.filter(status='p').order_by('-published_date')})



def page_not_found(request):
    return render(request, '404.html')

def SearchListView(request):
    query = request.GET.get('search')
    review_results = review.objects.all().filter(title__icontains=query)
    query2 = Q(first_name__icontains=query)
    query2.add(Q(last_name__icontains = query), Q.OR)
    names = query.split()
    if len(names) > 1:
        first = names[0]
        last  = names[1]
        query2.add(Q(first_name__icontains = first, last_name__icontains = last), Q.OR) 
        query2.add(Q(first_name__icontains = last, last_name__icontains = first), Q.OR)   
    person_results = person.objects.filter(query2)
    
    return render(request, 'results.html', {'reviews':review_results, 'persons': person_results, 'query' : query})

from .forms import UpdateHome

def print_movie(block, f,m):
    out = ""
    f.write('{% block '+block+' %}')
    if review.objects.filter(status='p').filter(tmdb=m['id']).exists():
        r = review.objects.get(tmdb=m['id'])
        f.write("<a href=\"{% url 'films:title' '"+str(r.link_title)+"' %}\">"+m["title"]+"</a>&nbsp;&nbsp;")
        for star in r.stars():
            if star == 1: f.write("★")
            elif star == 0.5: f.write("1/2")
    else:
        f.write(m['title'].encode('utf-8'))
    f.write('{% endblock %}\n')
    return out

def update(request):
    if request.method == 'POST':
        film = request.POST.get("film", "")
        a = tmdb.movies.Movies()
        f = open('templates/index.html', 'w')
        outnow = [c for c in a.now_playing(region='GB')['results']][0:8]
        coming = [d for d in a.upcoming(region='GB')['results']][0:8]
        f.write('{% extends "base_index.html" %}\n')
        f.write('{% load common %}\n')
        for i,m in enumerate(outnow):
            print_movie('cinema{}'.format(i+1),f,m)
        for i,m in enumerate(coming):
            print_movie('coming{}'.format(i+1),f,m)
        f.write('{% block body %}\n')
        f.write('{% assign mainid '+str(film)+' %}\n')
        f.write('{{block.super}}\n')
        f.write('{% endblock %}\n')
        return render(request, 'create_home_page.html')
    else:
        return render(request, 'create_home_page.html', {'form' : UpdateHome})
