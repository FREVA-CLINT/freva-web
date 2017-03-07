from django.conf.urls import url, patterns, include

urlpatterns = patterns(
    'plugins.views',
    # url(r'^$', 'home', name='home'),
    # react views
    url(r'^$', 'plugin_list', name='home'),
    url(r'^(?P<plugin_name>\w+)/detail/$', 'detail', name='detail'),

    url(r'^about/$', 'list_docu', name='about'),
    url(r'^browse-files/$', 'dirlist', name='dirlist'),
    url(r'^browse-files-new/$', 'list_dir', name='list_dir'),
    url(r'^(?P<plugin_name>\w+)/setup/$', 'setup', name='setup'),
    url(r'^(?P<plugin_name>\w+)/(?P<row_id>\d+)/setup/$', 'setup', name='setup'),
    url(r'^(?P<plugin_name>\w+)/similar-results/$', 'search_similar_results', name='similar'),
    url(r'^(?P<history_id>\d+)/similar-results-by-id/$', 'search_similar_results', name='similar'),
    url(r'^export-plugin/$', 'export_plugin', name='export_plugin'),
)

