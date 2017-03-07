from rest_framework import serializers
from django.contrib.flatpages.models import FlatPage


class PluginSerializer(serializers.Serializer):

    name = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    long_description = serializers.SerializerMethodField()
    tool_developer = serializers.DictField()
    docpage = serializers.SerializerMethodField()

    def get_name(self, plugin):
        return plugin.__class__.__name__

    def get_short_description(self, plugin):
        return plugin.__class__.__short_description__

    def get_long_description(self, plugin):
        try:
            return plugin.__long_description__
        except AttributeError:
            return plugin.__short_description__

    def get_docpage(self, plugin):
        try:
            docu_flatpage = FlatPage.objects.get(title__iexact=plugin.__class__.__name__)
            return docu_flatpage.url
        except FlatPage.DoesNotExist:
            return None
