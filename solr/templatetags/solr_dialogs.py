from django import template

register = template.Library()


@register.inclusion_tag('solr/templatetags/ncdump_dialog.html')
def ncdump_dialog():
    return {}
