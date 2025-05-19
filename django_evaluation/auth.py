import functools
import logging
import time

import requests
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

logger = logging.getLogger(__name__)


# The following decorator is the replacement for the login_required decorator
# from django.contrib.auth.decorators. We need this for OIDC token handling
def oidc_token_required(view_func):
    """
    Decorator to gurantee the user has a valid OIDC access token.
    If not, redirects to OIDC authentication flow to obtain one.
    """

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            next_url = request.get_full_path()
            return HttpResponseRedirect(f"/?login_required=1&next={next_url}")
        OIDC_VERIFY_SSL = settings.OIDC_VERIFY_SSL
        access_token = request.session.get("oidc_access_token")
        if not access_token:
            request.session["oidc_login_next"] = request.get_full_path()
            request.session.save()
            return HttpResponseRedirect(reverse("oidc_authentication_init"))

        token_expiry = request.session.get("oidc_token_expiry", 0)
        current_time = int(time.time())
        time_remaining = token_expiry - current_time
        needs_refresh = time_remaining < 30  # 30 seconds buffer
        if needs_refresh:
            # Basically since mozilla_django_oidc does not support
            # refresh tokens, we need to do the prcedure manually
            # in our codeabse
            refresh_token = request.session.get("oidc_refresh_token")
            if refresh_token:
                try:
                    request.session["oidc_login_next"] = request.get_full_path()
                    request.session.save()
                    token_url = settings.OIDC_OP_TOKEN_ENDPOINT
                    data = {
                        "client_id": settings.OIDC_RP_CLIENT_ID,
                        "client_secret": settings.OIDC_RP_CLIENT_SECRET,
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                    }

                    response = requests.post(token_url, data=data, verify=OIDC_VERIFY_SSL)
                    if response.status_code == 200:
                        # Update tokens in session
                        token_info = response.json()
                        request.session["oidc_access_token"] = token_info[
                            "access_token"
                        ]
                        request.session["oidc_id_token"] = token_info.get("id_token")
                        request.session["oidc_refresh_token"] = token_info.get(
                            "refresh_token"
                        )
                        if "expires_in" in token_info:
                            request.session["oidc_token_expiry"] = (
                                current_time + token_info["expires_in"]
                            )
                    else:
                        return redirect("oidc_authentication_init")
                except Exception as e:
                    logger.error(f"Token refresh failed: {e}")
                    return redirect("oidc_authentication_init")
            else:
                request.session["oidc_login_next"] = request.get_full_path()
                request.session.save()
                return redirect("oidc_authentication_init")
        return view_func(request, *args, **kwargs)

    return wrapper


def get_auth_header(request):
    """
    Get the authorization header for API requests.
    """
    access_token = request.session.get("oidc_access_token")
    if access_token:
        return {"Authorization": f"Bearer {access_token}"}
    return {}


class CustomOIDCBackend(OIDCAuthenticationBackend):
    """
    A light wrapper around the OIDCAuthenticationBackend to add
    custom functionality for our application.

    1. Use preferred_username or fall back to sub
    2. Map OIDC claims into Django User fields
    3. Store refresh_token in session (mozilla_django_oidc does not do this)
    """

    def get_username(self, claims):
        """without this replacemnet funcm,the username
        is set to the sub claim"""
        return claims.get("preferred_username") or claims.get("sub")

    def create_user(self, claims):
        """Create a new user with the given claims from
        the OIDC provider."""
        
        user = super().create_user(claims)
        print(f"Creating user with claims: {claims} {user.__dict__ }")
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        user.home = claims.get("home", "")
        self.request.session['user_home_dir'] = claims.get("home", "")
        user.save()

        return user

    def update_user(self, user, claims):
        """Update the user with the given claims from
        the OIDC provider."""
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        user.home = claims.get("home", "")        
        self.request.session['user_home_dir'] = claims.get("home", "")
        user.save()
        return user

    def get_token(self, payload):
        """
        Exchange code<->tokens with the OP, then persist the refresh_token.
        """
        token_info = super().get_token(payload)
        refresh = token_info.get("refresh_token")
        if refresh:
            self.request.session["oidc_refresh_token"] = refresh
            self.request.session.save()
        else:
            logger.warning("No refresh_token returned; check your scopes/settings")
        return token_info
