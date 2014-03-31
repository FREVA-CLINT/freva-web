from django import template
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.template.loader import render_to_string

from django_evaluation import settings

from history.utils import FileDict

import logging

register = template.Library()


@register.filter(is_safe=True, needs_autoescape=True)
def preview_tree(value, autoescape=None):
    """
    Template filter to display a FileDict defined in history.utils.FileDict
    
    :param value: instance of FileDict (compressed_copy)    
    """
    if autoescape:
        escaper = conditional_escape
    else:
        escaper = lambda x: x
       
    def _helperDict(dict_, depth=0):
        '''
        Helper function for the nested display process 
        Output is a file tree (unordered list) and preview images using fancybox2
        
        :param dict_: compressed_copy of a FileDict
        :param depth: tree depth
        '''
        output = []
        for key,value in sorted(dict_.items()):
            subdict = ''
            subdict_item = None
            if isinstance(dict_[key], FileDict):
                subdict_item = dict_[key]

            #if child is a dictionary use recursion
            if subdict_item:
                subdict = _helperDict(subdict_item,depth+1)
                if isinstance(subdict_item.values()[0],FileDict):
                    subdict = '\n<ul class="jqueryFileTree">\n%s\n</ul>\n' % (subdict,)
                else:
                    subdict = '\n<div class="row" >%s</div>\n' % (subdict,)

            #next lines define css-sytles of listitems
            visible = 'display:none;' if depth > 1 else ''
            wordwrap = 'word-wrap: break-word; white-space: normal;'
            folder_image = 'directory collapsed' if depth >0 else 'directory expanded'

            if not subdict_item:
                caption = None

                if isinstance(value,dict):
                    caption = value.get('caption', None)
                
                if caption:
                    caption = '<br>'.join([key, caption])
                else:
                    caption = key

                output.append(render_to_string('history/templatetags/preview-img.html', {'imgname':caption, 'preview':value['preview_file'], 
                                                                                         'PREVIEW_URL':settings.PREVIEW_URL,
                                                                                         'visible':visible}))
            else:
                output.append('<li class="%s" style="%s"><a href="#">%s</a>%s</li>' % (folder_image,
                                                                                       visible + wordwrap,
                                                                                       escaper(force_text(key)),
                                                                                       subdict))
        return '\n'.join(output)
    return mark_safe(_helperDict(value))
