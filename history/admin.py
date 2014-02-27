from django.contrib import admin
from history.models import History
from django.contrib.auth.models import User
import logging
class HistoryAmdin(admin.ModelAdmin):
    
    list_display = ('id', 'timestamp', 'tool', 'uid_or_str','uid_email','status_name')
    search_fields = ['tool', 'uid']
    date_hierarchy = 'timestamp'
    search_fields=['uid__username','tool','id']

    def uid_email(self, instance):
	return instance.uid.email

    def uid_or_str(self,instance):
	try:
	   isinstance(instance.uid,User)
	   return instance.uid
	except:
	   return History.objects.values_list('uid',flat=True).filter(id=instance.id)[0]
	
admin.site.register(History, HistoryAmdin)
