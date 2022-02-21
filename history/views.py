from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.flatpages.models import FlatPage
from django.utils.html import escape
from datatableview import helpers, columns
from datatableview import Datatable
from datatableview.views import XEditableDatatableView

from django_evaluation.ldaptools import get_ldap_object

import json
import os

import evaluation_system.api.plugin_manager as pm
from evaluation_system.model.db import UserDB
from evaluation_system.model.user import User
from evaluation_system.misc import config

from evaluation_system.model.history.models import History, ResultTag
from django_evaluation import settings
from plugins.utils import ssh_call, get_scheduler_hosts

from history.utils import FileDict, sendmail_to_follower

from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.db.models import Q
from django.urls import reverse

import logging
from history.models import HistoryTag
from history.templatetags.resulttags import mask_uid


class HistoryDatatable(Datatable):
    configuration = columns.TextColumn(
        "Configuration", sources=["configuration"], processor="info_button"
    )

    select_data = columns.TextColumn("", sources=["select_data"], processor="checkbox")

    status = columns.TextColumn("Status", sources=["get_status_display"])

    class Meta:
        model = History
        columns = [
            "select_data",
            "id",
            "uid",
            "tool",
            "caption",
            "timestamp",
            "status",
            "configuration",
        ]
        structure_template = "datatableview/default_structure.html"

    def checkbox(self, instance, *args, **kwargs):
        id = "cb_%i" % instance.id
        cb = '<input type="checkbox" id="%s" class="chksel">' % id
        return cb

    def info_button(self, instance, *args, **kwargs):
        # default text and format (scheduled jobs)
        request = kwargs.get("view").request
        information = "Information to scheduled job:"
        css_class = "class='btn btn-primary btn-sm ttbtn'"
        button_text = "Info"

        # change things for manually started jobs slightly
        if instance.slurm_output == "0":
            information = "Restricted information to manually started job:"
            css_class = "class='btn btn-info btn-sm ttbtn'"
            button_text = "Info"

        try:
            url = reverse("history:jobinfo", args=[instance.id])
            href = "href='%s'" % url
        except Exception as e:
            return escape(str(e))

        tooltip_style = (
            "data-bs-html='true' data-bs-toggle='tooltip' data-bs-placement='left'"
        )

        caption = instance.caption if instance.caption else ""

        config = (
            '%s<br><br><table class="table-condensed blacktable w-100">' % information
        )

        # fill configuration
        try:
            # this is much faster than the routine config_dict.
            config_dict = json.loads(instance.configuration)
            for key, value in config_dict.items():
                text = escape(mask_uid(str(value), request.user.isGuest()))
                config += (
                    '<tr class="blacktable"><td class="blacktable">%s</td><td class="blacktable">%s<td></tr>'
                    % (key, text)
                )
        except Exception as e:
            print("Tooltip error: ", e)

        config += "</table>"

        if caption:
            title = "title='%s<br><br>%s'" % (caption, config)
        else:
            title = "title='%s'" % (config,)

        info_button = "<a %s %s %s %s>%s</a>" % (
            css_class,
            href,
            tooltip_style,
            title,
            button_text,
        )

        result_text = "Results"
        style = "class='btn btn-success btn-sm'"

        try:
            url = reverse("history:results", args=[instance.id])
            href = "href='%s'" % url
        except Exception as e:
            return escape(str(e))

        second_button_text = "Edit Config"
        second_button_style = 'class="btn btn-success btn-sm"'

        try:
            url = reverse("plugins:setup", args=[instance.tool, instance.id])
            second_button_href = "href='%s'" % url
        except Exception as e:
            return escape(str(e))

        if instance.status in [
            instance.processStatus.finished_no_output,
            instance.processStatus.broken,
            instance.processStatus.not_scheduled,
        ]:
            result_text = "Report"

        elif instance.status in [
            instance.processStatus.scheduled,
            instance.processStatus.running,
        ]:
            result_text = "Progress"
            second_button_text = "Cancel Job"
            second_button_style = 'class="btn btn-danger btn-sm mybtn-cancel"'

            second_button_href = 'onclick="cancelDialog.show(%i);"' % instance.id

            # disable button for manually started jobs
            ## FIXME: == stat !=
            if instance.slurm_output != "0":
                second_button_text = "n/a"
                second_button_style = (
                    'class="btn btn-danger btn-sm mybtn-cancel disabled"'
                )
                second_button_href = ""

            # disable button when its not the user's job
            if instance.uid != request.user:
                second_button_style = (
                    'class="btn btn-danger btn-sm mybtn-cancel disabled"'
                )
                second_button_href = ""

        result_button = "<a  %s %s>%s</a>" % (style, href, result_text)

        second_button = "<a %s %s>%s</a>" % (
            second_button_style,
            second_button_href,
            second_button_text,
        )

        return "%s\n%s\n%s" % (result_button, second_button, info_button)


