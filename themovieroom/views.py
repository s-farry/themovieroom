from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from django.contrib.postgres.search import SearchVector

from films.models import review, film, person, feature
from django.db.models import Q

def index(request):
    return render(request, 'index.html', {'reviews' : review.objects.order_by('-created_date')[:5], 'features' : feature.objects.order_by('-created_date')[:3]})

def persons(request, person_id):
    f = get_object_or_404(person, id=person_id)
    return render(request, 'person.html', {'person': f})

def SearchListView(request):
    query = request.GET.get('q')
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
