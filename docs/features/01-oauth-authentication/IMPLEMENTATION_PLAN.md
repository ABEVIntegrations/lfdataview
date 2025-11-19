# OAuth Authentication - Implementation Plan

**Last Updated:** 2025-11-18

---

## Backend Implementation

### 1. Laserfiche API Client (`utils/laserfiche.py`)

```python
import httpx
from typing import Dict, List
from app.config import settings

class LaserficheClient:
    OAUTH_BASE = "https://signin.laserfiche.com/oauth"
    API_BASE = "https://api.laserfiche.com/odata4"

    def get_authorization_url(self, state: str, scopes: List[str]) -> str:
        """Build OAuth authorization URL"""
        scope_str = " ".join(scopes)
        params = {
            "client_id": settings.LASERFICHE_CLIENT_ID,
            "redirect_uri": settings.LASERFICHE_REDIRECT_URI,
            "response_type": "code",
            "scope": scope_str,
            "state": state
        }
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.OAUTH_BASE}/Authorize?{query}"

    async def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access and refresh tokens"""
        import base64

        # Basic auth with client_id:client_secret
        credentials = f"{settings.LASERFICHE_CLIENT_ID}:{settings.LASERFICHE_CLIENT_SECRET}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {b64_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.LASERFICHE_REDIRECT_URI
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.OAUTH_BASE}/Token", headers=headers, data=data)
            response.raise_for_status()
            return response.json()  # { access_token, refresh_token, expires_in, token_type }

    async def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh expired access token"""
        # Similar to exchange_code_for_token but with grant_type=refresh_token
        pass  # Implementation similar to above

laserfiche_client = LaserficheClient()
```

### 2. Auth Service (`services/auth_service.py`)

```python
from sqlalchemy.orm import Session
from app.models import User, Token, Session as SessionModel, OAuthState
from app.utils.laserfiche import laserfiche_client
from app.utils.security import encrypt_token, decrypt_token, create_session_token
import uuid
from datetime import datetime, timedelta

async def initiate_oauth_flow(db: Session, scopes: List[str]) -> Dict:
    """Initiate OAuth flow, return redirect URL"""
    # Generate state
    state = str(uuid.uuid4())

    # Store state in database
    oauth_state = OAuthState(
        state=state,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
        used=False
    )
    db.add(oauth_state)
    db.commit()

    # Get authorization URL
    redirect_url = laserfiche_client.get_authorization_url(state, scopes)

    return {"redirect_url": redirect_url, "state": state}

async def process_oauth_callback(code: str, state: str, db: Session) -> str:
    """Process OAuth callback, return session token"""
    # 1. Validate state
    oauth_state = db.query(OAuthState).filter(
        OAuthState.state == state,
        OAuthState.used == False,
        OAuthState.expires_at > datetime.utcnow()
    ).first()

    if not oauth_state:
        raise ValueError("Invalid or expired state")

    # Mark state as used
    oauth_state.used = True
    db.commit()

    # 2. Exchange code for tokens
    token_response = await laserfiche_client.exchange_code_for_token(code)

    # 3. Create or update user (get user info from Laserfiche API if available, or use placeholder)
    user = db.query(User).filter(User.laserfiche_user_id == "placeholder").first()
    if not user:
        user = User(
            laserfiche_user_id="placeholder",  # TODO: Get from Laserfiche user info endpoint
            username="user",
            email="user@example.com"
        )
        db.add(user)
        db.commit()

    # 4. Store tokens
    token = db.query(Token).filter(Token.user_id == user.id).first()
    if token:
        # Update existing token
        token.access_token = encrypt_token(token_response["access_token"])
        token.refresh_token = encrypt_token(token_response.get("refresh_token"))
        token.expires_at = datetime.utcnow() + timedelta(seconds=token_response["expires_in"])
        token.updated_at = datetime.utcnow()
    else:
        # Create new token
        token = Token(
            user_id=user.id,
            access_token=encrypt_token(token_response["access_token"]),
            refresh_token=encrypt_token(token_response.get("refresh_token")),
            expires_at=datetime.utcnow() + timedelta(seconds=token_response["expires_in"]),
            scopes=token_response.get("scope", "").split()
        )
        db.add(token)
    db.commit()

    # 5. Create session
    session_token = create_session_token()
    session = SessionModel(
        user_id=user.id,
        session_token=session_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(session)
    db.commit()

    return session_token
```

### 3. API Endpoints (`routers/auth.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.services import auth_service
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/login")
async def login(db: Session = Depends(get_db)):
    """Initiate OAuth flow"""
    scopes = ["table.Read", "table.Write", f"project/{settings.LASERFICHE_PROJECT}"]
    result = await auth_service.initiate_oauth_flow(db, scopes)
    return result

