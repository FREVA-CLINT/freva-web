import os

from django.urls import path, re_path

from .proxyviews import ChatBotProxy
from .views import chatbot

urlpatterns = [
    re_path(r"^chatbot/$", chatbot, name="chatbot"),
]

if int(os.environ.get("DEV_MODE", "0")) == 1:
    urlpatterns.append(
        path(
            r"api/chatbot/<path:url>/",
            ChatBotProxy.as_view(),
            name="chatbot_proxy",
        )
    )
