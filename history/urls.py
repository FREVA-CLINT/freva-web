from django.conf.urls import url, patterns
from django.contrib.auth.decorators import login_required
from history import views


urlpatterns = patterns('history.views',
    # url(r'^$', 'history', name='history'),
    url(r'^$', login_required(views.history_view.as_view()), name='history'),
    url(r'table$', login_required(views.history_table.as_view()), name='table'),
    url(r'^(?P<id>\w+)/results/$', 'results', name='results'),
    url(r'^(?P<uid>\w+)/show/$', login_required(views.history_view.as_view()), name='history'),
    url(r'^(?P<id>\w+)/jobinfo/$', 'jobinfo', name='jobinfo'),
    url(r'^(?P<id>\w+)/tail-file/$', 'tailFile', name='tailFile'),
    url(r'^cancel-slurmjob/$', 'cancelSlurmjob', name='cancelSlurmjob'),
    url(r'^sendmail/$', 'sendMail', name='sendMail'),
)
