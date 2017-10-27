from django.contrib import admin
from .models import HindcastEvaluation


class HindcastEvaluationAdmin(admin.ModelAdmin):
    list_display = ('id',)

admin.site.register(HindcastEvaluation, HindcastEvaluationAdmin)
