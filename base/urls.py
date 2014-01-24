"""urlconf for the base application"""

from django.conf.urls import url, patterns


urlpatterns = patterns('base.views',
    url(r'^$', 'home', name='home'),
    url(r'^logout', 'logout', name='logout'),
    url(r'^wiki', 'wiki', name='wiki'),
    url(r'^contact', 'contact', name='contact'),
    url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/favicon.ico'}),

)
