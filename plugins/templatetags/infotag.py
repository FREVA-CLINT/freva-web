from django import template
from evaluation_system.api.plugin_manager import getErrorWarning

register = template.library()

@register.inclusion_tag('plugins/templatetags/infodialog.html')
def infodialog(caption, text, show='show'):
    if show is True:
        show = 'show'
        
    elif show is False:
        show = 'hide'
    
    return {'caption' : caption,
            'text', text,
            'show', show}
    
    
@register.inclusion_tag('plugins/templatetags/infodialog.html')
def error_warning_dialog(toolname):
    (error, warning) = getErrorWarning(toolname)
    
    if error:
        return infodialog('Error', error, 'show')
    elif warning:
        return infodialog('Warning', warning, 'show')
    else:
        return infodialog('', '', 'hide')