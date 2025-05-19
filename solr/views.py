"""
Created on 14.11.2013

@author: Sebastian Illing

views for the solr application
"""

import logging
from functools import wraps

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, QueryDict, StreamingHttpResponse
from django.shortcuts import render

from django_evaluation.auth import get_auth_header, oidc_token_required

logger = logging.getLogger(__name__)


# TODO: when we have time we need to refactor here to keep it clean and unite
def conditional_oidc_required(view_func):
    """
    Decorator to conditionally apply the oidc_token_required decorator
    based on the presence of the "zarr_stream" query parameter.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.GET.get("zarr_stream") == "true":
            return oidc_token_required(view_func)(request, *args, **kwargs)
        else:
            return view_func(request, *args, **kwargs)

    return wrapper


@oidc_token_required
def load_data(request, flavour):
    """
    Proxy and stream the databrowser load endpoint,
    automatically passing through the Bearer token and query params.
    """
    api_url = (
        f"{settings.DATA_BROWSER_HOST}/api/freva-nextgen/databrowser/load/{flavour}"
    )
    params = QueryDict(request.META.get("QUERY_STRING", ""), mutable=True).dict()

    headers = get_auth_header(request)
    try:
        upstream = requests.get(
            api_url,
            params=params,
            headers=headers,
            stream=True,
            timeout=100,
            verify=False,
        )
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=503)

    if upstream.status_code != 201:
        try:
            payload = upstream.json()
        except ValueError:
            payload = upstream.text
        return JsonResponse(payload, status=upstream.status_code)
    response = StreamingHttpResponse(
        upstream.iter_content(chunk_size=8192),
        status=upstream.status_code,
        content_type="text/plain",
    )
    if request.GET.get("catalogue-type") == "intake":
        filename = f"IntakeEsmCatalogue_{flavour}_file_zarr.json"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
    return response

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


@conditional_oidc_required
def extended_search(request, flavour):
    return reverse_proxy(
        request,
        f"{settings.DATA_BROWSER_HOST}/api/freva-nextgen/databrowser/extended-search/{flavour}/file",
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


@oidc_token_required
def reverse_proxy(request, path):
    api_url = path
    query_string = request.META["QUERY_STRING"]
    all_parameters = get_all_parameters(query_string)
    headers = get_auth_header(request)

    try:
        response = requests.request(
            method="GET",
            url=api_url,
            params=all_parameters,
            headers=headers,  # Authorization header
            timeout=100,
        )
        return JsonResponse(response.json(), status=response.status_code)
    except requests.RequestException as e:
        logger.error(e)
        return JsonResponse({"error": str(e)}, status=500)
