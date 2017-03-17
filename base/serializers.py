from rest_framework import serializers
from django.contrib.auth.models import User
import pwd
from evaluation_system.misc import config


class UserSerializer(serializers.ModelSerializer):
    home = serializers.SerializerMethodField()
    scratch = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'isGuest', 'home', 'scratch')

    def get_home(self, instance):
        if instance.username == 'guest':
            return 'Guest has no home'
        return pwd.getpwnam(instance.username).pw_dir

    def get_scratch(self, instance):
        return config.get('scratch_dir').replace('$USER', instance.username)