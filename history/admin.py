from django.contrib import admin
from history.models import History, Configuration
from django.contrib.auth.models import User
from django.utils.html import format_html


class HistoryAmdin(admin.ModelAdmin):

    list_display = (
        "id",
        "timestamp",
        "tool",
        "uid_or_str",
        "uid_email",
        "user_name",
        "link_to_model",
        "status_name",
        "started_from_website",
    )
    search_fields = ["tool", "uid"]
    date_hierarchy = "timestamp"
    search_fields = ["uid__username", "tool", "id"]

    def uid_email(self, instance):
        return instance.uid.email

    def link_to_model(self, instance):
        return format_html(
            f'<a href="/history/{instance.id}/results/" target="_blank">Show Results</a>'
        )

    link_to_model.allow_tags = True

    def user_name(self, instance):
        return instance.uid.first_name + " " + instance.uid.last_name

    def started_from_website(self, instance):
        if instance.slurm_output == "0":
            return False
        else:
            return True

    started_from_website.boolean = True

    def uid_or_str(self, instance):
        try:
            isinstance(instance.uid, User)
            return instance.uid
        except:
            return History.objects.values_list("uid", flat=True).filter(id=instance.id)[
                0
            ]


class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ("value",)


admin.site.register(History, HistoryAmdin)
admin.site.register(Configuration, ConfigurationAdmin)
