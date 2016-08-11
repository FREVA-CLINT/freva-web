from django.contrib import admin
from plugins.models import ToolPullRequest


class ToolPullRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'tool', 'tagged_version', 'user', 'status')

admin.site.register(ToolPullRequest, ToolPullRequestAdmin)

