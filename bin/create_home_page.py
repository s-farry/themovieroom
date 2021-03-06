# -*- coding: utf-8 -*-

import tmdbsimple as tmdb
import django, os
os.environ["DJANGO_SETTINGS_MODULE"] = "moviereviews.settings"
django.setup()

from films.models import film, person, review

if len(os.sys.argv) != 2:
    print 'Only one argument is required:'
    os.sys.exit(2)

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
    
tmdb.API_KEY = '8cf2bbd6e9aa1a32c36bd9bb68afa0c9'
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

f.write("<h1>Latest Reviews</h1> </br>")
f.write("<div class = \"mainsynopsis\">")
r = review.objects.get(id=os.sys.argv[1])
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
"""%(r.synopsis))
f.write("</figure>")
f.write("</a>")

f.write('''
</div>

<div class = "synopsis">
  {% for review in reviews %}
{% if review.id != ''')
f.write(os.sys.argv[1]+''' %}
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
<h1> Latest Features </h1>
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
