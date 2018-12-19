import ast
import os
import re
import json

from collections import Counter, OrderedDict
from os.path import splitext
from copy import copy

import json
import re
import time

from collections import Counter, OrderedDict
from operator import itemgetter
from datetime import datetime


from history.models import History, Result, ResultTag
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.cache import cache


class FilterAbstract(object):
    @property
    def filter_field(self):
        raise NotImplementedError, 'filter_field must be implemented'

    @property
    def filter_method(self):
        raise NotImplementedError, 'filter_method must be implemented'

    def set_request(self,request):        
        request.GET._mutable = True
        if hasattr(settings,'CMIP6_PATH') and settings.CMIP6_PATH:
            request.GET['product'] = 'cmip6' if settings.CMIP6_PATH in request.META['HTTP_REFERER'] else 'cmip5'
        request.GET._mutable = False
        return request

    def get_filter_field(self, value):
        print {'%s__%s' % (self.filter_field, self.filter_method,): value}
        return {'%s__%s' % (self.filter_field, self.filter_method,): value}


    def generate_filter(self, queryset, params):
        self.allowed_facets += ['product'] if hasattr(settings,'CMIP6_PATH') and settings.CMIP6_PATH else []
        #params = request.query_params
        
        if hasattr(self, 'predefined_filter'):
            queryset = queryset.filter(**self.get_filter_field(self.predefined_filter))
    
        for fac in params.keys():

            if not hasattr(self, 'allowed_facets') or fac in self.allowed_facets:
                #queryset = queryset.filter(**self.get_filter_field(params[fac]))

                queryset = queryset.filter(history_id__parameter_id__parameter_name=fac,
                                                  history_id__value__icontains=' '+params[fac]+' ')

        self.allowed_facets.remove('product') if hasattr(settings,'CMIP6_PATH') and settings.CMIP6_PATH else None


        return queryset


class ResultFacets(APIView, FilterAbstract):
    allowed_facets = settings.RESULT_BROWSER_FACETS
    evc = getattr(settings,'EVC',None)
    filter_method = 'iregex'
    filter_field = 'configuration'

    if evc : filter_method = 'icontains'

    def prepare_facets(self, request, format=None):
        structure = OrderedDict()
        structure_temp = {}
        
        if self.evc:
            request = self.set_request(request)
            queryset = History.objects.filter(tool='EVC',status=0,flag=0)
            params = request.query_params
            queryset = self.generate_filter(queryset, params)
            facets = settings.RESULT_BROWSER_FACETS
            queryset = queryset.values_list('configuration', flat=True)

            items_dic = [json.loads(item) for item in queryset]

            # create a dictionary - tags: list of attributes
            # counts tags: total number of attributes
            for fac in facets:
                structure[fac] = []
                structure_temp[fac] = []
                for item in items_dic:
                    if fac in item:
                        itemList = item[fac]
                        itemList = itemList.split(',')
                        itemList = [item.lstrip().rstrip() for item in itemList]
                        structure_temp[fac].extend(itemList)
                for key, num in OrderedDict(sorted(Counter(structure_temp[fac]).items())).iteritems():
                    structure[fac].append(key)
                    structure[fac].append(num)
        else:
            queryset = History.objects.all()
            queryset = queryset.filter(flag__lt=3, status__lt=2)
            params = request.query_params
            modRequest = {}
            for key, value in params.iteritems():
                if key == 'plugin':
                    queryset = queryset.filter(tool=value)
                else:
                    value = value.replace('\\', '\\\\\\\\')
                    value = value.replace('*', '\*')
                    value = value.replace('.', '\.')
                    value = value.replace('[', '\[')
                    value = value.replace(']', '\]')
                    if value == '\*' or value == '\\\\\\\\\*':
                        value = '(\*|\\\\\\\\\*)'
                    modRequest[key] = r'"%s([0-9]{0,1})": "%s"' % (key, value)
            queryset = self.generate_filter(queryset, modRequest)
            queryset = queryset.values_list('id', 'tool', 'configuration')
            items_dic = []
            for id, tool, item in queryset:
                newItem = json.loads(item)
                if len(set(newItem.keys()) & set(self.allowed_facets)) == 0: continue
                newItem.update({'plugin': tool})
                items_dic.append(newItem)
            

            # create a dictionary - tags: list of attributes
            # counts tags: total number of attributes
            for fac in self.allowed_facets:
                structure[fac] = []
                structure_temp[fac] = []
                for item in items_dic:
                    regex = re.compile(r'"(%s)([0-9]{0,1})":' % fac)
                    matches = regex.findall(json.dumps(item))
                    matchlist = []
                    for match in matches:
                        matchJoin = ''.join(match)
                        if item[matchJoin] is None: continue
                        value = item[matchJoin].lower()
                        if value not in matchlist:
                            value = item[matchJoin].lower()
                            if value == '\*': value = '*'
                            structure_temp[fac].extend([value, ])
                            matchlist.append(value)
                        else:
                            continue
                for key, num in OrderedDict(sorted(Counter(structure_temp[fac]).items())).iteritems():
                    structure[fac].append(key)
                    structure[fac].append(num)
        return {'data': structure, 'metadata': None}


    def get(self, request, format=None):
        result = cache.get(request.get_full_path())
        if not result:
            result = self.prepare_facets(request)
            cache.set(request.get_full_path(), result, None)

        return Response(result)
        



