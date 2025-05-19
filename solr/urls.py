"""
Created on 14.11.2013

@author: Sebastian Illing

urlconf for the solr application
"""

import os

from django.conf import settings
from django.urls import path
from django.urls import re_path as url

from .proxyviews import DataBrowserProxy
from .views import databrowser, extended_search, load_data

urlpatterns = [
    url(r"^databrowser/$", databrowser, name="data_browser"),
    path("api/freva-nextgen/databrowser/load/<str:flavour>/", load_data, name="load_data"),
    path("api/freva-nextgen/databrowser/extended-search/<str:flavour>/file/", extended_search, name="extended_search"),
]
if int(os.environ.get("DEV_MODE", "0")) == 1:
    urlpatterns.append(
        path(
            r"api/freva-nextgen/databrowser/<path:url>/",
            DataBrowserProxy.as_view(),
            name="databrowser_proxy",
        )
    )
