"""Authentication endpoints for OAuth flow (stateless, cookie-based)."""

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from typing import Optional
import logging

from app.services import auth_service
from app.dependencies import get_user_access_token, get_user_access_token_optional
from app.utils.security import encrypt_token
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Cookie settings
TOKEN_COOKIE_MAX_AGE = 3600  # 1 hour (matches Laserfiche token expiry)
STATE_COOKIE_MAX_AGE = 600   # 10 minutes (for OAuth flow)


@router.get("/login")
async def login(response: Response):
    """Initiate OAuth flow.

    Sets a signed state cookie and returns redirect URL.

    Response:
        {
            "redirect_url": "https://signin.laserfiche.com/oauth/Authorize?..."
        }
    """
    # Define scopes - include project scope for table access
    # Community Edition: Read-only access
    scopes = [
        "table.Read",
        f"project/{settings.LASERFICHE_PROJECT_NAME}",
    ]

    logger.info(f"Initiating OAuth with scopes: {scopes}")
    result = auth_service.initiate_oauth_flow(scopes)

    # Set signed state in cookie for CSRF protection
    response.set_cookie(
        key="lf_state",
        value=result["signed_state"],
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=STATE_COOKIE_MAX_AGE,
        path="/auth",  # Only sent to auth endpoints
    )

    return {"redirect_url": result["redirect_url"]}


@router.get("/callback")
async def callback(
    code: str,
    state: str,
    request: Request,
    lf_state: Optional[str] = Cookie(None),
):
    """Handle OAuth callback from Laserfiche.

    Query Parameters:
        code: Authorization code from Laserfiche
        state: State parameter for CSRF validation

    Sets:
        lf_token cookie (httpOnly, encrypted access token)

    Returns:
        Redirect to frontend
    """
    # Validate state from cookie against callback state
    if not lf_state:
        raise HTTPException(
            status_code=400,
            detail="Missing state cookie. Please try logging in again.",
        )

    auth_service.validate_state(state, lf_state)

    # Exchange code for token
    token_response = await auth_service.exchange_code_for_token(code)
    logger.info(f"Token response keys: {token_response.keys()}")

    # Get token expiry (default 1 hour)
    expires_in = token_response.get("expires_in", 3600)

    # Encrypt access token for cookie storage
    encrypted_token = encrypt_token(token_response["access_token"])

    # Create redirect response to frontend
    redirect_response = RedirectResponse(url=settings.FRONTEND_URL, status_code=302)

    # Set encrypted access token in httpOnly cookie
    redirect_response.set_cookie(
        key="lf_token",
        value=encrypted_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=expires_in,
    )

    # Clear the state cookie (single use)
    redirect_response.delete_cookie("lf_state", path="/auth")

    logger.info("OAuth callback successful, redirecting to frontend")

    return redirect_response


@router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing cookies.

    Returns:
        Success message
    """
    response.delete_cookie("lf_token")
    response.delete_cookie("lf_state", path="/auth")

    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(
    access_token: str = Depends(get_user_access_token),
):
    """Get current authenticated user information.

    Requires authentication.

    Returns:
        Basic auth confirmation (no user details in stateless mode)
    """
    # In stateless mode, we don't have user details stored
    # The presence of a valid token confirms authentication
    return {
        "authenticated": True,
        "message": "Token is valid",
    }


@router.get("/status")
async def check_auth_status(
    access_token: Optional[str] = Depends(get_user_access_token_optional),
):
    """Check if user is authenticated.

    Does not require authentication.

    Returns:
        {
            "authenticated": true/false
        }
    """
    return {
        "authenticated": access_token is not None,
    }
