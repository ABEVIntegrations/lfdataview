"""Authentication service for OAuth flow and token management."""

from datetime import datetime, timedelta, timezone
from typing import Dict, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import User, Token, Session as SessionModel, OAuthState
from app.utils.security import (
    generate_state,
    generate_session_token,
    encrypt_token,
    decrypt_token,
)
from app.utils.laserfiche import laserfiche_client
from app.config import settings


async def initiate_oauth_flow(db: Session, scopes: List[str]) -> Dict:
    """Initiate OAuth flow by generating state and returning authorization URL.

    Args:
        db: Database session
        scopes: OAuth scopes to request

    Returns:
        Dict with redirect_url and state
    """
    # Generate state parameter
    state = generate_state()

    # Store state in database with expiry (10 minutes)
    oauth_state = OAuthState(
        state=state,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        used=False,
    )
    db.add(oauth_state)
    db.commit()

    # Get authorization URL from Laserfiche
    redirect_url = laserfiche_client.get_authorization_url(state, scopes)

    return {"redirect_url": redirect_url, "state": state}


async def validate_state(state: str, db: Session) -> bool:
    """Validate OAuth state parameter and mark as used.

    Args:
        state: State parameter from callback
        db: Database session

    Returns:
        True if valid, raises HTTPException if invalid

    Raises:
        HTTPException: If state is invalid or expired
    """
    oauth_state = (
        db.query(OAuthState)
        .filter(
            OAuthState.state == state,
            OAuthState.used == False,
            OAuthState.expires_at > datetime.now(timezone.utc),
        )
        .first()
    )

    if not oauth_state:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired state parameter. Please try logging in again.",
        )

    # Mark state as used
    oauth_state.used = True
    db.commit()

    return True


async def process_oauth_callback(
    code: str, state: str, db: Session, ip_address: str = None, user_agent: str = None
) -> str:
    """Process OAuth callback and create user session.

    Args:
        code: Authorization code from Laserfiche
        state: State parameter from callback
        db: Database session
        ip_address: Client IP address (optional)
        user_agent: Client user agent (optional)

    Returns:
        Session token string

    Raises:
        HTTPException: If callback processing fails
    """
    # 1. Validate state
    await validate_state(state, db)

    # 2. Exchange code for tokens
    try:
        token_response = await laserfiche_client.exchange_code_for_token(code)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange authorization code: {str(e)}",
        )

    # 3. Get or create user
    # Note: Laserfiche doesn't provide a user info endpoint in their OData API
    # For now, we'll create a placeholder user. In a real scenario, you might
    # decode the access token (if it's a JWT) or use another method to get user info.
    user = db.query(User).filter(User.laserfiche_user_id == "default_user").first()

    if not user:
        user = User(
            laserfiche_user_id="default_user",
            username="Laserfiche User",
            email=None,  # Not provided by Laserfiche API
            last_login_at=datetime.now(timezone.utc),
        )
        db.add(user)
        db.flush()  # Get user.id
    else:
        user.last_login_at = datetime.now(timezone.utc)

    # 4. Store or update tokens
    existing_token = db.query(Token).filter(Token.user_id == user.id).first()

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_response.get("expires_in", 3600))

    if existing_token:
        # Update existing token
        existing_token.access_token = encrypt_token(token_response["access_token"])
        existing_token.refresh_token = encrypt_token(
            token_response.get("refresh_token", "")
        )
        existing_token.expires_at = expires_at
        existing_token.scopes = token_response.get("scope", "").split()
        existing_token.updated_at = datetime.now(timezone.utc)
    else:
        # Create new token
        new_token = Token(
            user_id=user.id,
            access_token=encrypt_token(token_response["access_token"]),
            refresh_token=encrypt_token(token_response.get("refresh_token", "")),
            token_type=token_response.get("token_type", "Bearer"),
            expires_at=expires_at,
            scopes=token_response.get("scope", "").split(),
        )
        db.add(new_token)

    # 5. Create session
    session_token = generate_session_token()
    session = SessionModel(
        user_id=user.id,
        session_token=session_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.SESSION_EXPIRY_DAYS),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(session)
    db.commit()

    return session_token


async def refresh_user_token(user_id: str, db: Session) -> str:
    """Refresh user's access token if expired.

    Args:
        user_id: User UUID
        db: Database session

    Returns:
        Valid access token (decrypted)

    Raises:
        HTTPException: If token refresh fails
    """
    token = db.query(Token).filter(Token.user_id == user_id).first()

    if not token:
        raise HTTPException(status_code=401, detail="No token found for user")

    # Check if token is expired or about to expire (buffer: 5 minutes)
    if token.expires_at > datetime.now(timezone.utc) + timedelta(minutes=5):
        # Token still valid, return it
        return decrypt_token(token.access_token)

    # Token expired, refresh it
    if not token.refresh_token:
        raise HTTPException(
            status_code=401, detail="No refresh token available. Please log in again."
        )

    try:
        refresh_token_plain = decrypt_token(token.refresh_token)
        token_response = await laserfiche_client.refresh_access_token(refresh_token_plain)

        # Update token in database
        token.access_token = encrypt_token(token_response["access_token"])
        # Refresh token might be rotated
        if "refresh_token" in token_response:
            token.refresh_token = encrypt_token(token_response["refresh_token"])
        token.expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=token_response.get("expires_in", 3600)
        )
        token.updated_at = datetime.now(timezone.utc)
        db.commit()

        return token_response["access_token"]

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to refresh token. Please log in again. Error: {str(e)}",
        )


async def logout_user(session_token: str, db: Session) -> bool:
    """Logout user by deleting their session.

    Args:
        session_token: Session token to invalidate
        db: Database session

    Returns:
        True if successful
    """
    session = (
        db.query(SessionModel)
        .filter(SessionModel.session_token == session_token)
        .first()
    )

    if session:
        db.delete(session)
        db.commit()

    return True


def get_user_from_session(session_token: str, db: Session) -> User:
    """Get user from session token.

    Args:
        session_token: Session token from cookie
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If session invalid or expired
    """
    session = (
        db.query(SessionModel)
        .filter(
            SessionModel.session_token == session_token,
            SessionModel.expires_at > datetime.now(timezone.utc),
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=401, detail="Session expired or invalid. Please log in again."
        )

    user = db.query(User).filter(User.id == session.user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
