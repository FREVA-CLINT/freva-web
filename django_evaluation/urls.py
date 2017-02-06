""" Default urlconf for django_evaluation """

from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views.generic import RedirectView
from base.views_api import UserViewSet, AuthenticatedUser
from plugins.views_api import PluginsList, ExportPlugin
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'users', UserViewSet)

admin.autodiscover()


def bad(request):
    """ Simulates a server error """
    1 / 0

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/$', admin.site.admin_view(admin.site.index)),
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^plugins/', include('plugins.urls', namespace='plugins')),
    url(r'^history/', include('history.urls', namespace='history')),
    url(r'^solr/', include('solr.urls', namespace='solr')),
    url(r'^external/', include('externaluser.urls', namespace='external')),

    url(r'^bad/$', bad),
    url(r'', include('base.urls', namespace='base')),
    
    url(r'^favicon\.ico$', RedirectView.as_view(url=settings.STATIC_URL + 'img/freva-favicon.png', permanent=True)),

    # API views
    url(r'^api/plugins/list/$', PluginsList.as_view(), name='api-plugin-list'),
    url(r'^api/plugins/export/$', ExportPlugin.as_view(), name='api-export-plugin'),
    url(r'^api/users/active/$', AuthenticatedUser.as_view(), name='api-active-user'),
    url(r'^api/', include(router.urls, namespace='api')),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

# In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
