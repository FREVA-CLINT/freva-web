from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
#from scipy.io import netcdf
#from netCDF4 import Dataset
import numpy as np
from django.core.cache import cache
from .models import HindcastEvaluation
from django.db import IntegrityError
import re
from operator import itemgetter


display_names = {
    'pr': 'Precipitation (pr)',
    'tas': 'Temperature (tas)',
    'psl': 'Sea Level Pressure (psl)',
    'hc700total': 'Total Heat Content (hc700total)',

    'msss': 'MSESS',
    'correlation': 'Correlation',


    'b1-lr': 'Baseline1-LR',
    'b1-mr': 'Baseline1-MR',
    'preop-lr': 'Preop-LR',
    'preop-hr': 'Preop-HR',
    'unini': 'Uninitialized',
    'pr-gecco': 'Prototype-Gecco',
    'pr-ora': 'Prototype-OraS4',

    'vs_b1-lr': 'Baseline1-LR',
    'vs_b1-mr': 'Baseline1-MR',
    'vs_preop-lr': 'Preop-LR',
    'vs_preop-hr': 'Preop-HR',
    'vs_unini': 'Uninitialized',
    'vs_b0': 'Baseline0',
    'vs_clim': 'Climatology',
    'vs_pr-gecco': 'Prototype-Gecco',
    'vs_pr-ora': 'Prototype-OraS4',

    '-180_180_-90_90': 'Global',
    '-60_-10_50_65': 'North Atlantic',
    '-170_-120_-5_5': 'Nino3.4',
}


def convert(name):
    if name == 'metric':
        return 'score'
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


@api_view(['GET'])
def register_hindcast(request):
    path_structure = 'hindcast_set/reference/variable/time_frequency/region'.split('/')

    path = request.GET['path']
    facet_list = path.split('/')
    fn = facet_list.pop(-1)

    query_dict = dict()
    for i in xrange(-1, -1 - len(path_structure), -1):
        query_dict[path_structure[i]] = facet_list[i-1]
        print path_structure[i], facet_list[i-1]

    fn_list = fn.split('_')
    query_dict['score'] = fn_list[1]
    time_list = fn_list[2].split('-')

    exists = HindcastEvaluation.objects.filter(**query_dict).exists()

    if exists:
        hindcast = HindcastEvaluation.objects.get(**query_dict)
    else:
        hindcast = HindcastEvaluation.objects.create(
            eva_time_start=time_list[0],
            eva_time_end=time_list[1],
            **query_dict
        )

    if facet_list[-1] == 'map':
        if int(time_list[1]) >= int(hindcast.eva_time_end):
            hindcast.path_map = path
            hindcast.eva_time_end = time_list[1]
    else:
        if int(time_list[1]) >= int(hindcast.eva_time_end):
            hindcast.path_fieldmean = path
            hindcast.eva_time_end = time_list[1]

    hindcast.save()
    return Response(request.GET['path'])


@api_view(['GET'])
@login_required()
def get_hindcast_facets(request):
    data = request.GET
    facet = convert(data['facet'])

    qs = HindcastEvaluation.objects.all()

    for key, val in data.iteritems():
        key = convert(key)
        if key != 'facet':
            qs = qs.filter(**{key: val})
    map_data = qs.filter(path_map__isnull=False, path_fieldmean__isnull=False).values_list(facet, flat=True).distinct()
    result = []
    for val in map_data:
        result.append(dict(value=val, label=display_names.get(val) or val))

    return Response(sorted(result, key=itemgetter('label')))


@api_view(['GET'])
@login_required()
def get_hindcast_data(request):
    from netCDF4 import Dataset
    data = request.GET
    hindcast = HindcastEvaluation.objects.get(
        hindcast_set=data['hindcastset'],
        reference=data['reference'],
        variable=data['variable'],
        score=data['metric'],
        region=data['region']
    )
    fn = getattr(hindcast,'path_%s' % data['type'])
    cache_key = fn + data['leadtime'] if data['type'] == 'map' else fn

    ref_var = 'ref'
    if data['reference'] == 'vs_clim':
        ref_var = 'clim'

    result = cache.get(cache_key)
    if result:
        return Response(result)

    if data['type'] == 'map':

        leadtime = int(data['leadtime'])
        f = Dataset(fn, 'r')#netcdf.netcdf_file(fn, 'r')
        score = np.array(f.variables[data['metric']+'_' + ref_var])#.data.copy().squeeze()
        score_sign = np.array(f.variables[data['metric']+'_'+ ref_var + '_sign'])#.data.copy().squeeze()

        lon = np.array(f.variables['lon'])#.data.copy()
        lat = np.array(f.variables['lat'])#.data.copy()
        step = lon[10] - lon[9]

        lat = lat - step


        result = []
        for i, lon_val in enumerate(lon):
            for j, lat_val in enumerate(lat):
                if -90 <= lat_val <= 90:
                    polygon = [["%s" % lon_val, "%s" % lat_val], ["%s" % (lon_val + step), "%s" % lat_val],
                               ["%s" % (lon_val + step), "%s" % (lat_val + step)],
                               ["%s" % lon_val, "%s" % (lat_val + step)]]

                    sel = (leadtime-1, j, i) if len(score.shape) > 2 else (j,i )
                    result.append(
                        dict(type='LineString',
                             score="%s" % round(score[sel], 2),
                             coordinates=polygon,
                             score_sign=str(score_sign[sel])
                             )
                    )

    else:
        f = Dataset(fn, 'r')#netcdf.netcdf_file(fn, 'r')
        score = np.array(f.variables[data['metric']+'_' + ref_var])#f.variables[data['metric'] + '_' + ref_var].data.copy().squeeze()
        score_sign = np.array(f.variables[data['metric']+'_'+ ref_var + '_sign'])#f.variables[data['metric'] + '_' + ref_var + '_sign'].data.copy().squeeze()

        score_result = []
        sign = []

        for ly in range(0, len(score)):
            score_result.append({'x': ly+1, 'y': round(score[ly], 2)})
            if score_sign[ly] != 0:
                sign.append({'x': ly+1, 'y': round(score[ly], 2)})

        result = {'score': score_result, 'sign': sign}

    cache.set(cache_key, result, None)
    return Response(result)
