# -*- coding: utf-8 -*-

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import review, film

def index(request):
    return render(request, 'reviews.html', {'reviews' : review.objects.filter(status='p').order_by('-published_date')})

def detail(request, review_id):
    r = get_object_or_404(review, id=review_id,status='p')
    return render(request, 'review.html', {'review': r})

def title(request, title):
    r = get_object_or_404(review, link_title = title, status='p')
    return render(request, 'review.html', {'review': r})

def preview(request, review_id):
    r = get_object_or_404(review, id=review_id,status='d')
    return render(request, 'review.html', {'review': r})