class HistoryTable(XEditableDatatableView):
    datatable_class = HistoryDatatable
    template_name = "history/history_list.html"

    def get_queryset(self):
        user = self.kwargs.get("uid", self.request.user)

        if not (user and self.request.user.has_perm("history.results_view_others")):
            user = self.request.user

        objects = History.objects.order_by("-id").filter(uid=user)

        status = int(self.request.GET.get("status", -1))
        flag = int(self.request.GET.get("flag", -1))
        plugin = self.request.GET.get("plugin", None)
        if status >= 0:
            objects = objects.filter(status=status)

        if flag >= 0:
            objects = objects.filter(flag=flag)
        else:
            objects = objects.filter(~Q(flag=History.Flag.deleted))

        if plugin:
            objects = objects.filter(tool=plugin)

        return objects

    def get_context_data(self, **kwargs):
        context = super(HistoryTable, self).get_context_data(**kwargs)

        flag = int(self.request.GET.get("flag", -1))
        status = int(self.request.GET.get("status", -1))
        uid = self.kwargs.get("uid", self.request.user)

        context["STATUS_CHOICES"] = History.STATUS_CHOICES
        context["flag"] = flag
        context["status"] = status
        context["uid"] = uid
        return context


@login_required
def change_flag(request):
    ids = json.loads(request.POST.get("ids", ""))
    flag = request.POST.get("flag", None)

    user = str(request.user)
    db = UserDB(user)

    changed = 0

    if not (flag is None or request.user.isGuest()):
        for id in ids:
            changed += 1

            try:
                db.changeFlag(id, user, flag)

                # notify followers
                if int(flag) == int(History.Flag.deleted):
                    try:
                        name = "%s %s" % (
                            request.user.first_name,
                            request.user.last_name,
                        )

                        subject = "Deleted evaluation"
                        message = (
                            "The evaluation %s you are following has been deleted by %s.\n"
                            % (str(id), name)
                        )

                        sendmail_to_follower(request, id, subject, message)
                    except Exception as e:
                        logging.error(e)
            # TODO: Exception too broad!
            except:
                changed -= 1

    retstr = ""
    if changed != len(ids):
        retstr = "Changed %i of %i entries" % (changed, len(ids))

    return HttpResponse(retstr, content_type="text/plain")


@login_required
def follow_result(request, history_id):
    retstr = "Follow"

    history_object = get_object_or_404(History, id=history_id)

    # check if the user has the permission to access the result
    flag = history_object.flag
    guest = request.user.isGuest()

    if not guest and flag in [
        History.Flag.free,
        History.Flag.public,
        History.Flag.guest,
    ]:
        user = str(request.user)
        pm.follow_history_tag(history_object.id, user, "Web page: follow")
        retstr = "Unfollow"

    return HttpResponse(retstr, content_type="text/plain")


@login_required
def unfollow_result(request, history_id):
    """
    This routine renders the unfollow view.
    When the get parameter "button" is given, only
    the strings "Follow" and "Unfollow" will be returned.
    This is used for the button in the result view.
    """
    retstr = "Unfollow"
    success = False

    history_object = get_object_or_404(History, id=history_id)

    user = str(request.user)
    try:
        pm.unfollow_history_tag(history_object.id, user)
        retstr = "Follow"
        success = True
    # Todo: Exception too broad!
    except:
        pass

    if request.GET.get("button", None):
        return HttpResponse(retstr, content_type="text/plain")
    else:
        return render(
            request,
            "history/unfollow.html",
            {"success": success, "history_id": history_id},
        )


@login_required
def jobinfo(request, id):
    return results(request, id, True)


