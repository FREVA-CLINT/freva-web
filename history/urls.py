from django.conf.urls import url, patterns
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from history import views


urlpatterns = [
    url(r'^$', never_cache(login_required(views.HistoryTable.as_view())), name='history'),
    url(r'^(?P<id>\w+)/results/$', views.results, name='results'),
    url(r'^(?P<history_id>\w+)/comments/$', views.result_comments, name='result-comments'),
    url(r'^(?P<history_id>\w+)/follow/$', views.follow_result, name='follow'),
    url(r'^(?P<history_id>\w+)/unfollow/$', views.unfollow_result, name='unfollow'),
    url(r'^(?P<uid>[\w+.]+)/show/$', never_cache(login_required(views.HistoryTable.as_view())), name='history'),
    url(r'^(?P<id>[\w.]+)/jobinfo/$', views.jobinfo, name='jobinfo'),
    url(r'^(?P<id>\w+)/tail-file/$', views.tail_file, name='tailFile'),
    url(r'^change-flag/$', views.change_flag, name='changeFlag'),
    url(r'^cancel-slurmjob/$', views.cancel_slurmjob, name='cancelSlurmjob'),
    url(r'^(?P<id>\w+)/(?P<type>\w+)/generate-caption/$', views.generate_caption, name='generate-caption'),
    url(r'^(?P<history_id>\w+)/(?P<deleted>\w+)/count-notes/$', views.count_notes, name='count-notes'),
    url(r'^(?P<history_id>\w+)/(?P<tag_id>\w+)/edit-historytag/$', views.edit_htag, name='edit-historytag'),
    url(r'^sendmail/$', views.send_share_email, name='sendMail'),
    url(r'^mail-to-developer/$', views.send_mail_to_developer, name='mail_to_developer'),
]
