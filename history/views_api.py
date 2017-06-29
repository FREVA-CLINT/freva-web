import ast
from collections import Counter
from os.path import splitext

from history.models import History, Result
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.core.urlresolvers import reverse


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

        for fac in params.keys():
            if not hasattr(self, 'allowed_facets') or fac in self.allowed_facets:
                queryset = queryset.filter(**self.get_filter_field(params[fac]))

        return queryset


class ResultFacets(APIView, FilterAbstract):
    filter_field = 'configuration'
    filter_method = 'icontains'
    allowed_facets = settings.RESULT_BROWSER_FACETS
    predefined_filter = '"THEME"'

    def get(self, request, format=None):

        queryset = History.objects.all()
        queryset = self.generate_filter(queryset, request)

        facets = settings.RESULT_BROWSER_FACETS

        structure = {}

        queryset = queryset.values_list('configuration', flat=True)
        items_dic = [ast.literal_eval(item) for item in queryset]

        structure_temp = {}
        for fac in facets:
            structure[fac] = []
            structure_temp[fac] = []
            for item in items_dic:
                if fac in item:
                    structure_temp[fac].extend(item[fac])
            for key, num in Counter(structure_temp[fac]).items():
                structure[fac].append(key)
                structure[fac].append(num)

        data = {'data': structure, 'metadata': None}

        return Response(data)


class ResultFiles(APIView, FilterAbstract):
    filter_field = 'configuration'
    filter_method = 'icontains'
    allowed_facets = settings.RESULT_BROWSER_FACETS
    predefined_filter = '"THEME"'

    def get(self, request, format=None):
        queryset = History.objects.all()
        queryset = self.generate_filter(queryset, request)

        configuration = queryset.values_list('id', 'timestamp', 'configuration')
        data = []
        for item in configuration:
            data.append(
                {
                    'ID': item[0],
                    'Timestamp': item[1],
                    'namelist': splitext(ast.literal_eval(item[2])['namelist'][0])[0],
                    'link2results': reverse('history:results', args=[item[0]])
                }
            )

        data = {'data': data, 'metadata': {'start': 0, 'numFound': len(data)}}
        return Response(data)
