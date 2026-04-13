from logging import getLogger as get_logger
from urllib.parse import urlencode, urljoin
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from kobo_sync_rat.models.kobo.auth import (
    KoboTokenAndUserResponse,
    KoboTokenResponse,
    TokenType,
)

logger = get_logger(__name__)


router = APIRouter()


@router.post("/v1/auth/device", response_model=KoboTokenAndUserResponse)
async def post_auth_device():
    """Authorize a kobo device to your account.

    :param request:
    :return:
    """
    return KoboTokenAndUserResponse(
        token_type=TokenType.BEARER,
        access_token="ACCESS_TOKEN",
        refresh_token="REFRESH_TOKEN",
        user_key=UUID(int=1),
        tracking_id="TRACKING_ID",
    )


@router.post("/v1/auth/refresh", response_model=KoboTokenResponse)
async def post_auth_refresh(request: Request):
    """Refresh auth tokens."""
    # Request:
    #
    # {
    #   "AppVersion": "4.45.23640",
    #   "ClientKey": "CLIENT_KEY"
    #   "PlatformId": "00000000-0000-0000-0000-000000000391",
    #   "RefreshToken": ""
    # }

    return KoboTokenResponse(
        token_type=TokenType.BEARER,
        access_token="ACCESS_TOKEN",
        refresh_token="NEW_REFRESH_TOKEN",
    )


@router.get("/signin")
def get_sign_in():
    """Sign in to an account for this kobo device."""
    # Show web HTML and then do a redirect to..
    # kobo://UserAuthenticated?returnUrl={REDIRECT_URL}&userKey={USER_KEY}4&userId={USER_ID}&email={USER_EMAIL}
    # even if with javascript via
    # window.location.href = e.RedirectUrl;

    return HTMLResponse(
        content="<html><body>Redirecting...<script type=\"text/javascript\">window.location.href='/v1/auth/activate';</script></body></html>"
    )


@router.get("/v1/auth/activate")
def get_activation():
    """On activation completed."""
    # Placeholders
    user_key = UUID(int=1)
    user_id = UUID(int=2)
    user_email = "example@example.com"

    query_string = urlencode(
        {"userKey": str(user_key), "userId": str(user_id), "email": user_email}
    )

    return RedirectResponse(f"kobo://UserAuthenticated?{query_string}")


@router.get("/.well-known/openid-configuration")
def get_openid_configuration(request: Request):
    base_url = str(request.base_url)

    return {
        "authorization_endpoint": urljoin(base_url, "oidc/authorize"),
        "authorization_response_iss_parameter_supported": True,
        "claims_supported": [
            "sub",
            "given_name",
            "family_name",
            "name",
            "email",
            "email_verified",
            "preferred_username",
            "picture",
            "groups",
        ],
        "code_challenge_methods_supported": [
            "plain",
            "S256",
        ],
        "device_authorization_endpoint": urljoin(base_url, "oidc/device/authorize"),
        "end_session_endpoint": urljoin(base_url, "oidc/end-session"),
        "grant_types_supported": [
            "authorization_code",
            "refresh_token",
            "urn:ietf:params:oauth:grant-type:device_code",
            "client_credentials",
        ],
        "id_token_signing_alg_values_supported": ["RS256"],
        "introspection_endpoint": urljoin(base_url, "oidc/introspect"),
        "issuer": urljoin(base_url, "/"),
        "jwks_uri": urljoin(base_url, ".well-known/jwks.json"),
        "response_types_supported": ["code", "id_token"],
        "scopes_supported": ["openid", "profile", "email", "groups"],
        "subject_types_supported": ["public"],
        "token_endpoint": urljoin(base_url, "oidc/token"),
        "token_endpoint_auth_methods_supported": [
            "client_secret_basic",
            "client_secret_post",
            "none",
        ],
        "userinfo_endpoint": urljoin(base_url, "oidc/userinfo"),
    }


@router.get("/oidc/authorize")
def get_oidc_authorize():
    return {
        "device_code": "EXAMPLE_DEVICE_CODE",
        "user_code": "EXAMPLE",
        "verification_uri": "oidc/device",
        "verification_uri_complete": "oidc/device?user_code=EXAMPLE",
        "expires_in": 1800,
        "interval": 5,
    }


@router.post("/oidc/token")
async def post_oidc_token(request: Request):
    return {
        "access_token": "OIDC_ACCESS_TOKEN",
        "token_type": "Bearer",
        "refresh_token": "OIDC_REFRESH_TOKEN",
        "expires_in": 3600,
    }


@router.get("/v1/affiliate")
def get_affiliate():
    # This is passed along somewhere?
    return {"AffiliateName": "SyncRat"}
