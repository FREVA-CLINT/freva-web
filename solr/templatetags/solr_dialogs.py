from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.inclusion_tag('solr/templatetags/ncdump_dialog.html')
def ncdump_dialog():
   return {}
