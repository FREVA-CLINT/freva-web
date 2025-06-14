import os
from configparser import ConfigParser as Config
from configparser import ExtendedInterpolation

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from evaluation_system.misc import config
from evaluation_system.model.db import UserDB
from evaluation_system.model.user import User

from base.exceptions import UserNotFoundError


class OpenIdUser(User):
    """Get user information from session data"""

    def __init__(self, username: str, request=None):
        try:
            _user_model = get_user_model()
            _user = _user_model.objects.get(username=username)
        except ObjectDoesNotExist as error:
            raise UserNotFoundError() from error
        self._dir_type = config.get(config.DIRECTORY_STRUCTURE_TYPE)
        self._username = username
        self._uid = "web"
        # we use the email from the session if available, 
        # otherwise from the user model
        if request and hasattr(request, 'session'):
            user_info = request.session.get('user_info', {})
            self._email = user_info.get('email', _user.email)
        else:
            self._email = _user.email
            
        self._home_directory = "NA"
        self._userconfig = Config(interpolation=ExtendedInterpolation())
        self._userconfig.read([User.EVAL_SYS_DEFAULT_CONFIG])
        self._db = UserDB(self)

        row_id = self._db.getUserId(self.getName())
        if row_id:
            self._db.updateUserLogin(row_id, self._email)
        else:
            self._db.createUser(self.getName(), email=self._email)

    def getName(self):
        return self._username

    def getUserId(self):
        return self._uid

    def getUserHome(self):
        return self._home_directory

    def getEmail(self):
        return self._email

    def __str__(self):
        return (
            f"User: {self._username} Mail: {self._email} Home: {self._home_directory}"
        )
