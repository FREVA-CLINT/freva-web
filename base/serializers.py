from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    scratch = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "scratch",
        )

    def get_scratch(self, instance):
        """Get user scratch directory."""
        _user = self.context.get("user")
        if _user:
            return _user.getUserScratch()
        return None
