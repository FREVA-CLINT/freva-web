from pathlib import Path

import django.contrib.auth as auth
import evaluation_system.api.parameters as parameters
from django import forms
from django.conf import settings
from django.core import exceptions
from django.forms.widgets import Input, TextInput
from django.template import loader
from evaluation_system.api import plugin_manager as pm
from evaluation_system.misc.utils import PrintableList

from plugins.utils import ssh_call


class PluginNotFoundError(Exception):
    pass


class PluginWeb(object):
    def __init__(self, plugin):
        self.name = plugin.__class__.__name__
        self.short_description = plugin.__class__.__short_description__

        try:
            self.long_description = plugin.__long_description__
        except AttributeError:
            self.long_description = plugin.__short_description__


class PluginFileFieldWidget(Input):
    def __init__(self, *args, **kwargs):
        self.file_extension = kwargs.pop("file_extension", None)
        super(PluginFileFieldWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None, **kwargs):
        if value is not None and type(value) == list:
            value = PrintableList(value)
        return loader.render_to_string(
            "plugins/filefield.html",
            {
                "name": name,
                "value": value,
                "id": attrs["id"],
                "attrs": attrs,
                "file_extension": self.file_extension,
            },
        )


class PluginSelectFieldWidget(Input):
    def __init__(self, *args, **kwargs):
        self.options = kwargs.pop("options")
        self.allow_user_input = kwargs.pop("allow_user_input", False)
        self.multiple = kwargs.pop("multiple", False)
        import operator

        self.sorted_options = sorted(
            self.options.items(), key=operator.itemgetter(1)
        )
        super(PluginSelectFieldWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        return loader.render_to_string(
            "plugins/selectfield.html",
            {
                "name": name,
                #"value": value,
                "value": ",".join(value) if isinstance(value, list) else value,
                "attrs": attrs,
                "options": self.sorted_options,
                "option_keys": list(map(str, self.options.keys())),
                "multiple": self.multiple,
                "allow_user_input": self.allow_user_input,
            },
        )


class SolrFieldWidget(Input):
    def __init__(self, *args, **kwargs):
        self.facet = kwargs.pop("facet")
        self.group = kwargs.pop("group")
        self.multiple = kwargs.pop("multiple")
        self.predefined_facets = kwargs.pop("predefined_facets")
        self.editable = kwargs.pop("editable")
        super(SolrFieldWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, choices=(), renderer=None):
        return loader.render_to_string(
            "plugins/solrfield.html",
            {
                "name": name,
                "value": ",".join(value) if isinstance(value, list) else value,
                "attrs": attrs,
                "facet": self.facet,
                "group": self.group,
                "multiple": self.multiple,
                "predefined_facets": self.predefined_facets,
                "editable": self.editable,
            },
        )


class PluginRangeFieldWidget(Input):
    def render(self, name, value, attrs=None, renderer=None):
        if value is not None and type(value) == list:
            value = PrintableList(value)
        return loader.render_to_string(
            "plugins/rangefield.html",
            {"name": name, "value": value, "id": attrs["id"], "attrs": attrs},
        )


class PasswordField(forms.CharField):
    def __init__(self, *args, **kwargs):
        widget = kwargs.get("widget", forms.HiddenInput)
        super(PasswordField, self).__init__(widget=widget)

        self._user = kwargs.pop("uid")

    def validate(self, value):
        password_type = getattr(settings, "FORM_PASSWORD_CHECK", "LDAP")
        if password_type == "LDAP":
            u = auth.authenticate(username=self._user, password=value)
            if u is None:
                raise exceptions.ValidationError(
                    "You've entered a wrong password!", code="invalid_password"
                )
        elif password_type == "ssh":
            try:
                ssh_call(self._user, value, "ls", settings.SCHEDULER_HOSTS)
            except:
                raise exceptions.ValidationError(
                    "You've entered a wrong password!", code="invalid_password"
                )
        super(PasswordField, self).validate(value)


class PluginForm(forms.Form):
    caption_standard_names = [
        "caption",
        "result_caption",
        "web_caption",
        "my_caption",
    ]

    def get_caption_field(self, tool):
        # the caption field should not have a fixed name
        self.caption_field_name = None
        criticalcaption = True
        captionindex = 0
        # modify the caption name if necessary
        while criticalcaption:
            # go through the list of standard names
            if captionindex < len(self.caption_standard_names):
                self.caption_field_name = self.caption_standard_names[
                    captionindex
                ]
                captionindex += 1
            else:
                self.caption_field_name = "_" + self.caption_field_name
            # check whether the caption name appear in the list of parameters
            criticalcaption = self.caption_field_name in tool.__parameters__

    def __init__(self, *args, **kwargs):
        tool = kwargs.pop("tool")
        uid = kwargs.pop("uid")
        self._workdir = Path(pm.config.get("base_dir_location"))

        super(PluginForm, self).__init__(*args, **kwargs)

        # set the password field
        self.fields["password_hidden"] = PasswordField(uid=uid)

        self.get_caption_field(tool)

        for key in tool.__parameters__:
            param = tool.__parameters__.get_parameter(key)
            param_subtype = param.base_type

            if param.mandatory:
                required = True
            else:
                required = False

            help_str = param.help
            help_str = "<br />".join(help_str.split("\n"))
            if isinstance(param, parameters.Bool):
                self.fields[key] = forms.BooleanField(
                    required=required,
                    help_text=help_str,
                    widget=forms.RadioSelect(
                        choices=(("False", "False"), ("True", "True"))
                    ),
                )
            elif isinstance(param, parameters.Range):
                self.fields[key] = forms.CharField(
                    required=required,
                    help_text=help_str,
                    widget=PluginRangeFieldWidget({}),
                )
            elif isinstance(param, parameters.SelectField):
                self.fields[key] = forms.CharField(
                    required=required,
                    help_text=help_str,
                    widget=PluginSelectFieldWidget(
                        options=param.options,
                        multiple=getattr(param, "multiple", False),
                        allow_user_input=getattr(param, "allow_user_input", False),
                    ),
                )
            elif isinstance(param, parameters.SolrField):
                self.fields[key] = forms.CharField(
                    required=required,
                    help_text=help_str,
                    widget=SolrFieldWidget(
                        facet=param.facet,
                        group=param.group,
                        editable=param.editable,
                        multiple=param.multiple,
                        predefined_facets=param.predefined_facets,
                    ),
                )
            elif param_subtype == int:
                self.fields[key] = forms.IntegerField(
                    required=required, help_text=help_str
                )
            elif param_subtype == float:
                self.fields[key] = forms.FloatField(
                    required=required, help_text=help_str
                )
            elif isinstance(param, parameters.File):
                self.fields[key] = forms.CharField(
                    required=required,
                    help_text=help_str,
                    widget=PluginFileFieldWidget(
                        file_extension=param.file_extension
                    ),
                )
            else:
                self.fields[key] = forms.CharField(
                    required=required, help_text=help_str
                )

        # Add the caption field, now
        help_str = "An additional caption to be displayed with the results."
        if self.caption_field_name != self.caption_standard_names[0]:
            help_str += (
                " Other tools name this field "
                + self.caption_standard_names[0]
                + ", this might be confusing."
            )
        self.fields[self.caption_field_name] = forms.CharField(
            required=False, help_text=help_str
        )

        # add the "unique_output" field
        self.fields["unique_output_id"] = forms.BooleanField(
            required=False,
            help_text="If true append the freva run id to every output folder",
            widget=forms.RadioSelect(
                choices=(("False", "False"), ("True", "True"))
            ),
            initial=True,
        )
