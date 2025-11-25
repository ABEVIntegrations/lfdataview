"""Authentication endpoints for OAuth flow."""

from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional
from app.services import auth_service
from app.models import User
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/login")
async def login(db: Session = Depends(get_db)):
    """Initiate OAuth flow.

    Returns redirect URL to Laserfiche OAuth authorization endpoint.

    Response:
        {
            "redirect_url": "https://signin.laserfiche.com/oauth/Authorize?...",
            "state": "uuid-string"
        }
    """
    # Define scopes - include project scope for table access
    scopes = [
        "table.Read",
        "table.Write",
        f"project/{settings.LASERFICHE_PROJECT_NAME}",  # Required for OData Table API
    ]

    logger.info(f"Initiating OAuth with scopes: {scopes}")
    result = await auth_service.initiate_oauth_flow(db, scopes)

    return result


@router.get("/callback")
async def callback(
    code: str,
    state: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """Handle OAuth callback from Laserfiche.

    Query Parameters:
        code: Authorization code from Laserfiche
        state: State parameter for CSRF validation

    Returns:
        Success message with redirect instruction

    Sets:
        session_token cookie (httpOnly, secure in production)
    """
    try:
        # Get client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Process callback and get session token
        session_token = await auth_service.process_oauth_callback(
            code=code,
            state=state,
            db=db,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Create redirect response to frontend
        redirect_response = RedirectResponse(url=settings.FRONTEND_URL, status_code=302)

        # Set httpOnly cookie on the redirect response
        redirect_response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=settings.ENVIRONMENT == "production",  # HTTPS only in production
            samesite="lax",
            max_age=settings.SESSION_EXPIRY_DAYS * 24 * 60 * 60,  # Convert days to seconds
        )

        return redirect_response

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}",
        )


@router.post("/logout")
async def logout(
    response: Response,
    session_token: Optional[str] = Depends(lambda: None),  # Get from cookie
    db: Session = Depends(get_db),
):
    """Logout user by deleting session.

    Clears session cookie and removes session from database.

    Returns:
        Success message
    """
    if session_token:
        await auth_service.logout_user(session_token, db)

    # Clear cookie
    response.delete_cookie("session_token")

    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user information.

    Requires authentication.

    Returns:
        User information
    """
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "last_login": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
    }


@router.get("/status")
async def check_auth_status(
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Check if user is authenticated.

    Does not require authentication.

    Returns:
        {
            "authenticated": true/false,
            "user": {...} or null
        }
    """
    if current_user:
        return {
            "authenticated": True,
            "user": {
                "id": str(current_user.id),
                "username": current_user.username,
            },
        }
    else:
        return {
            "authenticated": False,
            "user": None,
        }
