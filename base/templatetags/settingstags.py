from django import template
from django.conf import settings

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
def get_menu_entries(entry):
    return getattr(settings,entry,None)



@register.assignment_tag
def external_group():
    return getattr(settings, 'EXTERNAL_GROUP', None)