@router.get("/callback")
async def callback(
    code: str,
    state: str,
    response: Response,
    db: Session = Depends(get_db)
):
    """Handle OAuth callback"""
    try:
        session_token = await auth_service.process_oauth_callback(code, state, db)

        # Set httpOnly cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=settings.ENVIRONMENT == "production",  # HTTPS only in prod
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 days
        )

        # Redirect to frontend
        return {"message": "Authentication successful", "redirect": "/"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
async def logout(
    response: Response,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user"""
    # Delete session from database
    db.query(SessionModel).filter(SessionModel.user_id == current_user.id).delete()
    db.commit()

    # Clear cookie
    response.delete_cookie("session_token")

    return {"message": "Logged out successfully"}

@router.get("/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current authenticated user info"""
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email
    }
```

### 4. Dependencies (`dependencies.py`)

```python
from fastapi import Cookie, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Session as SessionModel
from datetime import datetime

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    session_token: str = Cookie(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from session cookie"""
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Validate session
    session = db.query(SessionModel).filter(
        SessionModel.session_token == session_token,
        SessionModel.expires_at > datetime.utcnow()
    ).first()

    if not session:
        raise HTTPException(status_code=401, detail="Session expired or invalid")

    # Get user
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
```

---

## Frontend Implementation

### 1. Auth Context (`src/contexts/AuthContext.tsx`)

```typescript
import React, { createContext, useState, useEffect, useContext } from 'react';
import { getCurrentUser } from '../services/api';

interface User {
  id: string;
  username: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  checkAuth: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const checkAuth = async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    await fetch('http://localhost:8000/auth/logout', {
      method: 'POST',
      credentials: 'include'
    });
    setUser(null);
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    checkAuth,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
```

### 2. Login Page (`src/pages/LoginPage.tsx`)

```typescript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export function LoginPage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async () => {
    setLoading(true);
    try {
      // Get redirect URL from backend
      const response = await fetch('http://localhost:8000/auth/login', {
        credentials: 'include'
      });
      const data = await response.json();

      // Redirect to Laserfiche
      window.location.href = data.redirect_url;
    } catch (error) {
      console.error('Login failed:', error);
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <h1>Laserfiche Data View</h1>
      <p>Please login to continue</p>
      <button onClick={handleLogin} disabled={loading}>
        {loading ? 'Redirecting...' : 'Login with Laserfiche'}
      </button>
    </div>
  );
}
```

### 3. Callback Page (`src/pages/CallbackPage.tsx`)

```typescript
import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export function CallbackPage() {
  const [searchParams] = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { checkAuth } = useAuth();

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const state = searchParams.get('state');

      if (!code || !state) {
        setError('Missing authorization code or state');
        return;
      }

      try {
        // Call backend callback endpoint
        const response = await fetch(
          `http://localhost:8000/auth/callback?code=${code}&state=${state}`,
          { credentials: 'include' }
        );

        if (!response.ok) {
          throw new Error('Authentication failed');
        }

        // Update auth context
        await checkAuth();

        // Redirect to home
        navigate('/');
      } catch (err) {
        setError('Authentication failed. Please try again.');
        console.error(err);
      }
    };

    handleCallback();
  }, [searchParams, navigate, checkAuth]);

  if (error) {
    return (
      <div>
        <h2>Authentication Error</h2>
        <p>{error}</p>
        <button onClick={() => navigate('/login')}>Try Again</button>
      </div>
    );
  }

  return (
    <div>
      <h2>Authenticating...</h2>
      <p>Please wait while we complete your login.</p>
    </div>
  );
}
```

---

## Database Migration

```python
# alembic/versions/001_create_auth_tables.py

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('laserfiche_user_id', sa.String(255), unique=True, nullable=False),
        sa.Column('username', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True))
    )
    op.create_index('ix_users_username', 'users', ['username'])

    # Create tokens table
    op.create_table(
        'tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), unique=True, nullable=False),
        sa.Column('access_token', sa.Text, nullable=False),
        sa.Column('refresh_token', sa.Text),
        sa.Column('token_type', sa.String(50), nullable=False, server_default='Bearer'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('scopes', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('session_token', sa.String(255), unique=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.Text)
    )
    op.create_index('ix_sessions_expires_at', 'sessions', ['expires_at'])

    # Create oauth_states table
    op.create_table(
        'oauth_states',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('state', sa.String(255), unique=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean, nullable=False, server_default='false')
    )
    op.create_index('ix_oauth_states_expires_at', 'oauth_states', ['expires_at'])

def downgrade():
    op.drop_table('oauth_states')
    op.drop_table('sessions')
    op.drop_table('tokens')
    op.drop_table('users')
```

---

**Last Updated:** 2025-11-18