def results(request, id, show_output_only=False):
    from history.utils import pygtailwrapper

    # get history object
    history_object = get_object_or_404(History, id=id)
    try:
        user = User(request.user.username)
    except:
        user = User()

    plugin = pm.get_plugin_instance(history_object.tool, user=user)
    developer = plugin.tool_developer
    # check if the user has the permission to access the result
    flag = history_object.flag

    if not flag == History.Flag.free:
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login

            path = request.get_full_path()
            return redirect_to_login(path)

        elif not history_object.uid == request.user:
            if request.user.isGuest():
                if flag != History.Flag.guest:
                    raise PermissionDenied
            elif not (
                request.user.has_perm("history.results_view_others")
                and flag
                in [History.Flag.public, History.Flag.shared, History.Flag.guest]
            ):
                raise PermissionDenied
    if not request.user.is_authenticated:
        request.user.isGuest = True

    try:
        documentation = FlatPage.objects.get(title__iexact=history_object.tool)
    except FlatPage.DoesNotExist:
        documentation = None
    try:
        logging.debug(history_object.uid.email)
    # TODO: Exception too broad!
    except:
        pass

    try:
        analyze_command = pm.get_command_string(int(id))
    except Exception as e:
        logging.debug(e)
    analyze_command = pm.get_command_string(int(id))

    history_object = History.objects.get(id=id)
    file_content = []

    # ensure that this process has been started with slurm
    if history_object.slurm_output == "0":
        file_content = [
            "This job has been started manually.",
            "No further information is available.",
        ]

    else:
        # for a read-protected directory this will fail
        try:
            # maintenance programmer info: My first impression was that the pygtailwrapper here is useless.
            # It actually makes sense for still running jobs since it will update the log-output
            # every time something happened (frontend is polling for new data via /history/<id>/tail-file
            for line in pygtailwrapper(id, restart=True):
                file_content.append(line)
        except IOError:
            file_content = [
                "WARNING:",
                "This is not the content of the file '"
                + history_object.slurm_output
                + "'.",
                "Probably, your home directory denies read access to the file.",
                "In this case the results will be shown after the tool has finished.",
                "You can view the tool's progress in a terminal with the command",
                "tail -f " + history_object.slurm_output,
            ]

            # make sure that the file exists
            try:
                if not os.path.isfile(history_object.slurm_output):
                    file_content = [
                        "Can not locate the slurm file '%s'"
                        % history_object.slurm_output
                    ]
            except IOError:
                pass

    # init result object
    result_object = -1
    file_tree = None

    collapse = []

    if history_object.status in [
        History.processStatus.finished,
        History.processStatus.finished_no_output,
    ]:
        result_object = history_object.result_set.filter(~Q(preview_file="")).order_by(
            "output_file"
        )

        # build the file structure
        fd = FileDict()

        for r in result_object:
            caption = ResultTag.objects.filter(result_id_id=r.id).order_by("-id")
            result_info = {}
            result_info["preview_file"] = r.preview_file

            if caption:
                result_info["caption"] = caption[0].text
            fd.add_file(r.output_file, result_info)

        file_tree = fd.compressed_copy()
        file_tree.uncompress_single_files()

        collapse.append("results")
        if len(file_tree) == 0:
            collapse.append("output")
    else:
        collapse.append("output")

    if show_output_only:
        collapse = ["output"]

    # repository stuff
    try:
        repos = history_object.version_details.repository
    except ObjectDoesNotExist:
        repos = "Not available;Not available"
    tool_repos = repos.split(";")[0]
    api_repos = repos.split(";")[1]
    try:
        tool_version = history_object.version_details.internal_version_tool
        api_version = history_object.version_details.internal_version_api
    except ObjectDoesNotExist:
        tool_version = "Not available"
        api_version = "Not available"
    result_caption = history_object.caption
    if result_caption is None:
        result_caption = history_object.tool.upper()

    htag_notes = None
    follow_string = "Follow"

    historytag_objects = HistoryTag.objects.filter(history_id_id=id)

    try:
        htag_notes = historytag_objects.filter(
            (Q(uid=request.user) & Q(type=HistoryTag.tagType.note_private))
            | Q(type=HistoryTag.tagType.note_public)
        ).order_by("id")

    except Exception as e:
        logging.error(e)

    try:
        follow = historytag_objects.filter(
            Q(uid=request.user) & Q(type=HistoryTag.tagType.follow)
        )

        if len(follow) > 0:
            follow_string = "Unfollow"

    except Exception as e:
        logging.error(e)
    return render(
        request,
        "history/results.html",
        {
            "history_object": history_object,
            "result_object": result_object,
            "result_caption": result_caption,
            "file_content": file_content,
            "collapse": collapse,
            "PREVIEW_URL": settings.PREVIEW_URL,
            "file_list": file_tree,
            "documentation": documentation,
            "analyze_command": analyze_command,
            "api_repos": api_repos,
            "tool_repos": tool_repos,
            "api_version": api_version,
            "tool_version": tool_version,
            "notes": htag_notes,
            "follow": follow_string,
            "developer": developer,
        },
    )