class ResultFiles(APIView, FilterAbstract):
    filter_field = 'configuration'
    filter_method = 'iregex'
    allowed_facets = settings.RESULT_BROWSER_FACETS
    evc = getattr(settings,'EVC',None)
    
    def get_data(self, configuration):
        data = []
        for item in configuration:
            new_item = json.loads(item['configuration'])
            if len(set(new_item.keys()) & set(self.allowed_facets)) == 0: continue
            data.append(
                {
                    'id': item['id'],
                    'tool': item['tool'],
                    'configuration': item['configuration'],
                    'uid': item['uid'],
                    'timestamp': item['timestamp'].isoformat(),
                    'link2results': reverse('history:results', args=[item['id']]),
                    'caption': item['caption']
                }
            )

        return data

    def get(self, request, format=None):
        """
            - get all History entries(configurations) and looks in configurations for a given searchText
            - due to performance reason: use regular expressions to find the given SearchText
            - cache the output - depends on the url
            - append new entries on existing cache
            - apply offset, sortName, sortOrder and searchText on cache results
        """
        queryset = History.objects.all().order_by('-timestamp')
        full_path = request.get_full_path()
        params = request.query_params

        # filter- caching without options
        options = ['limit', 'offset', 'sortName', 'sortOrder', 'searchText']
        queries = {}
        for item in options:
            queries[item] = params[item]
            full_path = re.sub(r'&%s=(\d+|\w+)' % item, '', full_path)

        # new entries in database?
        max_id = queryset.filter(flag__lt=3, status__lt=2).order_by('id').last().id
        cache_max_id = cache.get('{}_{}'.format(full_path, max_id), 0)

        # regex are tricky - some replacements
        mod_request = {}
        for key, value in params.iteritems():
            if key == 'plugin':
                queryset = queryset.filter(tool=value)
            else:
                value = value.replace('\\', '\\\\\\\\')
                value = value.replace('*', '\*')
                value = value.replace('.', '\.')
                value = value.replace('[', '\[')
                value = value.replace(']', '\]')
                if value == '\*' or value == '\\\\\\\\\*':
                    value = '(\*|\\\\\\\\\*)'
                mod_request[key] = r'"%s([0-9]{0,1})": "%s"' % (key, value)

        # append new entries
        data = cache.get(full_path, list())
        if max_id > cache_max_id or not data:
            cache.set('{}_{}'.format(full_path, max_id), max_id, None)
            queryset = queryset.filter(flag__lt=3, status__lt=2, id__gt=cache_max_id)
            queryset = self.generate_filter(queryset, mod_request)
            configuration = queryset.values('id', 'tool', 'configuration', 'uid', 'timestamp', 'caption')
            data.extend(self.get_data(configuration))
            cache.set(full_path, data, None)

        # looking for searchText in configurations
        if len(queries['searchText']) > 0:
            # pattern = r'{.*?zykpak.*?\d+}' # alternative for re.findall - see below
            pattern = re.compile(r'{.*?%s.*?"id": \d+}' % queries['searchText'])
            # for findall we need a fake entry
            json_data = json.dumps(data)[:-1]+', {"fake" : "%s", "id": 0}' % queries['searchText']+']'
            first_findall = pattern.findall(json_data)
            data = [json.loads(re.findall(r'{.*?"id": \d+}', regex).pop()) for regex in first_findall]
            # remove fake entry
            data.pop()


        # sort entries
        reverse_order = False
        if queries['sortOrder'] == 'desc': reverse_order = True
        data = sorted(data, key=itemgetter(queries['sortName']), reverse=reverse_order)
        result = {'data': data[int(queries['offset']):int(queries['offset']) + int(queries['limit'])],
                  'metadata': {'start': 0, 'numFound': len(data)}}
        return Response(result)

class ResultPictures(APIView, FilterAbstract):
        filter_field = 'configuration'
        filter_method = 'icontains'
        allowed_facets = settings.RESULT_BROWSER_FACETS
        #predefined_filter = '"ESMValTool namelists"'
        #exclude = 'CMIP6'
        evc = getattr(settings,'EVC',None)
        
        def prepare_query(self,request):
            queryset = History.objects.filter(tool='EVC',status=0,flag=0)
            params = request.query_params
            queryset = self.generate_filter(queryset, params)
            rids = queryset.values_list('id', flat=True)
            rids = list(rids)
            result_object = Result.objects.filter(history_id__in=rids).prefetch_related('resulttag_set')

            pictures = []
            result = {}
            for r in result_object:
                rID = r.history_id.id
                caption = r.resulttag_set.all()[0].text
                pictures.append(
                    {
                        'preview_file': os.path.join(settings.PREVIEW_URL, r.preview_file),
                        'caption': caption if caption else None,
                        'link2results': reverse('history:results', args=[rID])
                    }
                )
            result['data'] = pictures
            result.update({'metadata': {'numFound': len(pictures)}})
            return result

        def get(self, request, format=None):
            request = self.set_request(request)
            request_json =  json.dumps(OrderedDict(sorted(request.GET.items(), key = lambda t: t[0])))
            result = cache.get(request_json)
            if not result:
                result = self.prepare_query(request)
                cache.set(request_json,result,43200)
            return Response(result)
