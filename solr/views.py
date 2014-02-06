"""
Created on 14.11.2013

@author: Sebastian Illing

views for the solr application
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from evaluation_system.model.solr import SolrFindFiles

import json
import logging

@login_required()
def data_browser(request):
    args = {'facet.limit':-1}
    facets = SolrFindFiles.facets(facets=None,**args)        
    logging.debug(facets)
    return render(request, 'solr/data_browser.html', {'facets':facets})


@login_required()
def solr_search(request):
    args = dict(request.GET)#self.request.arguments.copy()
    latest = True#bool(request.GET.get('latest', [False]))
    try:
        facets = request.GET['facet']
    except KeyError:
        facets = False
    
    #get page and strange "_" argument
    try:
        page_limit = args.pop('page_limit')
        _token = args.pop('_')
    except KeyError:
        page_limit = 10

    if 'start' in args: args['start'] = int(request.GET['start']) 
    if 'rows' in args: args['rows'] = int(request.GET['rows'])
    
    metadata = None
   
    def removeYear(d):
	tmp = [] 
	for i,val in enumerate(d):
		try:
			if i%2 == 0:	
				int(val[-4:])
				tmp_val = val[:-4]
				if tmp_val not in tmp:
					tmp.append(tmp_val)
					tmp.append(d[i+1])
		except:
			tmp.append(val)
			tmp.append(d[i+1])
	return tmp
		
 
    #return HttpResponse(json.dumps({"data": {"product": ["baseline0", 10, "baseline1", 10, "output", 1129, "output1", 1834]}, "metadata": None}))
    if facets:
	args['facet.limit']=-1
	logging.debug(args)
	#return HttpResponse(json.dumps(args))
        args.pop('facet')
        if facets == '*':
            #means select all, 
            facets = None
        if facets == 'experiment_prefix':
		args['experiment'] = args.pop('experiment_prefix')
	  	results = SolrFindFiles.facets(facets='experiment', **args)
		results['experiment_prefix'] = removeYear(results.pop('experiment'))
		#results = {"experiment_prefix": ["baseline0", 10, "baseline1", 10, "output", 1129, "output1", 1834]}
	else:
		if 'experiment_prefix' in args: args['experiment'] = args.pop('experiment_prefix')[0]+'*'
		results = SolrFindFiles.facets(facets=facets, **args)
    else:
        #return HttpResponse(json.dumps(dict(hallo='was')))
        results = SolrFindFiles.search( _retrieve_metadata = True, **args)
        metadata = results.next()
        results = list(results)
      
    return HttpResponse(json.dumps(dict(data=results, metadata=metadata)), content_type="application/json")
