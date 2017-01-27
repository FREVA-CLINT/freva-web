from django.conf.urls import url, patterns
from views_api import PluginsList, ExportPlugin

urlpatterns = patterns(
    'plugins.views',
    url(r'^$', 'home', name='home'),
    url(r'^list/$', 'plugin_list', name='plugin_list'),
    url(r'^about/$', 'list_docu', name='about'),
    url(r'^browse-files/$', 'dirlist', name='dirlist'),
    url(r'^browse-files-new/$', 'list_dir', name='list_dir'),
    url(r'^(?P<plugin_name>\w+)/detail/$', 'detail', name='detail'),
    url(r'^(?P<plugin_name>\w+)/setup/$', 'setup', name='setup'),
    url(r'^(?P<plugin_name>\w+)/(?P<row_id>\d+)/setup/$', 'setup', name='setup'),
    url(r'^(?P<plugin_name>\w+)/similar-results/$', 'search_similar_results', name='similar'),
    url(r'^(?P<history_id>\d+)/similar-results-by-id/$', 'search_similar_results', name='similar'),
    url(r'^export-plugin/$', 'export_plugin', name='export_plugin'),

    # API views
    url(r'^api/plugin-list/$', PluginsList.as_view(), name='api-plugin-list'),
    url(r'^api/export-plugin/$', ExportPlugin.as_view(), name='api-export-plugin'),
)
