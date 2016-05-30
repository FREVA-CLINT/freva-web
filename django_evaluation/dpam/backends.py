import pam

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
import grp
from django.contrib.auth.models import Group
import pwd


class PAMBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        service = getattr(settings, 'PAM_SERVICE', 'login')
        if not pam.authenticate(username, password, service=service):
            return None
        # check if user is in right group
        allowed_group = getattr(settings, 'ALLOWED_GROUP', None)
        if allowed_group:
            groups = [g.gr_name for g in grp.getgrall() if username in g.gr_mem]
            if allowed_group not in groups:
                return None
        try:
            user = User.objects.get(username=username)
        except:
            if not getattr(settings, "PAM_CREATE_USER", True):
                return None
            pwd_info = pwd.getpwnam(username)
            name = pwd_info.pw_gecos.split(' ')
            user = User(username=username, password='not stored here',
                        first_name=name[0], last_name=name[1])
            user.set_unusable_password()

            if getattr(settings, 'PAM_IS_SUPERUSER', False):
              user.is_superuser = True

            if getattr(settings, 'PAM_IS_STAFF', user.is_superuser):
              user.is_staff = True

            user.save()

            #add user to freva group
            g = Group.objects.get(name=allowed_group) 
            g.user_set.add(user)
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
