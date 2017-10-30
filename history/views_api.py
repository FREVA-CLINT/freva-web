import ast
import json
import re
import time
from collections import Counter, OrderedDict
from os.path import splitext

from history.models import History, Result
from rest_framework.views import APIView
from rest_framework.response import Response
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

    def get_filter_field(self, value):
        print {'%s__%s' % (self.filter_field, self.filter_method,): value}
        return {'%s__%s' % (self.filter_field, self.filter_method,): value}

    def generate_filter(self, queryset, params):

        if hasattr(self, 'predefined_filter'):
            queryset = queryset.filter(**self.get_filter_field(self.predefined_filter))

        for fac in params.keys():
            if not hasattr(self, 'facets') or fac in self.facets:
                queryset = queryset.filter(**self.get_filter_field(params[fac]))


        return queryset


class ResultFacets(APIView, FilterAbstract):
    facets = settings.RESULT_BROWSER_FACETS
    filter_method = 'iregex'
    filter_field= 'configuration'

    def prepare_facets(self, request, format=None):
        queryset = History.objects.all()
        queryset = queryset.filter(flag__lt = 3, status__lt = 2)
        params = request.query_params

        modRequest = {}
        for key,value in params.iteritems():
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

        structure = OrderedDict()
        start = time.time()
        queryset = queryset.values_list('id','tool','configuration')
        print 'DatenbankAbfrageFacets: %s ' %(time.time()-start)
        items_dic = []

        start = time.time()
        for id,tool,item in queryset:
            newItem = json.loads(item)
            if len(set(newItem.keys()) & set(self.facets)) == 0: continue
            newItem.update({'plugin':tool})
            items_dic.append(newItem)
        structure_temp = {}
        print 'PluginUpdate: %s' %(time.time() - start),

        # create a dictionary - tags: list of attributes
        # counts tags: total number of attributes
        start = time.time()
        for fac in self.facets:
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
                        if value == '\*': value='*'
                        structure_temp[fac].extend([value, ])
                        matchlist.append(value)
                    else:
                        continue
            for key, num in OrderedDict(sorted(Counter(structure_temp[fac]).items())).iteritems():
                structure[fac].append(key)
                structure[fac].append(num)
        print 'ZahleFacets: %s ' %(time.time() - start)
        return {'data': structure, 'metadata': None}

    def get(self, request, format=None):
        result = cache.get(request.get_full_path())
        if not result:
            result = self.prepare_facets(request)
            cache.set(request.get_full_path(),result,None)
        return Response(result)

class ResultFiles(APIView, FilterAbstract):
    filter_field = 'configuration'
    filter_method = 'iregex'
    facets = settings.RESULT_BROWSER_FACETS


    def prepare_files(self, request, format=None):
        queryset = History.objects.all()
        queryset = queryset.filter(flag__lt=3, status__lt=2)
        params = request.query_params
        modRequest = {}
        for key,value in params.iteritems():
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

        start = time.time()
        configuration = queryset.values_list('id', 'tool','configuration' )
        print 'DatenbankAbfrageFiles: %s ' %(time.time()-start)
        data = []

        start = time.time()
        for item in configuration:
            newItem = json.loads(item[2])
            if len(set(newItem.keys()) & set(self.facets)) == 0: continue
            data.append(
                {
                    'id' : item[0],
                    'tool': item[1],
                    'link2results': reverse('history:results', args=[item[0]])
                }
            )
        caption = ('Plugin','Link')
        print 'REST-API: %s ' % (time.time() - start)
        return {'data': data, 'metadata': {'start': 0, 'numFound': len(data)},'caption':caption}

    def get(self, request, format=None):
        result = cache.get(request.get_full_path())
        if not result:
            result = self.prepare_files(request)
            cache.set(request.get_full_path(),result,None)
        return Response(result)