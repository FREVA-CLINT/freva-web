from django.conf.urls import url, patterns
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from . import views


urlpatterns = [
    url(r'^$', views.hindcast_frontend, name='hindcast_frontend'),
]
