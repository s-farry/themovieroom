import imp
import os
import sys


sys.path.insert(0, os.path.dirname(__file__))

wsgi = imp.load_source('wsgi', 'themovieroom/wsgi.py')
application = wsgi.application


#a2 specific problem
# https://stackoverflow.com/questions/49594955/django-1-11-on-passenger-wsgi-not-routing-post-request

# Set this to your root
SCRIPT_NAME = ''

class PassengerPathInfoFix(object):
    """
    Sets PATH_INFO from REQUEST_URI since Passenger doesn't provide it.
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        from urlparse import unquote
        environ['SCRIPT_NAME'] = SCRIPT_NAME

        request_uri = unquote(environ['REQUEST_URI'])
        script_name = unquote(environ.get('SCRIPT_NAME', ''))
        offset = request_uri.startswith(script_name) and len(environ['SCRIPT_NAME']) or 0
        environ['PATH_INFO'] = request_uri[offset:].split('?', 1)[0]
        return self.app(environ, start_response)


#application = get_wsgi_application()
application = PassengerPathInfoFix(application)
