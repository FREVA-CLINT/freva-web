import logging
from typing import Union

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, QueryDict
from django.shortcuts import render


@login_required()
def chatbot(request):
    """
    New view for plugin list
    TODO: As we use react now, we should use ONE default view for all react pages
    """
    return render(request, "plugins/list.html", {"title": "Chat Bot"})


def ping(request):
    print(f"{settings.CHAT_BOT_URL}/api/chatbot/ping")
    return reverse_proxy(request, f"{settings.CHAT_BOT_URL}/api/chatbot/ping")


def get_all_parameters(query_string):
    query_dict = QueryDict(query_string)
    parameters = {}

    for key in query_dict.keys():
        values = query_dict.getlist(key)
        parameters[key] = values

    return parameters


def reverse_proxy(request, path):
    api_url = path
    query_string = request.META["QUERY_STRING"]
    all_parameters = get_all_parameters(query_string)
    try:
        response = requests.request(
            method="GET",
            url=api_url,
            params=all_parameters,
            stream=True,  # Enable streaming
            timeout=100,
        )
        return response.content
    except requests.RequestException as e:
        logging.error(e)
        return JsonResponse({"error": str(e)}, status=500)
