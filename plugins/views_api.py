import os

import evaluation_system.api.plugin_manager as pm
from django.conf import settings
from django.contrib.auth import get_user_model
from evaluation_system.misc import config
from evaluation_system.model.user import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from base.exceptions import UserNotFoundError
from base.Users import OpenIdUser
from plugins.utils import get_plugin_or_404, plugin_metadata_as_dict

from .serializers import PluginSerializer


class PluginsList(APIView):
    def get(self, request, format=None):
        pm.reload_plugins(request.user.username)
        plugins = pm.get_plugins(request.user.username)
        tools = {
            k: plugin_metadata_as_dict(v)
            for (k, v) in pm.get_plugins(request.user.username).items()
        }
        res = sorted(tools.items())
        return Response(res)


class PluginDetail(APIView):
    def get(self, request, plugin_name):
        pm.reload_plugins(request.user.username)
        user = None
        try:
            user = OpenIdUser(request.user.username)
        except UserNotFoundError:
            user = User()
        plugin = get_plugin_or_404(plugin_name, user=user)
        plugin_dict = pm.get_plugin_metadata(
            plugin_name, user_name=request.user.username
        )
        print(f"plugin_dict: {plugin.tool_developer}")
        # plugin = PluginWeb(plugin)
        data = PluginSerializer(plugin).data
        data["user_exported"] = plugin_dict.user_exported
        return Response(data)


"""
ExportPlugin does not export anything. It either deletes a Env-Variable
EVALUATION_SYSTEM_PLUGINS_<username> which has a path to a Plugin
or it _IMPORTS_ a plugin to freva by setting the same env-variable.

FIXME: At least in the dev-environment there is another env-var EVALUATION_SYSTEM_PLUGINS (without suffix)
which also contains the path to a plugin. This one is connected to all
users and if it is set then the "remove exported plugin"-Button in the web-interface is
basically useless.
"""


class ExportPlugin(APIView):
    def post(self, request):
        if request.session["user_home_dir"] == "":
            return Response("Guests are not allowed to add plugins")

        # try to remove plugin from enironment
        try:
            del os.environ["EVALUATION_SYSTEM_PLUGINS_%s" % request.user]
            return Response("Plugin removed")
        # add plugin to env
        except:
            fn = request.data.get("export_file")
            if fn and os.path.isfile(fn):
                fn = os.path.normpath(fn)
                parts = fn.split("/")
                path = "/".join(parts[:-1])
                module = parts[-1].split(".")[0]
                os.environ["EVALUATION_SYSTEM_PLUGINS_%s" % request.user] = "%s,%s" % (
                    path,
                    module,
                )
            return Response(fn)


class SendMailToDeveloper(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if request.session["user_home_dir"] == "":
            return Response(False)
        from templated_email import send_templated_mail

        text = request.data.get("text", None)
        tool_name = request.data.get("tool_name", None)
        url = request.data.get("url", None)

        if url:
            text = text + "\nThis email has been send from this url: " + url
        try:
            user = OpenIdUser(request.user.username)
        except UserNotFoundError:
            user = User()

        my_email = request.user.email
        username = request.user.get_full_name()

        if not username:
            username = request.user.username

        if not my_email:
            my_email = settings.SERVER_EMAIL

        tool = pm.get_plugin_instance(tool_name, user=user)
        developer = tool.tool_developer

        send_templated_mail(
            template_name="mail_to_developer",
            from_email=my_email,
            recipient_list=[developer["email"]],
            context={
                "username": username,
                "developer_name": developer["name"],
                "text": text,
                "tool_name": tool_name,
                "mail": my_email,
                "project": config.get("project_name"),
                "website": config.get("project_website"),
            },
            #  cc=[a[1] for a in settings.ADMINS],
            headers={"Reply-To": my_email},
        )
        return Response(True)


class ShareResultsByMail(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if request.session["user_home_dir"] == "":
            status = "Normally, the selected recipients would get an email containing a link to this result,"
            status += "but this feature is turned off for guest users."
            return Response(status)
        from templated_email import send_templated_mail

        text = request.data.get("text", None)
        url = request.data.get("url", None)

        my_email = request.user.email
        username = request.user.get_full_name()

        one4all = request.data.get("one4all", "off")
        copy4me = request.data.get("copy4me", "off")

        if not username:
            username = request.user.username

        if not my_email:
            my_email = settings.SERVER_EMAIL

        recipient_names = request.POST["rec"].split(",")

        email_adresses = []
        for uid in recipient_names:
            user = get_user_model().objects.get(username=uid)
            if user.email:
                email_adresses.append(user.email)

        if copy4me == "on":
            email_adresses.append(my_email)
        if one4all == "on":
            send_templated_mail(
                template_name="share_results",
                from_email=my_email,
                recipient_list=email_adresses,
                context={
                    "username": username,
                    "text": text,
                    "mail": my_email,
                    "url": url,
                    "project": config.get("project_name"),
                    "website": config.get("project_website"),
                },
                headers={"Reply-To": my_email},
            )
        else:
            for r in email_adresses:
                send_templated_mail(
                    template_name="share_results",
                    from_email=my_email,
                    recipient_list=[r],
                    context={
                        "username": username,
                        "text": text,
                        "mail": my_email,
                        "url": url,
                        "project": config.get("project_name"),
                        "website": config.get("project_website"),
                    },
                    headers={"Reply-To": my_email},
                )
        return Response("Results successfully shared")
