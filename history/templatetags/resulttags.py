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


        print 'Sorted:\n', sorted(dict_.items(), key=lambda(k, v) : '*' + str(k) if isinstance(v,FileDict) else str(k))

        sort_key = lambda(k, v) : ('d' if isinstance(v,FileDict) else 'f') + str(k)

        for key,value in sorted(dict_.items(), key=sort_key):
            subdict = ''
            subdict_item = None
            if isinstance(dict_[key], FileDict):
                subdict_item = dict_[key]

            #if child is a dictionary use recursion
            if subdict_item:
                print key, subdict_item.values()[-1].__class__.__name__
                subdict = _helperDict(subdict_item,depth+1)

                has_filedict = False

                for v in subdict_item.values():
                    has_filedict = has_filedict or isinstance(v, FileDict)

                # if isinstance(subdict_item.values()[0],FileDict):
                if has_filedict:
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
