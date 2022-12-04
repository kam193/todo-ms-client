import hashlib
import secrets
import webbrowser
import wsgiref.simple_server
import wsgiref.util
from base64 import urlsafe_b64encode
from typing import Any, Callable, Optional

from furl import furl  # type: ignore
from requests import Response
from requests_oauthlib import OAuth2Session  # type: ignore

from .base import AbstractProvider


class _LocalRedirectHandlingApp(object):
    """A WSGI app handles redirection from sign-in service."""

    def __init__(self, message: str) -> None:
        self.callback_url: str
        self._message = message

    def __call__(self, environ: Any, start_response: Callable) -> list[bytes]:
        start_response("200 OK", [("Content-type", "text/plain")])
        self.callback_url = wsgiref.util.request_uri(environ)
        return [self._message.encode("utf-8")]


class RequestBeforeAuthenticatedError(Exception):
    """Try to execute request before authenticate"""


class WebBrowserProvider(AbstractProvider):
    """An provider that can call webbrowser to open sign-in page"""

    _SCOPES = "profile openid User.Read Calendars.Read Tasks.ReadWrite"
    _DEFAULT_OPEN_MESSAGE = (
        "Open following page in your webbrowser and finish singing in:"
    )
    _DEFAULT_FINISH_MESSAGE = (
        "Authorization completed. You can close this page and return to the app"
    )

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        authority: str = "https://login.microsoftonline.com/common/",
        authorize_endpoint: str = "oauth2/v2.0/authorize",
        token_endpoint: str = "oauth2/v2.0/token",
        open_message: str = _DEFAULT_OPEN_MESSAGE,
        finish_message: str = _DEFAULT_FINISH_MESSAGE,
    ):
        self._app_id = app_id
        self._app_secret = app_secret
        self._open_message = open_message
        self._finish_message = finish_message

        authority_url = furl(authority)
        self._authorize_url = (authority_url / authorize_endpoint).url
        self._token_url = (authority_url / token_endpoint).url

        self._session: OAuth2Session

    def _save_token(self, token: dict) -> None:
        self._token = token

    def _replace_http_into_https(self, url: str) -> str:
        """OAuthLib strictly expects HTTPS protocol, even for localhost"""
        if url.startswith("http://"):
            return url.replace("http", "https", 1)
        return url

    def _build_session(self, redirect_url: str) -> OAuth2Session:
        refresh_params = {"client_id": self._app_id, "client_secret": self._app_secret}

        session = OAuth2Session(
            self._app_id,
            scope=self._SCOPES,
            redirect_uri=self._replace_http_into_https(redirect_url),
            auto_refresh_url=self._token_url,
            auto_refresh_kwargs=refresh_params,
            token_updater=self._save_token,
        )
        # Workaround for InsecureTransportError from OAuthLib for http://localhost
        session.redirect_uri = redirect_url

        return session

    def authorize(self, local_port: int = 8888, print_message: bool = True) -> None:
        """Run authorization workflow. Call webbrowser login, get response and token

        'local_port' - on this port we wait for redirection from sing-in page.
        Address http://localhost:<local_port>/ must be allowed as redirect URL."""

        redirect_url = f"http://localhost:{local_port}"

        self._session = self._build_session(redirect_url)

        code_verifier = secrets.token_bytes(32).hex()
        code_challenge = str(
            urlsafe_b64encode(hashlib.sha256(code_verifier.encode("ascii")).digest()),
            "utf-8",
        ).replace("=", "")

        sign_in_url, state = self._session.authorization_url(
            self._authorize_url,
            prompt="login",
            code_challenge=code_challenge,
            code_challenge_method="S256",
        )

        response_app = _LocalRedirectHandlingApp(self._finish_message)
        response_server = wsgiref.simple_server.make_server(
            "localhost", local_port, response_app
        )

        if print_message:
            print(self._open_message)
            print(sign_in_url)

        webbrowser.open(sign_in_url)
        response_server.handle_request()

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "http://localhost",
        }
        self._token = self._session.fetch_token(
            self._token_url,
            # client_secret=self._app_secret,
            include_client_id=True,
            authorization_response=self._replace_http_into_https(
                response_app.callback_url
            ),
            code_verifier=code_verifier,
            headers=headers,
        )

    def get(self, url: str, params: Optional[dict] = None) -> Response:
        if not self._token:
            raise RequestBeforeAuthenticatedError

        return self._session.get(url=url, params=params)  # type: ignore

    def delete(self, url: str) -> Response:
        if not self._token:
            raise RequestBeforeAuthenticatedError

        return self._session.delete(url=url)  # type: ignore

    def patch(self, url: str, json_data: dict) -> Response:
        if not self._token:
            raise RequestBeforeAuthenticatedError

        return self._session.patch(url=url, json=json_data)  # type: ignore

    def post(self, url: str, json_data: dict) -> Response:
        if not self._token:
            raise RequestBeforeAuthenticatedError

        return self._session.post(url=url, json=json_data)  # type: ignore
