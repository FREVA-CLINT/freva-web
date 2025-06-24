from django.urls import re_path as url

import base.views

from .views_api import proxy_auth_view

urlpatterns = [
    url(r"^$", base.views.home, name="home"),
    url(r"^login/$", base.views.OIDCLoginView.as_view(), name="oidc_login"),
    url(r"^callback$", base.views.OIDCCallbackView.as_view(), name="oidc_callback"),
    url(r"^logout$", base.views.logout_view, name="logout"),
    url(r"^refresh-token/$", base.views.manual_refresh_token, name="get_refresh_token"),
    url(r"^get-current-token/$", base.views.collect_current_token, name="collect_current_token"),
    url(r"^wiki$", base.views.wiki, name="wiki"),
    url(r"^contact$", base.views.contact, name="contact"),
    url(r"^restart$", base.views.restart, name="restart"),
    url(r"^freva.cs", base.views.dynamic_css, name="dynamic_css"),
    url(r"^api/freva-nextgen/auth/(?P<path>.*)$", proxy_auth_view, name="auth_proxy"),

    # url(r'^shell-in-a-box', 'shell_in_a_box', name='shell_in_a_box'),
]
