from django.contrib.auth.decorators import login_required
from django.urls import re_path as url
from django.views.decorators.cache import never_cache

from history import views
from plugins.views_api import ShareResultsByMail

urlpatterns = [
    url(
        r"^$", never_cache(login_required(views.HistoryTable.as_view())), name="history"
    ),
    url(r"^(?P<id>\w+)/results/$", views.results, name="results"),
    url(
        r"^(?P<history_id>\w+)/comments/$",
        views.result_comments,
        name="result-comments",
    ),
    url(r"^(?P<history_id>\w+)/follow/$", views.follow_result, name="follow"),
    url(r"^(?P<history_id>\w+)/unfollow/$", views.unfollow_result, name="unfollow"),
    url(
        r"^(?P<uid>[^/]+)/show/$",
        never_cache(login_required(views.HistoryTable.as_view())),
        name="history",
    ),
    url(r"^(?P<id>[\w.]+)/jobinfo/$", views.jobinfo, name="jobinfo"),
    url(r"^(?P<id>\w+)/tail-file/$", views.tail_file, name="tailFile"),
    url(r"^change-flag/$", views.change_flag, name="changeFlag"),
    url(r"^cancel-slurmjob/$", views.cancel_slurmjob, name="cancelSlurmjob"),
    url(
        r"^(?P<id>\w+)/set-caption/$",
        views.set_caption,
        name="set-caption",
    ),
    url(
        r"^(?P<history_id>\w+)/(?P<deleted>\w+)/count-notes/$",
        views.count_notes,
        name="count-notes",
    ),
    url(
        r"^(?P<history_id>\w+)/(?P<tag_id>\w+)/edit-historytag/$",
        views.edit_htag,
        name="edit-historytag",
    ),
    url(r"^sendmail/$", ShareResultsByMail.as_view(), name="share_results"),
    url(r"^result-browser/$", views.result_browser, name="result_browser"),
]
