"""Backend for the OIDC Server."""

import os
from typing import Any, Optional

import jwt
import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend


class OIDCPasswordBackend(BaseBackend):
    """
    Custom authentication backend to authenticate users via JWT tokens.

    This backend handles the authentication by sending a request to an
    authentication server to obtain a JWT token. It then extracts user
    information from the token and creates or retrieves a user in the Django
    database.
    """

    def authenticate(
        self, request: Any, username=Optional[str], password=Optional[str]
    ):
        """
        Authenticate a user by obtaining a JWT token and extracting user
        information.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object.
        username : Optional[str], optional
            The username of the user. Defaults to None.
        password : Optional[str], optional
            The password of the user. Defaults to None.

        Returns
        -------
        Optional[User]: The authenticated user instance if authentication is
                        successful, otherwise None.
        """
        api_url = os.getenv("FREVA_REST_URL", "http://localhost:7777")
        token_url = f"{api_url.rstrip('/')}/api/auth/v2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "password",
            "username": username,
            "password": password,
        }
        response = requests.post(
            token_url, headers=headers, data=data, timeout=3
        )
        uid_field = os.getenv("TOKEN_UID", "preferred_username")
        email_field = os.getenv("TOKEN_EMAIL", "email")
        first_name_field = os.getenv("TOKEN_FIRST_NAME", "given_name")
        last_name_field = os.getenv("TOKEN_LAST_NAME", "family_name")
        if response.status_code == 200:
            token = response.json().get("access_token", "")
            headers = {"Authorization": f"Bearer {token}"}
            user_info = jwt.decode(token, options={"verify_signature": False})
            user_model = get_user_model()
            user, _ = user_model.objects.get_or_create(
                username=user_info[uid_field],
                email=user_info.get(email_field),
                first_name=user_info.get(first_name_field),
                last_name=user_info.get(last_name_field),
            )
            return user
        return None

    def get_user(self, user_id: int) -> Optional[Any]:
        """
        Retrieve a user instance by its ID.

        Parameters
        ----------
        user_id : int
            The ID of the user.

        Returns
        -------
        Optional[User]: The user instance if found, otherwise None.
        """
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None