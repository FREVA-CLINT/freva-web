from django import template
from django.utils.safestring import mark_safe
from django.utils.encoding import force_str
from django.utils.html import conditional_escape
from django.template.loader import render_to_string
from base.LdapUser import LdapUser
from base.exceptions import UserNotFoundError
from django_evaluation import settings

from history.utils import FileDict
from history.models import HistoryTag

from evaluation_system.misc.exceptions import PluginManagerException

import re

register = template.Library()


@register.filter(is_safe=True, needs_autoescape=True)
def preview_tree(value, autoescape=None):
    """
    Template filter to display a FileDict defined in history.utils.FileDict

    :param value: instance of FileDict (compressed_copy)
    """
    if autoescape:
        escaper = conditional_escape
    else:
        escaper = lambda x: x

    def _helper_dict(dict_, depth=0):
        """
        Helper function for the nested display process
        Output is a file tree (unordered list) and preview images using fancybox2

        :param dict_: compressed_copy of a FileDict
        :param depth: tree depth
        """
        output = []

        sort_key = lambda k_v: (
            ("d" if isinstance(k_v[1], FileDict) else "f") + str(k_v[0])
        )

        first_dir = True
        first_file = True

        for key, value in sorted(dict_.items(), key=sort_key):
            subdict = ""
            subdict_item = None

            # set the matching html environment
            if isinstance(dict_[key], FileDict):
                subdict_item = dict_[key]
                if first_dir:
                    output.append('<ul class="jqueryFileTree">')
                    first_dir = False
                    if not first_file:
                        output.append("</div>")
                        first_file = True

            else:
                if first_file:
                    if not first_dir:
                        output.append("</ul>")
                        first_dir = True

                    output.append('<div class="row" >')
                    first_file = False

            # if child is a dictionary use recursion
            if subdict_item:
                subdict = _helper_dict(subdict_item, depth + 1)

            # next lines define css-styles of list items
            visible = "display:none;" if depth > 1 else ""
            wordwrap = "word-wrap: break-word; white-space: normal;"
            folder_image = "directory collapsed" if depth > 0 else "directory expanded"

            if not subdict_item:
                caption = None

                if isinstance(value, dict):
                    caption = value.get("caption", None)

                if caption:
                    caption = "<br>".join([key, caption])
                else:
                    caption = key
                fn = value["preview_file"]
                file_ext = fn.split(".")[-1]
                if file_ext in ["pdf", "zip"]:
                    output.append(
                        '<ul class="jqueryFileTree" style="'
                        + visible
                        + '"><li class="file ext_'
                        + file_ext
                        + '"><a class="pdf_download" target="_blank" href="'
                        + settings.PREVIEW_URL
                        + fn
                        + '">'
                        + key
                        + "</a></li></ul>"
                    )
                elif file_ext in ["mp4", "ogg", "avi"]:
                    output.append(
                        render_to_string(
                            "history/templatetags/preview-vid.html",
                            {
                                "imgname": caption,
                                "preview": value["preview_file"],
                                "PREVIEW_URL": settings.PREVIEW_URL,
                                "visible": visible,
                                "file_ext": file_ext,
                            },
                        )
                    )
                elif file_ext in ["html", "xhtml"]:
                    output.append(
                        render_to_string(
                            "history/templatetags/preview-html.html",
                            {
                                "imgname": caption,
                                "preview": value["preview_file"],
                                "PREVIEW_URL": settings.PREVIEW_URL,
                                "visible": visible,
                            },
                        )
                    )
                else:
                    output.append(
                        render_to_string(
                            "history/templatetags/preview-img.html",
                            {
                                "imgname": caption,
                                "preview": value["preview_file"],
                                "PREVIEW_URL": settings.PREVIEW_URL,
                                "visible": visible,
                            },
                        )
                    )
            else:
                output.append(
                    '<li class="%s" style="%s"><a href="#">%s</a>%s</li>'
                    % (
                        folder_image,
                        visible + wordwrap,
                        escaper(force_str(key)),
                        subdict,
                    )
                )
        # close the html environment
        if not first_file:
            output.append("</div>")

        if not first_dir:
            output.append("</ul>")

        return "\n".join(output)

    return mark_safe(_helper_dict(value))


@register.inclusion_tag("history/templatetags/comment.html")
def comment_field(user, history_id, historytag_entry=None):
    htag = None
    class_id = "new"

    if historytag_entry:
        htag = historytag_entry
        class_id = str(htag.id)

    return {
        "user": user,
        "class_id": class_id,
        "history_id": history_id,
        "htag": htag,
        "tagType": HistoryTag.tagType,
    }


user_mask = {}


@register.inclusion_tag("history/templatetags/mail_to_developer.html")
def mail_to_developer(tool_name, username, url):
    from evaluation_system.api import plugin_manager as pm

    try:
        user = LdapUser(username)
        tool = pm.get_plugin_instance(tool_name, user)
        developer = tool.tool_developer
    except (UserNotFoundError, PluginManagerException, AttributeError):
        developer = None

    return {"tool_name": tool_name, "developer": developer, "current_url": url}


def get_masked_uid(uid):
    try:
        name = user_mask[uid]
    # TODO: Exception too broad!
    except:
        number = len(user_mask) + 1
        name = "User%i" % number
        user_mask[uid] = name

    return name


@register.filter("mask_uid")
def mask_uid(text, is_guest):
    rettext = text

    if is_guest:
        try:
            users = re.findall(settings.USERNAME_FILTER, text)
            for u in users:
                rettext = rettext.replace(u, get_masked_uid(u))
        except:
            pass

    return rettext


@register.filter("mask_safe_uid")
def mask_safe_uid(text, is_guest):
    from django.utils.safestring import mark_safe

    return mark_safe(mask_uid(text, is_guest))
