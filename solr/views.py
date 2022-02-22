"""
Created on 14.11.2013

@author: Sebastian Illing

views for the solr application
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.views.decorators.debug import sensitive_post_parameters

from evaluation_system.model.solr import SolrFindFiles
from django.conf import settings
from paramiko import AuthenticationException

from plugins.utils import ssh_call, get_scheduler_hosts
import json
import logging


@login_required()
def databrowser(request):
    """
    New view for plugin list
    TODO: As we use react now, we should use ONE default view for all react pages
    """
    return render(request, "plugins/list.html", {"title": "Databrowser"})


@login_required()
def solr_search(request):
    args = dict(request.GET)
    latest = True
    try:
        facets = request.GET["facet"]
    except KeyError:
        facets = False

    # get page and strange "_" argument
    try:
        page_limit = args.pop("page_limit")
        _token = args.pop("_")
    except KeyError:
        page_limit = 10

    if not request.user.has_perm("history.browse_full_data"):
        restrictions = settings.SOLR_RESTRICTIONS
        arg_keys = list(args.keys())
        for k in arg_keys:
            if k in restrictions:
                args[k] = list(set(args[k]).intersection(set(restrictions[k])))
                if not args[k]:
                    args.pop(k)

        tmp = restrictions.copy()
        tmp.update(args)
        args = tmp

    if "start" in args:
        args["start"] = int(request.GET["start"])
    if "rows" in args:
        args["rows"] = int(request.GET["rows"])

    metadata = None

    def remove_year(d):
        tmp = []
        for i, val in enumerate(d):
            try:
                if i % 2 == 0:
                    try:
                        int(val[-6:])
                        tmp_val = val[:-6]
                    except:
                        int(val[-4:])
                        tmp_val = val[:-4]
                    if tmp_val not in tmp:
                        tmp.append(tmp_val)
                        tmp.append(d[i + 1])
            except:
                tmp.append(val)
                tmp.append(d[i + 1])
        return tmp

    def reorder_results(res):
        import collections

        cmor = [
            "project",
            "product",
            "institute",
            "model",
            "experiment",
            "time_frequency",
            "realm",
            "variable",
            "ensemble",
            "data_type",
        ]
        results = collections.OrderedDict()
        for cm in cmor:
            try:
                results[cm] = res.pop(cm)
            except KeyError:
                pass
        for k, v in res.items():
            results[k] = v
        return results

    if facets:
        args["facet.limit"] = -1
        logging.debug(args)
        args.pop("facet")
        if facets == "*":
            # means select all,
            facets = None

        if facets == "experiment_prefix":
            args["experiment"] = args.pop("experiment_prefix")
            results = SolrFindFiles.facets(facets="experiment", **args)
            results["experiment_prefix"] = remove_year(results.pop("experiment"))
        else:
            if "experiment_prefix" in args:
                args["experiment"] = args.pop("experiment_prefix")[0] + "*"
            print("args nochmal", args)
            results = SolrFindFiles.facets(facets=facets, **args)
            print("results", results)
            results = reorder_results(results)
    else:
        results = SolrFindFiles.search(_retrieve_metadata=True, **args)
        metadata = next(results)
        results = list(results)

    return HttpResponse(
        json.dumps(dict(data=results, metadata=metadata)),
        content_type="application/json",
    )
