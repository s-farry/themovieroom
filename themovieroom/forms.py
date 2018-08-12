from django import forms
from films.models import *

class UpdateHome(forms.Form):
    query = review.objects.filter(status='p')
    film    = forms.ModelChoiceField(queryset=review.objects.order_by('-created_date'))
    if len(query) > 0:
        film.initial = query.order_by('-created_date')[0]
    #feature = forms.ModelChoiceField(queryset=feature.objects.all())

