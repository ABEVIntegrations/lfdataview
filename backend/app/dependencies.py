"""FastAPI dependencies for authentication and database sessions."""

from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import User
from app.services.auth_service import get_user_from_session


async def get_current_user(
    session_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
) -> User:
    """Dependency to get the current authenticated user from session cookie.

    Args:
        session_token: Session token from cookie
        db: Database session

    Returns:
        User object if authenticated

    Raises:
        HTTPException: 401 if not authenticated or session invalid
    """
    if not session_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please log in.",
        )

    user = get_user_from_session(session_token, db)
    return user


async def get_current_user_optional(
    session_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Optional authentication dependency.

    Returns User if authenticated, None otherwise.
    Does not raise exception if not authenticated.

    Args:
        session_token: Session token from cookie
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    if not session_token:
        return None

    try:
        user = get_user_from_session(session_token, db)
        return user
    except HTTPException:
        return None


async def get_user_access_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> str:
    """Dependency to get a valid access token for the current user.

    Automatically refreshes the token if expired.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Valid access token (decrypted)

    Raises:
        HTTPException: If token refresh fails
    """
    from app.services.auth_service import refresh_user_token

    access_token = await refresh_user_token(str(current_user.id), db)
    return access_token
