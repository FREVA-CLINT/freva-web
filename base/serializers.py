from django.contrib.auth.models import User
from rest_framework import serializers

from django_evaluation.settings.local import HOME_DIRS_AVAILABLE


class UserSerializer(serializers.ModelSerializer):
    home = serializers.SerializerMethodField()
    scratch = serializers.SerializerMethodField()
    isGuest = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "isGuest",
            "home",
            "scratch",
        )

    def get_isGuest(self, instance):
        """Get guest status from session data."""
        request = self.context.get("request")
        if request and hasattr(request, 'session'):
            user_info = request.session.get('user_info', {})
            return user_info.get('is_guest', False)
        return False

    def get_home(self, instance):
        """Get user home directory."""
        request = self.context.get("request")
        if request and hasattr(request, 'session'):
            user_info = request.session.get('user_info', {})
            if user_info.get('is_guest', False):
                return None
        if not HOME_DIRS_AVAILABLE:
            return None
        _user = self.context.get("user")
        if _user:
            return _user.getUserHome()
        return None

    def get_scratch(self, instance):
        """Get user scratch directory."""
        _user = self.context.get("user")
        if _user:
            return _user.getUserScratch()
        return None
