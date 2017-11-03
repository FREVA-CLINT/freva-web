from django.contrib import admin
from .models import HindcastEvaluation


class HindcastEvaluationAdmin(admin.ModelAdmin):
    list_display = ('variable', 'hindcast_set', 'reference', 'region', 'score', 'map', 'fieldmean')

    def map(self, instance):
        return instance.path_map is not None

    def fieldmean(self, instance):
        return instance.path_fieldmean is not None

    map.boolean = True
    map.admin_order_field = 'path_map'
    fieldmean.boolean = True
    fieldmean.admin_order_field = 'path_fieldmean'
    search_fields = ['variable', 'hindcast_set', 'reference', 'region', 'score']
    list_filter = ['variable', 'hindcast_set', 'reference', 'region', 'score']

admin.site.register(HindcastEvaluation, HindcastEvaluationAdmin)
