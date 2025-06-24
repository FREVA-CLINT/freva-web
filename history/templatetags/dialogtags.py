import json
import logging

from django import template
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.safestring import mark_safe

from django_evaluation import settings

register = template.Library()


@register.inclusion_tag("history/templatetags/dialog.html")
def cancel_dialog():
    return {}


@register.inclusion_tag("history/templatetags/sendmail_dialog.html")
def sendmail_dialog(url):
    return {"url": url}


@register.inclusion_tag("history/templatetags/caption_dialog.html")
def caption_dialog(current, default, history_object, user):
    return {
        "current_caption": current,
        "default_caption": default,
        "history_object": history_object,
        "user": user,
    }


@register.inclusion_tag("history/templatetags/mailfield.html")
def mailfield():
    """Extract the email information from users that have been logged in."""
    data = mark_safe(json.dumps([]))
    try:
        data = cache.get("user_email_info")
    except Exception as error:
        data = None
        logger = logging.getLogger("freva-web")
        logger.error("Could not add user email info to cache: %s", error)
    data = data or mark_safe(
        json.dumps(
            [
                {
                    "id": u.username,
                    "text": f"{u.first_name}, {u.last_name} ({u.email})",
                }
                for u in get_user_model()
                .objects.exclude(email__exact="")
                .exclude(email__isnull=True)
            ]
        )
    )
    return {"user_data": data}
