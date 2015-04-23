from django.contrib import admin
from solr.models import UserCrawl

class UserCrawlAdmin(admin.ModelAdmin):
    list_display = ('id','created','user','status')

admin.site.register(UserCrawl,UserCrawlAdmin)

