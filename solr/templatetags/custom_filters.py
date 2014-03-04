from django import template

from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def divide(value, arg): return int(value) / int(arg)

@register.filter
def lookup(d, key):
    return d[key]

@register.filter
def dict_to_url(d):
    if d is None:
	return ''
    result = ''
    for key,val in d.iteritems():
	for item in val:
	   result += '&'+key+'='+item
    return mark_safe(result) 
