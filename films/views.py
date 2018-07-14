# -*- coding: utf-8 -*-

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import review, film

def index(request):
    return render(request, 'films.html', {'films' : film.objects.all()})

def detail(request, film_id):
    f = get_object_or_404(review, id=film_id)
    return render(request, 'film.html', {'review': f})
    
