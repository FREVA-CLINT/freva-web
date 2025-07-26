"""middleware for handling OAuth2 token refresh and plugin reloading."""

import logging
import time

import requests
from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from evaluation_system.api import plugin_manager as pm

from base.views import TOKEN_URL

logger = logging.getLogger(__name__)


class OIDCTokenRefreshMiddleware:
    """
    Middleware to refresh OAuth2 tokens only when necessary.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # TODO: we can define these variables in the Django settings.py file
        # to allow customization of the refresh buffer and cooldown
        # but for now we use hardcoded values
        self.refresh_buffer = getattr(settings, 'TOKEN_REFRESH_BUFFER', 120)
        self.refresh_cooldown = getattr(settings, 'TOKEN_REFRESH_COOLDOWN', 30)

    def __call__(self, request):
        # when user hits the following paths, we skip the token refresh logic
        skip_paths = ['/login/', '/callback', '/logout/', '/admin/', '/refresh-token/', '/freva.css', '/static/', '/media/']
        if any(request.path.startswith(path) for path in skip_paths):
            return self.get_response(request)

        # Check if user is authenticated and has tokens in session
        if (request.user.is_authenticated and 
            'access_token' in request.session and 
            'refresh_token' in request.session):

            # Only check token expiry, don't refresh immediately
            if self._is_token_expired_or_expiring_soon(request):
                # Check if we recently attempted a refresh
                if not self._is_refresh_on_cooldown(request):
                    if not self._refresh_token(request):
                        # Refresh failed, logout user and redirect to login
                        logger.warning(f"Token refresh failed for user {request.user.username}, logging out")
                        logout(request)
                        return HttpResponseRedirect("/")

        return self.get_response(request)

    def _is_token_expired_or_expiring_soon(self, request):
        """
        Check if token is expired or will expire very soon.
        It only returns True when refresh is really needed.
        """
        token_expires = request.session.get('token_expires')
        if not token_expires:
            return True

        current_time = int(time.time())
        time_until_expiry = token_expires - current_time

        # Only refresh if token expires within buffer time cooldown
        return time_until_expiry <= self.refresh_buffer

    def _is_refresh_on_cooldown(self, request):
        """
        Check if we recently attempted a token refresh.
        Prevents rapid successive refresh attempts.
        """
        last_refresh_attempt = request.session.get('last_refresh_attempt', 0)
        current_time = int(time.time())

        # it returns True if we're still in cooldown period
        return (current_time - last_refresh_attempt) < self.refresh_cooldown

    def _refresh_token(self, request):
        """
        Refresh the access token using the refresh token.
        Returns True if refresh was successful, False otherwise.
        """
        refresh_token = request.session.get('refresh_token')
        if not refresh_token:
            logger.error("No refresh token available for token refresh")
            return False

        # Check if refresh token itself is expired
        refresh_expires = request.session.get('refresh_expires')
        if refresh_expires and int(time.time()) >= refresh_expires:
            logger.error("Refresh token expired")
            return False

        # store refresh attempt time
        request.session['last_refresh_attempt'] = int(time.time())
        request.session.modified = True

        # Prevent concurrent refresh attempts for the same session
        refresh_key = f"refreshing_token_{request.session.session_key}"
        if request.session.get(refresh_key):
            time.sleep(0.1)  # small wait for concurrent refresh
            return request.session.get('access_token') is not None

        try:
            # !Mark that we're refreshing to prevent concurrent attempts
            request.session[refresh_key] = True
            request.session.modified = True

            data = {
                'refresh-token': refresh_token
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            logger.info(f"Refreshing token for user {request.user.username}")
            response = requests.post(TOKEN_URL, headers=headers, data=data, timeout=10)

            if response.status_code == 200:
                token_data = response.json()
                request.session['access_token'] = token_data['access_token']
                request.session['refresh_token'] = token_data['refresh_token']
                request.session['token_expires'] = token_data['expires']
                request.session['refresh_expires'] = token_data['refresh_expires']

                # Clear the last refresh attempt time on success
                request.session.pop('last_refresh_attempt', None)

                logger.info(f"Token refreshed successfully for user {request.user.username}")
                return True
            else:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.exception(f"Token refresh error for user {request.user.username}: {e}")
            return False
        finally:
            # pop the refresh lock
            request.session.pop(refresh_key, None)
            request.session.modified = True


class ReloadPluginsMiddleware:
    """
    Middleware to reload plugins for each authenticated user request.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                pm.reload_plugins(request.user.username)
            except Exception as e:
                logger.warning(f"Failed to reload plugins for user {request.user.username}: {e}")
        response = self.get_response(request)
        return response
