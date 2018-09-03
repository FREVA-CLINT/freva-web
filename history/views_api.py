import ast
import os
import re
import json

from collections import Counter, OrderedDict
from os.path import splitext

from history.models import History, Result, ResultTag
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
        return {'%s__%s' % (self.filter_field, self.filter_method,): value}

    def generate_filter(self, queryset, request):

        params = request.query_params
        if hasattr(self, 'predefined_filter'):
            queryset = queryset.filter(**self.get_filter_field(self.predefined_filter))
        if hasattr(self, 'exclude'):
            queryset = queryset.exclude(**self.get_filter_field(self.exclude))
    
        for fac in params.keys():
            if not hasattr(self, 'allowed_facets') or fac in self.allowed_facets:
                #queryset = queryset.filter(**self.get_filter_field(params[fac]))

                queryset = queryset.filter(history_id__parameter_id__parameter_name=fac,
                                                  history_id__value__icontains=' '+params[fac]+' ')

        return queryset


class ResultFacets(APIView, FilterAbstract):
    filter_field = 'configuration'
    filter_method = 'icontains'
    allowed_facets = settings.RESULT_BROWSER_FACETS
    #predefined_filter = '"ESMValTool namelists"'
    #exclude = 'CMIP6'

    def get(self, request, format=None):
        queryset = History.objects.filter(tool='EVC',status=0,flag=0)
        queryset = self.generate_filter(queryset, request)

        facets = settings.RESULT_BROWSER_FACETS

        structure = OrderedDict()

        queryset = queryset.values_list('configuration', flat=True)
        items_dic = [json.loads(item) for item in queryset]

        structure_temp = {}
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

        return Response({'data': structure, 'metadata': None})


class ResultFiles(APIView, FilterAbstract):
    filter_field = 'configuration'
    filter_method = 'icontains'
    allowed_facets = settings.RESULT_BROWSER_FACETS
    #predefined_filter = '"ESMValTool namelists"'
    exclude = 'CMIP6'

    def get(self, request, format=None):
        queryset = History.objects.filter(tool='EVC')
        queryset = self.generate_filter(queryset, request)

        configuration = queryset.values_list('id', 'timestamp', 'configuration')
        data = []
        for item in configuration:
            data.append(
                {
                    'ID': item[0],
                    'Timestamp': item[1],
                    'namelist': splitext(json.loads(item[2])['ESMValTool namelists'][0])[0],
                    'link2results': reverse('history:results', args=[item[0]])
                }
            )

        return Response({'data': data, 'metadata': {'start': 0, 'numFound': len(data)}})

class ResultPictures(APIView, FilterAbstract):
    filter_field = 'configuration'
    filter_method = 'icontains'
    allowed_facets = settings.RESULT_BROWSER_FACETS
    #predefined_filter = '"ESMValTool namelists"'
    #exclude = 'CMIP6'

    def prepare_query(self,request):
        queryset = History.objects.filter(tool='EVC',status=0,flag=0)
        queryset = self.generate_filter(queryset, request)

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
        result = cache.get(request.get_full_path())
        if not result:
            result = self.prepare_query(request)
            cache.set(request.get_full_path(),result,43200)
        return Response(result)

class ResultFacetsCMIP6(APIView, FilterAbstract):
    filter_field = 'configuration'
    filter_method = 'icontains'
    allowed_facets = settings.RESULT_BROWSER_FACETS
    predefined_filter = '"Product": " CMIP6'
    #exclude = 'CMIP6'

    def get(self, request, format=None):
        queryset = History.objects.filter(tool='EVC',status=0,flag=0)
        queryset = self.generate_filter(queryset, request)

        facets = settings.RESULT_BROWSER_FACETS

        structure = OrderedDict()

        queryset = queryset.values_list('configuration', flat=True)
        items_dic = [json.loads(item) for item in queryset]

        structure_temp = {}
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

        return Response({'data': structure, 'metadata': None})

class ResultPicturesCMIP6(APIView, FilterAbstract):
    filter_field = 'configuration'
    filter_method = 'icontains'
    allowed_facets = settings.RESULT_BROWSER_FACETS
    predefined_filter = '"Product": " CMIP6'


    def prepare_query(self,request):
        queryset = History.objects.filter(tool='EVC',status=0,flag=0)
        queryset = self.generate_filter(queryset, request)

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
        result = cache.get(request.get_full_path())
        if not result:
            result = self.prepare_query(request)
            cache.set(request.get_full_path(),result,43200)
        return Response(result)
