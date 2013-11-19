"""
Created on 14.11.2013

@author: Sebastian Illing

urlconf for the solr application
"""

from django.conf.urls import url, patterns


urlpatterns = patterns('solr.views',
    url(r'^solr-search/$', 'solr_search', name='solr_search'),  
)