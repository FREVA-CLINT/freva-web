from django.urls import re_path as url

import base.views

urlpatterns = [
    url(r"^$", base.views.home, name="home"),
    url(r"^logout", base.views.logout, name="logout"),
    url(r"^edit_account", base.views.edit_account, name="edit_account"),
    url(r"^wiki", base.views.wiki, name="wiki"),
    url(r"^contact", base.views.contact, name="contact"),
    url(r"^restart", base.views.restart, name="restart"),
    url(r"^freva.cs", base.views.dynamic_css, name="dynamic_css"),
    # url(r'^shell-in-a-box', 'shell_in_a_box', name='shell_in_a_box'),

]
