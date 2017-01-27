from rest_framework.views import APIView
from rest_framework.response import Response
import os

import evaluation_system.api.plugin_manager as pm


class PluginsList(APIView):

    def get(self, request, format=None):
        pm.reloadPlugins(request.user.username)
        tools = pm.getPlugins(request.user.username)
        res = []
        for key, val in sorted(tools.iteritems()):
            res.append([key, val])
        return Response(res)


class ExportPlugin(APIView):

    def get(self, request):
        # try to remove plugin from enironment
        try:
            del os.environ["EVALUATION_SYSTEM_PLUGINS_%s" % request.user]
            return Response('Plugin removed')
        # add plugin to env
        except:

            fn = request.GET.get('export_file')
            if fn is not None and os.path.isfile(fn):
                parts = fn.split('/')
                path = '/'.join(parts[:-1])
                module = parts[-1].split('.')[0]
                os.environ["EVALUATION_SYSTEM_PLUGINS_%s" % request.user] = \
                    "%s,%s" % (path, module)
            return Response(fn)