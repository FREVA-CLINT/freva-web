from django import template
from django_evaluation.ldaptools import miklip_user_information
from django.utils.safestring import mark_safe
from django_evaluation import settings

import json

register = template.Library()

@register.inclusion_tag('history/templatetags/dialog.html')
def cancel_dialog():
    return {}

@register.inclusion_tag('history/templatetags/sendmail_dialog.html') #, takes_context = True)
def sendmail_dialog(url, is_guest):
    return {'url' : url, 'is_guest' : is_guest}

@register.inclusion_tag('history/templatetags/mailfield.html')
def mailfield(is_guest):
    info = []
    user_info = miklip_user_information()

    if is_guest:
        for uid in settings.EMAIL_RESTRICTIONS:
            ldap_info = user_info.get_user_info(uid)

            if ldap_info:
                info.append(ldap_info)
    else:
        info = user_info.get_user_info()

    data = []

    for user in info:
        id = user[0]
        data.append({'id' : id, 'text' : "%s, %s (%s)" % (user[1], user[2], user[0])})
    
    return {'user_data' : mark_safe(json.dumps(data))}
