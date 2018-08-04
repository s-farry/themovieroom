from django import forms
from films.models import *

class UpdateHome(forms.Form):
    #film    = forms.ModelChoiceField(queryset=review.objects.order_by('-created_date'), initial = review.objects.order_by('-created_date')[0])
    feature = forms.ModelChoiceField(queryset=feature.objects.all())

