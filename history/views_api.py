import json
import re
import time

from collections import Counter, OrderedDict
from operator import itemgetter
from datetime import datetime

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
    filter_field = 'configuration'

    def prepare_facets(self, request, format=None):
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

        structure = OrderedDict()
        start = time.time()
        queryset = queryset.values_list('id', 'tool', 'configuration')
        print 'DatenbankAbfrageFacets: %s ' % (time.time() - start)
        items_dic = []

        start = time.time()
        for id, tool, item in queryset:
            newItem = json.loads(item)
            if len(set(newItem.keys()) & set(self.facets)) == 0: continue
            newItem.update({'plugin': tool})
            items_dic.append(newItem)
        structure_temp = {}
        print 'PluginUpdate: %s' % (time.time() - start),

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
    facets = settings.RESULT_BROWSER_FACETS

    def get_data(self, configuration):
        data = []
        for item in configuration:
            new_item = json.loads(item['configuration'])
            if len(set(new_item.keys()) & set(self.facets)) == 0: continue
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
