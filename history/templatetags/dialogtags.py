import json

from django import template
from django.utils.safestring import mark_safe

from django_evaluation import settings
from django_evaluation.ldaptools import get_ldap_object

register = template.Library()


@register.inclusion_tag("history/templatetags/dialog.html")
def cancel_dialog():
    return {}


@register.inclusion_tag("history/templatetags/sendmail_dialog.html")
def sendmail_dialog(url, is_guest):
    return {"url": url, "is_guest": is_guest}


@register.inclusion_tag("history/templatetags/caption_dialog.html")
def caption_dialog(current, default, history_object, user):
    return {
        "current_caption": current,
        "default_caption": default,
        "history_object": history_object,
        "user": user,
    }


@register.inclusion_tag("history/templatetags/mailfield.html")
def mailfield(is_guest):
    info = []
    user_info = get_ldap_object()

    if not is_guest:
        info = user_info.get_all_users()

    data = []

    for user in info:
        id = user[0]
        data.append({"id": id, "text": "%s, %s (%s)" % (user[1], user[2], user[0])})

    return {"user_data": mark_safe(json.dumps(data)), "is_guest": is_guest}