@login_required()
def tail_file(request, id):
    from history.utils import pygtailwrapper

    history_object = get_object_or_404(History, id=id)
    new_lines = list()

    try:
        for lines in pygtailwrapper(id):
            line = lines.replace("\n", "<br/>")
            new_lines.append(line)
    except IOError:
        pass

    if history_object.status < 2:
        new_lines = False

    return HttpResponse(json.dumps(new_lines), content_type="application/json")


@login_required()
def generate_caption(request, id, type):
    caption = request.POST["caption"].strip()
    tool_name = request.POST["tool"].strip().capitalize()

    retval = pm.generate_caption(caption, tool_name)

    if not request.user.isGuest():

        hist = History.objects.get(id=id)
        if hist.uid == request.user:
            hist.caption = retval
            hist.save()
        else:
            retval = "*" + retval

    else:
        retval = "*" + retval

    return HttpResponse(json.dumps(retval), content_type="application/json")


@sensitive_post_parameters("password")
@login_required()
def cancel_slurmjob(request):

    from paramiko import AuthenticationException

    history_item = History.objects.get(pk=request.POST["id"])
    if history_item.status < 3:
        return HttpResponse(
            json.dumps("Job already finished"), content_type="application/json"
        )

    slurm_id = history_item.slurmId()

    try:
        host_names = get_scheduler_hosts(request.user)
        source_machine = settings.LOAD_MODULE
        result = ssh_call(
            username=request.user.username,
            password=request.POST["password"],
            command='bash -c "%s module load slurm; scancel -Q %s;exit 0"'
            % (
                source_machine,
                slurm_id,
            ),
            hostnames=host_names,
        )
        history_item.status = 2
        history_item.save()
        return HttpResponse(
            json.dumps(result[2].readlines()), content_type="application/json"
        )
    except AuthenticationException:
        return HttpResponse(
            json.dumps("wrong password"), content_type="application/json"
        )


@login_required
def result_comments(request, history_id):
    htag_notes = None

    try:
        historytag_objects = HistoryTag.objects.filter(history_id_id=history_id)
        htag_notes = historytag_objects.filter(
            (Q(uid=request.user) & Q(type=HistoryTag.tagType.note_private))
            | Q(type=HistoryTag.tagType.note_public)
        ).order_by("-id")
    except HistoryTag.DoesNotExist:
        pass
    except:
        pass

    return render(
        request,
        "history/comments.html",
        {"history_id": history_id, "notes": htag_notes},
    )


@login_required()
def edit_htag(request, history_id, tag_id):
    from django.template import defaultfilters as filters

    text = request.POST["text"].strip()
    type = int(request.POST["type"])

    allowed_types = [
        HistoryTag.tagType.note_public,
        HistoryTag.tagType.note_private,
        HistoryTag.tagType.note_deleted,
    ]

    retval = ""

    if not request.user.isGuest() and type in allowed_types:
        user = request.user
        db = UserDB(user)

        if tag_id == "0":
            db.addHistoryTag(history_id, type, text, user)

        elif HistoryTag.objects.get(id=tag_id).uid == user:
            db.updateHistoryTag(tag_id, type, text, user.username)

        retval = filters.linebreaks(filters.escape(text))

        # notify followers
        name = "%s %s" % (request.user.first_name, request.user.last_name)
        url = request.build_absolute_uri(
            reverse("history:results", kwargs={"id": history_id})
        )

        if type == HistoryTag.tagType.note_public:
            if tag_id == "0":
                subject = "New comment"
                message = (
                    "%s added new comment to the results of the evaluation %s\n"
                    % (name, history_id)
                )
                message += url

            else:
                subject = "Edited comment"
                message = (
                    "%s edited comment %s belonging to the results of the evaluation %s\n"
                    % (name, tag_id, history_id)
                )
                message += url

            sendmail_to_follower(request, history_id, subject, message)

    return HttpResponse(json.dumps(retval), content_type="application/json")


def count_notes(request, history_id, deleted):
    count = 0

    history_tags = None

    if request.user.is_authenticated:
        try:
            history_tags = HistoryTag.objects.filter(history_id_id=history_id)

            count += history_tags.filter(type=HistoryTag.tagType.note_public).count()
            count += (
                history_tags.filter(type=HistoryTag.tagType.note_private)
                .filter(uid=request.user)
                .count()
            )
        # TODO: Exception too broad!
        except Exception as e:
            pass

    if int(deleted):
        try:
            count += (
                history_tags.filter(type=HistoryTag.tagType.note_deleted)
                .filter(uid=request.user)
                .count()
            )
        # TODO: Exception too broad!
        except:
            pass

    return HttpResponse(str(count), content_type="text/plain")


@login_required()
def result_browser(request):
    return render(request, "plugins/list.html", {"title": "Result-Browser"})
