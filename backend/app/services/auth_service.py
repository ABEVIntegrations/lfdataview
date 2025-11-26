"""Authentication service for OAuth flow (stateless, cookie-based)."""

from typing import Dict, List
from fastapi import HTTPException

from app.utils.security import (
    generate_state,
    create_signed_state,
    verify_signed_state,
)
from app.utils.laserfiche import laserfiche_client


def initiate_oauth_flow(scopes: List[str]) -> Dict:
    """Initiate OAuth flow by generating state and returning authorization URL.

    Args:
        scopes: OAuth scopes to request

    Returns:
        Dict with redirect_url and signed_state (to store in cookie)
    """
    # Generate cryptographically secure state
    state = generate_state()

    # Create signed state with 10-minute expiry
    signed_state = create_signed_state(state, expires_in_seconds=600)

    # Get authorization URL from Laserfiche
    redirect_url = laserfiche_client.get_authorization_url(state, scopes)

    return {
        "redirect_url": redirect_url,
        "state": state,
        "signed_state": signed_state,
    }


def validate_state(state_from_callback: str, signed_state_from_cookie: str) -> bool:
    """Validate OAuth state parameter from callback against signed cookie.

    Args:
        state_from_callback: State parameter from Laserfiche callback
        signed_state_from_cookie: Signed state from cookie

    Returns:
        True if valid

    Raises:
        HTTPException: If state is invalid or expired
    """
    try:
        original_state = verify_signed_state(signed_state_from_cookie)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid or expired state. Please try logging in again. ({str(e)})",
        )

    if state_from_callback != original_state:
        raise HTTPException(
            status_code=400,
            detail="State mismatch. Possible CSRF attack. Please try logging in again.",
        )

    return True


async def exchange_code_for_token(code: str) -> Dict:
    """Exchange authorization code for access token.

    Args:
        code: Authorization code from Laserfiche

    Returns:
        Token response dict with access_token, expires_in, etc.

    Raises:
        HTTPException: If token exchange fails
    """
    try:
        token_response = await laserfiche_client.exchange_code_for_token(code)
        return token_response
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange authorization code: {str(e)}",
        )
