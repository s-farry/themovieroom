import django, os
os.environ["DJANGO_SETTINGS_MODULE"] = "themovieroom.settings"
django.setup()

from films.models import films, reviews

if len(os.sys.argv) != 2:
    print 'Only one argument is required:'
    print '  %s "person name"' % sys.argv[0]
    os.sys.exit(2)

fid = os.sys.argv[1]
film = films.objects.get(id = fid)
print "Adding review to ",film.title
review = reviews(films_ptr_id = film.pk)
review.__dict__.update(film.__dict__)
review.id=None
review.text="Insert Review Here"
review.rating = 1
review.save()
