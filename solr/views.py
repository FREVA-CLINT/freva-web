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
def data_browser(request):
    return render(request, 'solr/data_browser_new.html')


@login_required()
def databrowser(request):
    """
    New view for plugin list
    TODO: As we use react now, we should use ONE default view for all react pages
    """
    return render(request, 'plugins/list.html', {})


@sensitive_post_parameters('pass')
@login_required()
def ncdump(request):
    fn = request.POST['file']
    user_pw = request.POST['pass']
    command = '%s -h %s' % (settings.NCDUMP_BINARY, fn,)
    
    if not request.user.has_perm('history.browse_full_data'):
        ncdump_out = 'Guest users are not allowed to use this command.<br/>Normally you would see the output of <strong>ncdump</strong> here.'
        return HttpResponse(json.dumps(dict(ncdump=mark_safe(ncdump_out),
                                            error_msg='')),
                            status=200)        
     
    try:
        result = ssh_call(request.user.username, user_pw,
                          command, get_scheduler_hosts(request.user))
        ncdump_out = result[1].readlines()
        ncdump_err = result[2].readlines()
        ncdump_out = '<pre>'+''.join(ncdump_out)+'</pre>'
        return HttpResponse(json.dumps(dict(ncdump=mark_safe(ncdump_out),
                                            error_msg=''.join(ncdump_err))),
                            status=200)
    except AuthenticationException:
        return HttpResponse('AuthenticationException', status=500,
                            content_type="application/json")


@login_required()
def solr_search(request):
    args = dict(request.GET)
    latest = True
    try:
        facets = request.GET['facet']
    except KeyError:
        facets = False
    
    # get page and strange "_" argument
    try:
        page_limit = args.pop('page_limit')
        _token = args.pop('_')
    except KeyError:
        page_limit = 10

    if not request.user.has_perm('history.browse_full_data'):
        restrictions = settings.SOLR_RESTRICTIONS

        for k in args.keys():
            if not restrictions.get(k, None) is None:
                args[k] = list(set(args[k]).intersection(set(restrictions[k])))
                if not args[k]:
                    args.pop(k)

        tmp = restrictions.copy()
        tmp.update(args)
        args = tmp

    if 'start' in args:
        args['start'] = int(request.GET['start'])
    if 'rows' in args:
        args['rows'] = int(request.GET['rows'])
    
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
                        tmp.append(d[i+1])
            except:
                tmp.append(val)
                tmp.append(d[i+1])
        return tmp

    def reorder_results(res):
        import collections
        cmor = ['project', 'product', 'institute', 'model', 'experiment', 'time_frequency', 'realm', 'variable',
                'ensemble', 'data_type']
        results = collections.OrderedDict()
        for cm in cmor:
            try:
                results[cm] = res.pop(cm)
            except KeyError:
                pass
        for k, v in res.iteritems():
            results[k] = v
        return results

    if facets:
        args['facet.limit'] = -1
        logging.debug(args)
        args.pop('facet')
        if facets == '*':
            # means select all,
            facets = None

        if facets == 'experiment_prefix':
            args['experiment'] = args.pop('experiment_prefix')
            results = SolrFindFiles.facets(facets='experiment', **args)
            results['experiment_prefix'] = remove_year(results.pop('experiment'))
        else:
            if 'experiment_prefix' in args:
                args['experiment'] = args.pop('experiment_prefix')[0]+'*'
            results = SolrFindFiles.facets(facets=facets, **args)
            results = reorder_results(results)
    else:
        results = SolrFindFiles.search(_retrieve_metadata=True, **args)
        metadata = results.next()
        results = list(results)
      
    return HttpResponse(json.dumps(dict(data=results, metadata=metadata)), content_type="application/json")
