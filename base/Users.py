import pwd
from configparser import ConfigParser as Config
from configparser import ExtendedInterpolation
from typing import NamedTuple

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from evaluation_system.misc import config
from evaluation_system.model.db import UserDB
from evaluation_system.model.user import User

from base.exceptions import UserNotFoundError


class UserData(NamedTuple):
    """A class the defines pwd's entries."""

    pw_name: str
    pw_gecos: str
    pw_dir: str = "N/A"
    pw_uid: int = 1000
    pw_gid: int = 1001
    pw_shell: str = "/bin/bash"
    pw_passwd: str = "x"


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
        if request and hasattr(request, "session"):
            user_info = request.session.get("user_info", {})
            self._email = user_info.get("email", _user.email)
        else:
            self._email = _user.email
        self._userconfig = Config(interpolation=ExtendedInterpolation())
        self._userconfig.read([User.EVAL_SYS_DEFAULT_CONFIG])
        self._db = UserDB(self)

        row_id = self._db.getUserId(self.getName())
        if row_id:
            self._db.updateUserLogin(row_id, self._email)
        else:
            self._db.createUser(self.getName(), email=self._email)
        try:
            self._userdata = pwd.getpwnam(username)
        except KeyError:
            self._userdata = UserData(pw_name=username, pw_gecos=username)

    def getName(self):
        return self._username

    def getUserId(self):
        return self._uid

    def getEmail(self):
        return self._email

    def __str__(self):
        return f"User: {self._username} Mail: {self._email}"
