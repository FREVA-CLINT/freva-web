from django import template

from django_evaluation import settings

register = template.Library()

@register.simple_tag
def settings_val(value):
    """
    Returns a variable from the settings
    """
    
    return str(getattr(settings, value))
