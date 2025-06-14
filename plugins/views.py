""" Views for the plugins application """

import json
import logging
import os
import urllib
from pathlib import Path

import evaluation_system.api.plugin_manager as pm
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
from evaluation_system.misc import config
from evaluation_system.model.user import User

from base.exceptions import UserNotFoundError
from base.Users import OpenIdUser
from django_evaluation.settings.local import HOME_DIRS_AVAILABLE
from history.models import Configuration, History
from plugins.forms import PluginForm, PluginWeb
from plugins.utils import (
    get_plugin_or_404,
    get_scheduler_hosts,
    is_path_relative_to,
    ssh_call,
)


@login_required()
def plugin_list(request):
    """
    New view for plugin list
    TODO: As we use react now, we should use ONE default view for all react pages
    """
    return render(request, "plugins/list.html", {"title": "Plugins"})


@login_required()
def detail(request, plugin_name):
    """
    New view for plugin list
    TODO: As we use react now, we should use ONE default view for all react pages
    """
    return render(request, "plugins/list.html", {"title": plugin_name})


@login_required()
def search_similar_results(request, plugin_name=None, history_id=None):
    pm.reload_plugins(request.user.username)

    def hist_to_dict(h_obj):
        hist_dict = dict()
        results = h_obj.result_set.filter(file_type=1)
        hist_dict["preview"] = ""
        if len(results) > 0:
            hist_dict["preview"] = results[0].preview_file
        hist_dict["pk"] = h_obj.pk
        hist_dict["tool"] = h_obj.tool
        hist_dict["uid"] = str(h_obj.uid)
        return hist_dict

    data = {}

    if request.session.get('user_info', {}).get('is_guest'):
        hist_objects = History.objects.filter(uid=request.user).filter(tool=plugin_name)
    else:
        try:
            user = OpenIdUser(request.user.username)
        except UserNotFoundError:
            user = User()
        if history_id is not None:
            o = Configuration.objects.filter(history_id_id=history_id)
            hist_objects = History.find_similar_entries(o, max_entries=5)

        else:
            # create the tool
            tool = pm.get_plugin_instance(plugin_name, user=user)
            param_dict = tool.__parameters__
            param_dict.synchronize(plugin_name)
            plugin_fields = param_dict.keys()

            # don't search for empty form fields
            for key, val in request.GET.items():
                if val != "":
                    if key in plugin_fields:
                        data[key] = val

            try:
                o = pm.dict2conf(plugin_name, data, user=user)
            except Exception:
                return HttpResponse("[]")
            hist_objects = History.find_similar_entries(
                    o, uid=request.user.username, max_entries=5
                )

    res = list()
    for obj in hist_objects:
        res.append(hist_to_dict(obj))
    #    data = serializers.serialize('json',hist_objects,fields=('preview'))
    return HttpResponse(json.dumps(res))


@sensitive_post_parameters("password_hidden")
@sensitive_variables("password")
@login_required()
def setup(request, plugin_name, row_id=None):
    pm.reload_plugins(request.user.username)
    user_can_submit = request.session.get("user_info", {}).get("isGuest")
    if user_can_submit:
        try:
            user = OpenIdUser(request.user.username)
        except UserNotFoundError:
            user = User()
    else:
        user = User()

    plugin = get_plugin_or_404(plugin_name, user=user)

    error_msg = pm.get_error_warning(plugin_name)[0]

    if request.method == "POST":
        form = PluginForm(request.POST, tool=plugin, uid=request.user.username)
        if form.is_valid():
            # read the configuration
            config_dict = dict(form.data)

            # read the caption
            caption = config_dict[form.caption_field_name][0].strip()

            if not caption:
                caption = None

            unique_output = config_dict["unique_output_id"][0]

            # empty values in the form will not be added to the dictionary.
            # as a consequence we can not submit intentionally blank fields.
            tmp_dict = dict()
            for k, v in config_dict.items():
                if v[0]:
                    tmp_dict[str(k)] = "'%s'" % str(v[0])

            config_dict = tmp_dict
            del (
                config_dict["password_hidden"],
                config_dict["csrfmiddlewaretoken"],
            )
            _ = config_dict.pop(form.caption_field_name, "")
            logging.debug(config_dict)

            # start the scheduler via sbatch
            username = request.user.username
            password = request.POST["password_hidden"]
            hostnames = list(get_scheduler_hosts(request.user))

            logging.info(hostnames)
            # compose the plugin command

            slurm_options = config.get_section("scheduler_options")

            # Get modules and files to source
            config.reloadConfiguration()
            eval_str = f"EVALUATION_SYSTEM_CONFIG_FILE={config.CONFIG_FILE}"
            exe_path = f"PATH={settings.FREVA_BIN}:$PATH"

            if "EVALUATION_SYSTEM_PLUGINS_%s" % request.user in os.environ:
                plugin_str = os.environ["EVALUATION_SYSTEM_PLUGINS_%s" % request.user]
                export_user_plugin = "EVALUATION_SYSTEM_PLUGINS=%s" % plugin_str
            else:
                export_user_plugin = ""
            scheduler_options = ",".join(
                [
                    s
                    for s in config_dict.get("extra_scheduler_options", "").split(",")
                    if s.strip()
                ]
            )
            sched_opts_str = f"extra_scheduler_options={scheduler_options}"
            cmd = plugin.compose_command(
                config_dict,
                batchmode="web" if slurm_options else False,
                caption=caption,
                unique_output=unique_output,
            )
            if scheduler_options:
                cmd.append(sched_opts_str)
            command = " ".join(cmd)
            ssh_cmd = f'bash -c "{eval_str} {exe_path} {export_user_plugin} freva-plugin {command}"'
            logging.info(ssh_cmd)
            # finally send the ssh call
            _, stdout, stderr = ssh_call(
                username=username,
                password=password,
                # we use "bash -c because users with other login shells can't use "export"
                # not clear why we removed this in the first place...
                command=ssh_cmd,
                hostnames=hostnames,
            )

            # get the text form stdout
            out = stdout.readlines()
            err = stderr.readlines()

            logging.debug("command:" + str(ssh_cmd))
            logging.debug("output of analyze:" + str(out))
            logging.debug("errors of analyze:" + str(err))
            try:
                row_id = (
                    History.objects.filter(uid=request.user.username, tool=plugin_name)
                    .latest("timestamp")
                    .id
                )
            except Exception as error:
                logging.exception(error)
                # We couldn't find out the row id due to issues with the log file.
                # Redirect to user's history
                return redirect("history:history")

            return redirect("history:results", id=row_id)

    else:
        # load data into form, when a row id is given.
        if row_id:
            h = History.objects.get(pk=row_id)
            config_dict = h.config_dict()
            f = PluginForm(tool=plugin, uid=user.getName())
            config_dict[f.caption_field_name] = h.caption
        else:
            config_dict = plugin.setup_configuration(check_cfg=False, substitute=True)

        form = PluginForm(initial=config_dict, tool=plugin, uid=user.getName())

    plugin_dict = pm.get_plugin_metadata(plugin_name, user_name=request.user.username)

    home_dir = user.getUserHome() if HOME_DIRS_AVAILABLE else None
    try:
        scratch_dir = user.getUserScratch()
    except:
        scratch_dir = None
    plugin_web = PluginWeb(plugin)

    return render(
        request,
        "plugins/setup.html",
        {
            "tool": plugin_web,
            "user_exported": plugin_dict.user_exported,
            "form": form,
            "user_home": home_dir,
            "user_scratch": scratch_dir,
            "error_message": error_msg,
            "restricted_user": not user_can_submit,
            "show_pw_error": "password_hidden" in form.errors.keys(),
            "PREVIEW_URL": settings.PREVIEW_URL,
        },
    )


