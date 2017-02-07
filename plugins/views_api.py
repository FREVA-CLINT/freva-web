from rest_framework.views import APIView
from rest_framework.response import Response
import os

import evaluation_system.api.plugin_manager as pm
from evaluation_system.misc import config
from django_evaluation.ldaptools import get_ldap_object
from plugins.utils import get_plugin_or_404
from .forms import PluginWeb
from .serializers import PluginSerializer
from django.conf import settings


class PluginsList(APIView):

    def get(self, request, format=None):
        pm.reloadPlugins(request.user.username)
        tools = pm.getPlugins(request.user.username)
        res = []
        for key, val in sorted(tools.iteritems()):
            res.append([key, val])
        return Response(res)


class PluginDetail(APIView):

    def get(self, request, plugin_name):
        print self.request.user
        pm.reloadPlugins(request.user.username)
        plugin = get_plugin_or_404(plugin_name, user_name=request.user.username)
        #plugin = PluginWeb(plugin)
        return Response(PluginSerializer(plugin).data)


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


class SendMailToDeveloper(APIView):

    def post(self, request):
        from templated_email import send_templated_mail
        text = request.data.get('text', None)
        tool_name = request.data.get('tool_name', None)
        tool = pm.getPluginInstance(tool_name, user_name=request.user.username)
        developer = tool.tool_developer
        user_info = get_ldap_object()
        myinfo = user_info.get_user_info(str(request.user))
        try:
            my_email = myinfo[3]
            username = request.user.get_full_name()
        # TODO: Exception too broad!
        except:
            my_email = settings.SERVER_EMAIL
            username = 'guest'

        send_templated_mail(
            template_name='mail_to_developer',
            from_email=my_email,
            recipient_list=[developer['email']],
            context={
                'username': username,
                'developer_name': developer['name'],
                'text': text,
                'tool_name': tool_name,
                'mail': my_email,
                'project': config.get('project_name'),
                'website': config.get('project_website')
            },
            cc=[a[1] for a in settings.ADMINS],
            headers={'Reply-To': my_email},
        )
        return Response(True)