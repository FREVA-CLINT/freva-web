"""
Created on 14.11.2013

@author: Sebastian Illing

urlconf for the solr application
"""

from django.conf.urls import url, patterns


urlpatterns = patterns('solr.views',
    url(r'^solr-search/$', 'solr_search', name='solr_search'),
    url(r'^data-browser/$', 'data_browser', name='data_browser'),  
    url(r'^ncdump/$', 'ncdump', name='ncdump'),

    # react views
    url(r'^data-browser-new/$', 'databrowser', name='databrowser'),
)
