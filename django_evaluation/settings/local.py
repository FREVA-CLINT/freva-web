"""This is the 2nd configuration file for the web app.

Since the web app is meant to be run in a container most of its config
is passed by environment variables. Here is a list of variables that are
evaluated:

EVALUATION_SYSTEM_CONFIG_FILE : str
FREVA_WEB_CONFIG_FILE : str
DEV_MODE : 0|1
PROJECT_ROOT : str
FREVA_REST_URL : str
SCHEDULER_HOST : str
REDIS_HOST : str
REDIS_PORT : str
SERVER_EMAIL : str
ALLOWED_HOSTS : str
CSRF_TRUSTED_ORIGINS : str
FREVA_BIN: str
"""

import logging
import os
import shutil
import sys
from pathlib import Path

import requests
import toml
from django.urls import reverse_lazy
from evaluation_system.misc import config

logger_format = logging.Formatter(
    "%(name)s - %(asctime)s - %(levelname)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

logging.basicConfig(
    format="%(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("freva-web")


freva_share_path = Path(os.environ["EVALUATION_SYSTEM_CONFIG_FILE"]).parent
web_config_path = Path(
    os.environ.get(
        "FREVA_WEB_CONFIG_FILE",
        freva_share_path / "web" / "freva_web_conf.toml",
    )
)


def _get_conf_key(cfg, key, alternative, is_file=True):
    """Check config of freva_web config."""
    if not is_file:
        return cfg.get(key) or alternative
    value = Path(cfg.get(key, alternative))
    if value.exists():
        return value
    return Path(alternative)


def _get_logo(logo_file, project_root):
    static_folder = Path(project_root) / "static"
    if (
        not logo_file
        or not Path(logo_file).exists()
        or not (static_folder / "img").exists()
    ):
        return "/static/img/thumb-placeholder.png"
    logo_file = Path(logo_file)
    new_file = static_folder / "img" / logo_file.name
    if new_file.exists():
        return f"/static/img/{logo_file.name}"
    shutil.copy(logo_file, new_file)
    return f"/static/img/{logo_file.name}"


def _read_secret(port: int = 5002, key: str = "email") -> dict[str, str]:
    """Read the key-value pair secrets from vault server."""
    sha = config._get_public_key(config.get("project_name"))
    uri = f"http://{config.get('db.host')}:{port}/vault/{key}/{sha}"
    try:
        res = requests.get(uri, timeout=5)
        res.raise_for_status()
        req = res.json()
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.HTTPError,
    ) as error:
        logger.warning("Could not read secrets from vault: %s", error)
        req = {}
    return req


def _set_favicon(html_color: str, project_root: Path) -> None:
    img_folder = Path(project_root) / "static" / "img"
    tmpl_folder = Path(project_root) / "static_root" / "img"
    svg_tmpl = tmpl_folder / "favicon-tmpl.svg"
    favicon = img_folder / "favicon.svg"
    with svg_tmpl.open() as f_obj:
        new_svg = f_obj.read().replace(
            'style="fill:#000000"', f'style="fill:{html_color}"'
        )
    try:
        favicon.parent.mkdir(exist_ok=True, parents=True)
        with favicon.open("w") as f_obj:
            f_obj.write(new_svg)
    except PermissionError as error:
        logger.error("Could not create static folder: %s", error)


try:
    web_config = toml.loads(web_config_path.read_text())
except FileNotFoundError:
    web_config = {}
# SECURITY WARNING: don't run with debug turned on in production!
# Set this to 0 on all server instances and True only for development.
DEV = DEBUG = TEMPLATE_DEBUG = bool(int(os.environ.get("DEV_MODE", 0)))
PROJECT_ROOT = os.environ.get("PROJECT_ROOT", None) or str(
    Path(__file__).absolute().parents[2]
)
STATIC_URL = "/static/"
if not DEV:
    STATIC_ROOT = str(Path(PROJECT_ROOT) / "static")

INSTITUTION_LOGO = _get_logo(web_config.get("institution_logo", ""), PROJECT_ROOT)
FREVA_LOGO = f"{STATIC_URL}img/by_freva_transparent.png"
MAIN_COLOR = _get_conf_key(web_config, "main_color", "Tomato", False)
_set_favicon(MAIN_COLOR, Path(PROJECT_ROOT))
BORDER_COLOR = _get_conf_key(web_config, "border_color", "#6c2e1f", False)
HOVER_COLOR = _get_conf_key(web_config, "hover_color", "#d0513a", False)
HOMEPAGE_TEXT = web_config.get("homepage_text") or (
    "Lorem ipsum dolor sit amet"
    ", consectetur adipiscing elit"
    ", sed do eiusmod tempor incididunt ut"
    "labore et dolore magna aliqua. Ut enim"
    "ad minim veniam, quis nostrud exercitation"
    "ullamco laboris nisi ut aliquip ex ea commodo"
    "consequat. Duis aute irure dolor in reprehenderit"
    "in voluptate velit esse cillum dolore eu fugiat"
    "nulla pariatur. Excepteur sint occaecat cupidatat"
    "non proident, sunt in culpa qui officia deserunt"
    "mollit anim id est laborum."
)
IMPRINT = web_config.get("imprint") or [
    "ANAIS - RegIKlim",
    "German Climate Computing Center (DKRZ)",
    "Bundesstr. 45a",
    "20146 Hamburg",
    "Germany",
]
HOMEPAGE_HEADING = web_config.get("homepage_heading") or "Lorem ipsum dolor."
ABOUT_US_TEXT = web_config.get("about_us_text") or "Hello world, this is freva."
CONTACTS = web_config.get("contacts") or ["freva@dkrz.de"]
if isinstance(CONTACTS, str):
    CONTACTS = [c for c in CONTACTS.split(",") if c.strip()]
##########
# Here you can customize the footer and texts on the startpage
##########
INSTITUTION_NAME = web_config.get("insitution_name") or "Freva"
##################################################
# the host to start the scheduler
SCHEDULER_HOSTS = [
    h.strip()
    for h in os.environ.get("SCHEDULER_HOST", "levante.dkrz.de").split(",")
    if h.strip()
]

# The url of the freva-rest api
FREVA_REST_URL = os.getenv("FREVA_REST_URL", "http://localhost:7777")

# temporary directory for tailed scheduler files
TAIL_TMP_DIR = "/tmp/tail/"
# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    os.path.join(PROJECT_ROOT, "static_root"),
    ("assets/bundles", os.path.join(PROJECT_ROOT, "assets", "bundles")),
)
# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django.contrib.staticfiles.finders.DefaultStorageFinder",
)
config.reloadConfiguration()
db_name = config.get("db.db")
db_user = config.get("db.user")
db_password = config.get("db.passwd")
db_host = config.get("db.host")
db_port = config.get("db.port")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": db_name,
        "USER": db_user,
        "PASSWORD": db_password,  #'miklip',
        "HOST": db_host,  #'wwwdev-miklip',
        "PORT": db_port,
        "OPTIONS": {"charset": "utf8mb4"},
    },
}
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "django_evaluation.auth.OIDCAuthorizationCodeBackend",
)
### Caching stuff
REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_USER = os.environ.get("REDIS_USER")
REDIS_PASSWD = os.environ.get("REDIS_PASSWD")
REDIS_SSL_CERTFILE = os.environ.get("REDIS_SSL_CERTFILE")
REDIS_SSL_KEYFILE = os.environ.get("REDIS_SSL_KEYFILE")

