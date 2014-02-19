from django.contrib import admin
from history.models import History

class HistoryAmdin(admin.ModelAdmin):
    
    list_display = ('id', 'timestamp', 'tool', 'uid')
    search_fields = ['tool', 'uid']
    date_hierarchy = 'timestamp'

admin.site.register(History, HistoryAmdin)
