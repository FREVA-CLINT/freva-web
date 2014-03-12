from django.conf.urls import url, patterns

urlpatterns = patterns('history.views',
    url(r'^$', 'history', name='history'),
    url(r'^$', 'history2', name='history2'),
    url(r'^(?P<id>\w+)/results/$', 'results', name='results'),
    url(r'^(?P<id>\w+)/jobinfo/$', 'jobinfo', name='jobinfo'),
    url(r'^(?P<id>\w+)/tail-file/$', 'tailFile', name='tailFile'),
    url(r'^cancel-slurmjob/$', 'cancelSlurmjob', name='cancelSlurmjob')
)