redis_options = {}
if REDIS_SSL_CERTFILE:
    schema = "rediss"
    redis_options["ssl_certfile"] = REDIS_SSL_CERTFILE
    redis_options["ssl_ca_certs"] = REDIS_SSL_CERTFILE
else:
    schema = "redis"

if REDIS_SSL_KEYFILE:
    redis_options["ssl_keyfile"] = REDIS_SSL_KEYFILE

if REDIS_USER:
    redis_options["username"] = REDIS_USER
if REDIS_PASSWD:
    redis_options["password"] = REDIS_PASSWD

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"{schema}://{REDIS_HOST}:{REDIS_PORT}/9",
        "OPTIONS": redis_options,
    },
}

DATA_BROWSER_HOST = os.environ.get("FREVA_REST_URL", "http://localhost:7777")

SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "freva@dkrz.de")
DEFAULT_FROM_EMAIL = SERVER_EMAIL

EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

# Provide a full list of all valid hosts (including the http(s):// prefix) which are expected
CSRF_TRUSTED_ORIGINS = [
    h.strip()
    for h in os.environ.get("CSRF_TRUSTED_ORIGINS", "http://localhost").split(",")
    if h.strip()
]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
FORM_PASSWORD_CHECK="OIDC"  # OIDC or ssh
# path to the site packages used:
VENV_PYTHON_DIR = "/usr/bin/python3"
# Path to miklip-logo
MIKLIP_LOGO = STATIC_URL + "img/miklip-logo.png"
LOAD_MODULE = " "
FREVA_BIN = os.environ.get("FREVA_BIN", os.path.join(sys.exec_prefix, "bin"))
NCDUMP_BINARY = os.path.join(FREVA_BIN, "metadata-inspector") + " --html"

