# -*- coding: utf-8 -*-

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import review, film

def index(request):
    return render(request, 'reviews.html', {'films' : review.objects.filter(status='p')})

def detail(request, review_id):
    r = get_object_or_404(review, id=review_id)
    return render(request, 'review.html', {'review': r})

