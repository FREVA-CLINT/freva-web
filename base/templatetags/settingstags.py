from django import template
import requests
from django.conf import settings
from django.core.cache import cache, get_cache


register = template.Library()


@register.simple_tag
def settings_val(value):
    """
    Returns a variable from the settings
    """
    return str(getattr(settings, value))


@register.simple_tag
def setting_to_list(value):
    
    setting_value = getattr(settings, value)
    result = ''
    for val in setting_value:
        result += '<li>%s</li>' % val
    return result


@register.assignment_tag
def shell_in_a_box():
    get_cache('default')
    shell_status_code = None
    return False
    #shell_status_code = cache.get('shell_in_a_box')
    if not shell_status_code:
        url = 'https://%s/shell/' % settings.ALLOWED_HOSTS[0]
        r = requests.get(url)
        shell_status_code = r.status_code
        cache.set('shell_in_a_box', shell_status_code, 3600)
    return True if shell_status_code == 200 else False

@register.assignment_tag
def external_group():
    return getattr(settings, 'EXTERNAL_GROUP', None)