SHELL_IN_A_BOX = "/shell/"
WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "assets/bundles",
        "STATS_FILE": PROJECT_ROOT + "/webpack-stats.json",
    }
}
RESULT_BROWSER_FACETS = [
    "plugin",
    "project",
    "product",
    "institute",
    "model",
    "experiment",
    "time_frequency",
    "variable",
]
MENU_ENTRIES = []

CHAT_BOT_URL = "http://vader4-icpub.lvt.dkrz.de:8502"
CHAT_BOT_AUTH_KEY = os.environ.get("CHAT_BOT_AUTH_KEY")
CHAT_BOT_FREVA_CONFIG = os.environ.get("CHAT_BOT_FREVA_CONFIG")
### CHATBOT development settings
# Since the backend of chatbot is running on an operational system
# it is necessary to pass some configuration from a non-localhost
# and accessible freva instance to the chatbot backend.
# For example we can catch the project name and vault url
# and freva_rest and freva_config from the environment variables
VAULT_URL = os.environ.get("VAULT_URL")
CHAT_BOT_FREVA_PROJECT = os.environ.get("CHAT_BOT_FREVA_PROJECT")
##################################
if os.getenv("CHAT_BOT", "0").isdigit():
    ACTIVATE_CHAT_BOT = bool(int(os.getenv("CHAT_BOT", "0")))
else:
    ACTIVATE_CHAT_BOT = False

# Sometimes it is desired to put a link into the navbar which does not correspond
# to a template inside django. If something like this is needed, put a slash as a
# prefix to your relative url (the second value in each of the lists), e.g. "/impressum"
_MENU_ENTRIES = [
    ["Data-Browser", "solr:data_browser", "browser_menu"],
    ["Plugins", "plugins:home", "plugin_menu"],
    ["History", "history:history", "history_menu"],
    ["Result-Browser", "history:result_browser", "result_browser_menu"],
]

for title, url, html_id in web_config.get("menu_entries", []) or _MENU_ENTRIES:
    if url.startswith("/"):
        MENU_ENTRIES.append({"name": title, "url": url, "html_id": html_id})
    else:
        MENU_ENTRIES.append(
            {"name": title, "url": reverse_lazy(url), "html_id": html_id}
        )

if ACTIVATE_CHAT_BOT:
    MENU_ENTRIES.append(
        {
            "name": "FrevaGPT",
            "url": reverse_lazy("bot:chatbot"),
            "html_id": "chatbot_menu",
        }
    )
