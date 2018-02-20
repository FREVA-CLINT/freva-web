from django.contrib import admin
from externaluser.models import ExternalUser


class ExternalUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'status_changed', 'status')


admin.site.register(ExternalUser, ExternalUserAdmin)
