"""
This is your project's main settings file that can be committed to your
repo. If you need to override a setting locally, use local.py
"""

import logging
import os

import django.utils

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy


def get_env_setting(setting):
    """Get the environment setting or return exception"""
    try:
        return os.environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)


LOGIN_URL = "/?login_required=1"

# temporary directory for tailed scheduler files
TAIL_TMP_DIR = "/tmp/tail_offset/"

# Your project root
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__) + "../../../")
SUPPORTED_NONLOCALES = ["media", "admin", "static"]

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

SITE_ID = 1

# Defines the views served for root URLs.
ROOT_URLCONF = "django_evaluation.urls"

# Application definition
INSTALLED_APPS = (
    # Django contrib apps
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.humanize",
    "django.contrib.syndication",
    "django.contrib.staticfiles",
    "django.contrib.flatpages",
    # Third-party apps, patches, fixes
    "debug_toolbar",
    "compressor",
    "bootstrap5",
    "datatableview",
    "webpack_loader",
    "rest_framework",
    "debug_toolbar_user_panel",
    "base",
    "plugins",
    "history",
    "solr",
)

# Place bcrypt first in the list, so it will be the default password hashing
# mechanism
PASSWORD_HASHERS = (
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.SHA1PasswordHasher",
    "django.contrib.auth.hashers.MD5PasswordHasher",
    "django.contrib.auth.hashers.CryptPasswordHasher",
)

# Sessions
#
# By default, be at least somewhat secure with our session cookies.
SESSION_COOKIE_HTTPONLY = True

# Set this to true if you are using https
SESSION_COOKIE_SECURE = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.example.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.example.com/media/", "http://example.com/media/"
MEDIA_URL = "/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "static")

# URL prefix for static files.
# Example: "http://media.example.com/static/"
STATIC_URL = "/static/"

# URL for preview files
PREVIEW_URL = STATIC_URL + "preview/"

# Additional locations of static files
STATICFILES_DIRS = [
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, "static"),
    os.path.join(PROJECT_ROOT, "assets"),
]


# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "UTC"
# TIME_ZONE = 'Europe/Berlin'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
    "django_evaluation.middelwares.ReloadPluginsMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    'django_evaluation.middelwares.OIDCTokenRefreshMiddleware',
]


TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, "templates"),
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
    "django.template.backends.django.DjangoTemplates",
)

# Allow default field to be auto added by django
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(PROJECT_ROOT, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.template.context_processors.static",
                "django.template.context_processors.csrf",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    },
]
# DEBUG_TOOLBAR_PATCH_SETTINGS = False


def custom_show_toolbar(request):
    """Only show the debug toolbar to users with the superuser flag."""
    return False  # request.user.is_superuser


FILE_UPLOAD_PERMISSIONS = 0o664

# The WSGI Application to use for runserver
WSGI_APPLICATION = "django_evaluation.wsgi.application"

INTERNAL_IPS = ["127.0.0.1"]

SYSTEM_EMAIL_PREFIX = "[django_evaluation]"

## Log settings

LOG_LEVEL = logging.INFO
HAS_SYSLOG = True
SYSLOG_TAG = "http_app_django_evaluation"  # Make this unique to your project.

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

DEBUG = TEMPLATE_DEBUG = True
DEV = True

# SECURITY WARNING: keep the secret key used in production secret!
# Hardcoded values can leak through source control. Consider loading
# the secret key from an environment variable or a file instead.
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "hj1bkzobng0ck@0&%t509*1ki$#)i5y+i0)&=7zv@amu8pm5*t"
)


# filter for user numbers
USERNAME_FILTER = r"^[a-z]\d{6}$"
USERNAME_REPLACE = "*****"

# Django rest framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication"
    ],
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

MENU_ENTRIES = [
    {
        "name": "Plugins",
        "url": reverse_lazy("plugins:home"),
        "html_id": "plugin_menu",
    },
    {
        "name": "History",
        "url": reverse_lazy("history:history"),
        "html_id": "history_menu",
    },
    {
        "name": "Data-Browser",
        "url": reverse_lazy("solr:data_browser"),
        "html_id": "browser_menu",
    },
    {"name": "Help", "url": reverse_lazy("plugins:about"), "html_id": "doc_menu"},
    {
        "name": "Contact",
        "url": reverse_lazy("base:contact"),
        "html_id": "contact_menu",
    },
]