@login_required()
def dirlist(request):
    try:
        user = OpenIdUser(request.user.username)
        home_dir = user.getUserHome()
        scratch_dir = user.getUserScratch()
    except UserNotFoundError as e:
        logging.exception(e)
        # This user has no access to the underlying system and therefore
        # must not be able to get a file listing
        return HttpResponse(
            '<div class="alert alert-danger">You are not allowed to see the folder listing</div>'
        )

    base_directory = Path(urllib.parse.unquote(request.POST.get("dir"))).resolve()
    if not is_path_relative_to(base_directory, home_dir) and not is_path_relative_to(
        base_directory, scratch_dir
    ):
        # user is trying to get a listing of a folder he is not allowed to see
        return HttpResponse(
            '<div class="alert alert-danger">Invalid base folder requested</div>'
        )
    elif not base_directory.exists():
        return HttpResponse(
            f'<div class="alert alert-warning">The directory {base_directory} does not exists. Please create it on a HPC login-node first</div>'
        )

    # we can specify an ending in GET request
    files = list()
    file_type = request.GET.get("file_type", "nc")
    r = ['<ul class="jqueryFileTree" style="display: none;">']
    try:
        for f in sorted(os.listdir(base_directory)):
            if f[0] != ".":
                ff = os.path.join(base_directory, f)
                if os.path.isdir(ff):
                    r.append(
                        '<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>'
                        % (ff, f)
                    )
                else:
                    e = os.path.splitext(f)[1][1:]  # get .ext and remove dot
                    if e == file_type:
                        files.append(
                            '<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>'
                            % (e, ff, f)
                        )
    except Exception as e:
        r.append("Could not load directory: %s" % str(e))
    r = r + files
    r.append("</ul>")
    return HttpResponse("".join(r))


@login_required()
def list_dir(request):
    try:
        user = OpenIdUser(request.user.username)
        home_dir = user.getUserHome()
        scratch_dir = user.getUserScratch()
    except UserNotFoundError:
        # This user has no access to the underlying system and therefore
        # must not be able to get a file listing
        return JsonResponse(
            {
                "status": "You are not allowed to see the folder listing",
                "folders": [],
            }
        )

    # we can specify an ending in GET request
    base_directory = Path(urllib.parse.unquote(request.GET.get("dir")))
    resolved_dir = base_directory.resolve()
    if (
        not is_path_relative_to(base_directory, home_dir)
        and not is_path_relative_to(base_directory, scratch_dir)
    ) or not resolved_dir.exists():
        # user is trying to get a listing of a folder he is not allowed to see
        return JsonResponse({"status": "Invalid base folder requested", "folders": []})
    elif not base_directory.exists():
        return JsonResponse(
            {
                "status": f"The directory {base_directory} does not exists. Please create it on a HPC login-node first",
                "folders": [],
            }
        )

    files = []
    folders = []
    # we can specify an ending in GET request
    file_type = request.GET.get("file_type", "pdf")
    try:
        for f in sorted(os.listdir(base_directory)):
            if f[0] != ".":
                ff = os.path.join(base_directory, f)
                if os.path.isdir(ff):
                    folders.append(dict(type="folder", path=ff, name=f))
                else:
                    e = os.path.splitext(f)[1][1:]  # get .ext and remove dot
                    if e == file_type:
                        files.append(dict(type="file", ext=e, path=ff, name=f))
        folders = folders + files
    except Exception as e:
        return JsonResponse(
            {
                "status": "Could not load directory: %s" % str(e),
                "folders": [],
            }
        )
    return JsonResponse({"status": "success", "folders": folders})


def list_docu(request):
    return render(request, "plugins/list-docu.html")
