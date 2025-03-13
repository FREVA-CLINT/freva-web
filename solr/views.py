"""
Created on 14.11.2013

@author: Sebastian Illing

views for the solr application
"""

import logging
from typing import Union

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, QueryDict
from django.shortcuts import render


@login_required()
def databrowser(request):
    """
    New view for plugin list
    TODO: As we use react now, we should use ONE default view for all react pages
    """
    return render(request, "plugins/list.html", {"title": "Databrowser"})


def search_overview(request):
    return reverse_proxy(
        request, f"{settings.DATA_BROWSER_HOST}/api/freva-nextgen/databrowser/overview"
    )


def extended_search(request, flavour, unique_key):
    return reverse_proxy(
        request,
        f"{settings.DATA_BROWSER_HOST}/api/freva-nextgen/databrowser/extended-search/{flavour}/{unique_key}",
    )


def data_search(request, flavour, unique_key):
    return reverse_proxy(
        request,
        f"{settings.DATA_BROWSER_HOST}/api/freva-nextgen/databrowser/data-search/{flavour}/{unique_key}",
    )


def metadata_search(request, flavour, unique_key):
    return reverse_proxy(
        request,
        f"{settings.DATA_BROWSER_HOST}/api/freva-nextgen/databrowser/metadata-search/{flavour}/{unique_key}",
    )


def intake_catalogue(request, flavour, unique_key):
    return reverse_proxy(
        request,
        f"{settings.DATA_BROWSER_HOST}/api/freva-nextgen/databrowser/intake-catalogue/{flavour}/{unique_key}",
    )

def stac_catalogue(request, flavour, unique_key):
    return reverse_proxy(
        request,
        f"{settings.DATA_BROWSER_HOST}/api/freva-nextgen/databrowser/stac-catalogue/{flavour}/{unique_key}",
    )

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
            timeout=100,
        )
        return JsonResponse(response.json(), status=response.status_code)
    except requests.RequestException as e:
        logging.error(e)
        return JsonResponse({"error": str(e)}, status=500)
