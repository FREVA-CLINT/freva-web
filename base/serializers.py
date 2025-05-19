from django.contrib.auth.models import User
from rest_framework import serializers

from django_evaluation.settings.local import HOME_DIRS_AVAILABLE


class UserSerializer(serializers.ModelSerializer):
    home = serializers.SerializerMethodField()
    scratch = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "home",
            "scratch",
        )

    def get_home(self, instance):
        _user = self.context.get("user")
        return _user.getUserHome()

    def get_scratch(self, instance):
        _user = self.context.get("user")
        if _user:
            return _user.getUserScratch()
        return None
