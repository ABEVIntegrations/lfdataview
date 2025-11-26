"""FastAPI dependencies for authentication."""

from fastapi import Cookie, HTTPException
from typing import Optional

from app.utils.security import decrypt_token


async def get_user_access_token(
    lf_token: Optional[str] = Cookie(None),
) -> str:
    """Get decrypted access token from cookie.

    Args:
        lf_token: Encrypted access token from cookie

    Returns:
        Decrypted access token

    Raises:
        HTTPException: 401 if not authenticated or token invalid
    """
    if not lf_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please log in.",
        )

    try:
        return decrypt_token(lf_token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token. Please log in again.",
        )


async def get_user_access_token_optional(
    lf_token: Optional[str] = Cookie(None),
) -> Optional[str]:
    """Optional authentication - returns token or None.

    Args:
        lf_token: Encrypted access token from cookie

    Returns:
        Decrypted access token if valid, None otherwise
    """
    if not lf_token:
        return None

    try:
        return decrypt_token(lf_token)
    except Exception:
        return None
