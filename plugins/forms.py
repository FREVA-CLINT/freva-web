""" Basic models, such as user profile """
from django import forms
import django.contrib.auth as auth
from django.forms import ValidationError
from django.core import validators, exceptions
from django.forms.widgets import Input, Select
from django.shortcuts import render_to_response

from django.template import loader

import evaluation_system.api.plugin_manager as pm
import evaluation_system.api.parameters as parameters

from evaluation_system.misc.utils import PrintableList


class PluginNotFoundError(Exception):
    pass



class PluginWeb(object):
    
    def __init__(self,plugin): 
        self.name = plugin.__class__.__name__
        self.short_description = plugin.__class__.__short_description__
        
        try:
            self.long_description = plugin.__long_description__
        except AttributeError:
            self.long_description = plugin.__short_description__

class PluginFileFieldWidget(Input):
    def render(self, name, value, attrs=None):
        if value is not None and type(value) == list:
            value = PrintableList(value)
        return loader.render_to_string('plugins/filefield.html', {'name': name, 'value': value, 'id':attrs['id']})

class PluginSelectFieldWidget(Input):
    def __init__(self,*args,**kwargs):
	self.options=kwargs.pop('options')
	super(PluginSelectFieldWidget,self).__init__(*args,**kwargs)

    def render(self, name, value, attrs=None):
	return loader.render_to_string('plugins/selectfield.html', {'name':name, 'value':value, 'attrs':attrs, 'options':self.options})

class SolrFieldWidget(Input):
    def __init__(self, *args, **kwargs):
        self.facet = kwargs.pop('facet')
        self.group = kwargs.pop('group')
        self.multiple = kwargs.pop('multiple')
        self.predefined_facets = kwargs.pop('predefined_facets')
        super(SolrFieldWidget,self).__init__(*args,**kwargs)
        
    def render(self, name, value, attrs=None, choices=()):
        return loader.render_to_string('plugins/solrfield.html', {'name': name, 'value': value, 'attrs':attrs, 
                                                                  'facet':self.facet, 'group':self.group, 'multiple':self.multiple,
                                                                  'predefined_facets':self.predefined_facets})

class PluginRangeFieldWidget(Input):
    def render(self, name, value, attrs=None):
        if value is not None and type(value) == list:
            value = PrintableList(value)
        return loader.render_to_string('plugins/rangefield.html', {'name': name, 'value': value, 'id':attrs['id']})
    

class PasswordField(forms.CharField):
    def __init__(self, *args, **kwargs):
        widget = kwargs.get('widget', forms.HiddenInput)
        super(PasswordField, self).__init__(widget=widget)

        self._user = kwargs.pop('uid')

    def validate(self, value):
        u = auth.authenticate(username=self._user, password=value)
        
        if not u:
            raise exceptions.ValidationError('Invalid password', code='invalid_password')

        super(PasswordField, self).validate(value)

class PluginForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        tool = kwargs.pop('tool')
        uid = kwargs.pop('uid')
        
        super(PluginForm, self).__init__(*args, **kwargs)
        
        # set the password field
        self.fields['password_hidden'] = PasswordField(uid=uid)
        
        for key in tool.__parameters__:
            
            param = tool.__parameters__.get_parameter(key)
            param_subtype = param.base_type
            
            if param.mandatory:
                required=True
            else: 
                required=False
            
            help_str = param.help
            
            if isinstance(param, parameters.Bool):
                self.fields[key] = forms.BooleanField(required=required, help_text=help_str, widget=forms.RadioSelect(choices=(('False', 'False'), ('True', 'True'))))
            elif isinstance(param, parameters.Range):
                self.fields[key] = forms.CharField(required=required, help_text=help_str, widget=PluginRangeFieldWidget({}))
            elif isinstance(param, parameters.SelectField):
		self.fields[key] = forms.CharField(required=required, help_text=help_str, widget=PluginSelectFieldWidget(options=param.options))
	    elif isinstance(param, parameters.SolrField):
                self.fields[key] = forms.CharField(required=required, help_text=help_str, 
                                                   widget=SolrFieldWidget(facet=param.facet,group=param.group, 
                                                                          multiple=param.multiple, predefined_facets=param.predefined_facets))
            elif param_subtype == int:
                self.fields[key] = forms.IntegerField(required=required, help_text=help_str)
            elif isinstance(param, parameters.File):
                self.fields[key] = forms.CharField(required=required, help_text=help_str, widget=PluginFileFieldWidget({}))
            else:
                self.fields[key] = forms.CharField(required=required, help_text=help_str)
            #s.write(self.displayInput(key, config_dict[key], tool.__parameters__.get_parameter(key)))
        

        
        
        