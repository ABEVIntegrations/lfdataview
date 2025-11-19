# Feature 01: OAuth Authentication - TODO List

**Last Updated:** 2025-11-18
**Status:** Not Started
**Estimated Tasks:** 35

---

## Phase 1: Planning & Setup

### Laserfiche Developer Console Setup
- [ ] Create Laserfiche Developer Console account (if needed)
- [ ] Register new application as "Web App"
  - [ ] Set application name
  - [ ] Configure redirect URI (e.g., `http://localhost:8000/auth/callback` for dev)
  - [ ] Request scopes: `table.Read`, `table.Write`, `project/{YOUR_PROJECT}`
  - [ ] Save `client_id` and `client_secret`
- [ ] Document app registration details in `.env.example`
- [ ] Test OAuth flow manually (using Postman/cURL) to verify credentials

### Environment Configuration
- [ ] Create `backend/.env` file from template
  - [ ] Add `LASERFICHE_CLIENT_ID`
  - [ ] Add `LASERFICHE_CLIENT_SECRET`
  - [ ] Add `LASERFICHE_REDIRECT_URI`
  - [ ] Add `SECRET_KEY` (generate with `openssl rand -hex 32`)
  - [ ] Add `TOKEN_ENCRYPTION_KEY` (generate with Python `Fernet.generate_key()`)
  - [ ] Add `DATABASE_URL`
- [ ] Create `frontend/.env` file
  - [ ] Add `VITE_API_BASE_URL=http://localhost:8000`
- [ ] Add `.env` to `.gitignore` (security)

---

## Phase 2: Database Implementation

### Database Schema
- [ ] Create SQLAlchemy models (see [data_models.md](../../_core/data_models.md))
  - [ ] `models/user.py` - User model (id, laserfiche_user_id, username, email, timestamps)
  - [ ] `models/token.py` - Token model (id, user_id, access_token, refresh_token, expires_at, scopes)
  - [ ] `models/session.py` - Session model (id, user_id, session_token, expires_at, ip_address, user_agent)
  - [ ] `models/oauth_state.py` - OAuthState model (id, state, expires_at, used)

### Database Migrations
- [ ] Initialize Alembic
  - [ ] Run `alembic init alembic`
  - [ ] Configure `alembic.ini` with `DATABASE_URL`
  - [ ] Update `alembic/env.py` to import models
- [ ] Create initial migration
  - [ ] Run `alembic revision --autogenerate -m "Create initial schema"`
  - [ ] Review generated migration script
  - [ ] Run `alembic upgrade head`
- [ ] Verify tables created
  - [ ] Connect to PostgreSQL: `psql -U lfdataview -d lfdataview`
  - [ ] List tables: `\dt`
  - [ ] Verify schema: `\d users`, `\d tokens`, `\d sessions`, `\d oauth_states`

---

## Phase 3: Backend Implementation

### Utility Functions
- [ ] Create `utils/security.py`
  - [ ] `generate_state()` - Generate random UUID for CSRF protection
  - [ ] `encrypt_token(token: str) -> str` - Encrypt access/refresh tokens
  - [ ] `decrypt_token(encrypted: str) -> str` - Decrypt tokens
  - [ ] `create_session_token()` - Generate secure session token (JWT or random)
  - [ ] `verify_session_token(token: str)` - Validate session token

- [ ] Create `utils/laserfiche.py`
  - [ ] `LaserficheClient` class
    - [ ] `get_authorization_url(state: str, scopes: list) -> str` - Build authorization URL
    - [ ] `exchange_code_for_token(code: str) -> dict` - Exchange auth code for tokens
    - [ ] `refresh_access_token(refresh_token: str) -> dict` - Refresh expired access token
    - [ ] `get_user_info(access_token: str) -> dict` - Get user info from Laserfiche (if available)
    - [ ] `_make_request(method, url, headers, data)` - Internal HTTP helper with error handling

### Services
- [ ] Create `services/auth_service.py`
  - [ ] `initiate_oauth_flow(db: Session) -> str` - Generate state, store in DB, return redirect URL
  - [ ] `validate_state(state: str, db: Session) -> bool` - Validate and mark state as used
  - [ ] `process_oauth_callback(code: str, state: str, db: Session) -> Session` - Full callback logic
    - [ ] Validate state
    - [ ] Exchange code for tokens
    - [ ] Get or create user
    - [ ] Store tokens in database
    - [ ] Create session
    - [ ] Return session token
  - [ ] `refresh_user_token(user_id: UUID, db: Session) -> str` - Refresh access token if expired
  - [ ] `logout_user(session_token: str, db: Session)` - Delete session and optionally tokens
  - [ ] `get_current_user(session_token: str, db: Session) -> User` - Get user from session token

### API Dependencies
- [ ] Create `dependencies.py`
  - [ ] `get_db()` - Database session dependency
  - [ ] `get_current_user(session_token: str = Cookie(None))` - Extract and validate session from cookie
  - [ ] `require_auth()` - Dependency that raises 401 if not authenticated

### API Endpoints
- [ ] Create `routers/auth.py`
  - [ ] `GET /auth/login` - Initiate OAuth flow
    - [ ] Generate state parameter
    - [ ] Store state in database with expiry
    - [ ] Return redirect URL to Laserfiche authorization endpoint
  - [ ] `GET /auth/callback` - OAuth callback handler
    - [ ] Extract `code` and `state` from query params
    - [ ] Validate state (CSRF check)
    - [ ] Exchange code for access_token and refresh_token
    - [ ] Create or update user record
    - [ ] Store tokens in database (encrypted)
    - [ ] Create session
    - [ ] Set httpOnly cookie with session token
    - [ ] Redirect to frontend home page
  - [ ] `POST /auth/logout` - Logout user
    - [ ] Delete session from database
    - [ ] Clear session cookie
    - [ ] Return success response
  - [ ] `GET /auth/me` - Get current user info
    - [ ] Requires authentication (use `require_auth` dependency)
    - [ ] Return user info (username, email, etc.)
  - [ ] `GET /auth/status` - Check if user is authenticated
    - [ ] Check session token validity
    - [ ] Return `{ authenticated: true/false }`

### FastAPI Main App
- [ ] Update `main.py`
  - [ ] Include auth router: `app.include_router(auth.router)`
  - [ ] Configure CORS for frontend origin
  - [ ] Add session middleware (if using sessions)
  - [ ] Add exception handlers for 401, 403 errors

---

## Phase 4: Frontend Implementation

### React Context & Hooks
- [ ] Create `src/contexts/AuthContext.tsx`
  - [ ] State: `user`, `isAuthenticated`, `isLoading`
  - [ ] Functions: `login()`, `logout()`, `checkAuth()`
  - [ ] Use React Context to share auth state globally

- [ ] Create `src/hooks/useAuth.ts`
  - [ ] Hook to access AuthContext
  - [ ] Returns `{ user, isAuthenticated, isLoading, login, logout }`

### API Client
- [ ] Create `src/services/api.ts`
  - [ ] Axios instance with base URL (`VITE_API_BASE_URL`)
  - [ ] Interceptor to include credentials (cookies)
  - [ ] Error handling interceptor (401 → redirect to login)
  - [ ] API functions:
    - [ ] `login() -> redirect URL` - Call GET /auth/login
    - [ ] `logout()` - Call POST /auth/logout
    - [ ] `getCurrentUser()` - Call GET /auth/me
    - [ ] `checkAuthStatus()` - Call GET /auth/status

### Pages & Components
- [ ] Create `src/pages/LoginPage.tsx`
  - [ ] "Login with Laserfiche" button
  - [ ] On click: Call API to get authorization URL, redirect user
  - [ ] Show loading state while redirecting

- [ ] Create `src/pages/CallbackPage.tsx`
  - [ ] Extract `code` and `state` from URL query params
  - [ ] Call backend `/auth/callback` endpoint
  - [ ] On success: Update auth context, redirect to home
  - [ ] On error: Show error message, link to retry login

- [ ] Create `src/components/ProtectedRoute.tsx`
  - [ ] Wrapper component for authenticated routes
  - [ ] If not authenticated: Redirect to login page
  - [ ] If authenticated: Render children

- [ ] Update `src/App.tsx`
  - [ ] Wrap app in `AuthContext.Provider`
  - [ ] Check auth status on mount
  - [ ] Show loading spinner while checking auth

### Routing
- [ ] Update `src/router.tsx`
  - [ ] Route: `/login` → LoginPage
  - [ ] Route: `/auth/callback` → CallbackPage
  - [ ] Route: `/` → ProtectedRoute → Home (placeholder for now)

---

## Phase 5: Testing

### Backend Tests
- [ ] Create `tests/test_auth.py`
  - [ ] Test `GET /auth/login` endpoint
    - [ ] Returns redirect URL with state parameter
    - [ ] State is stored in database
  - [ ] Test `GET /auth/callback` endpoint
    - [ ] Valid code and state → creates user, session, tokens
    - [ ] Invalid state → returns 400 error
    - [ ] Expired state → returns 400 error
    - [ ] Used state → returns 400 error
  - [ ] Test `POST /auth/logout` endpoint
    - [ ] Deletes session
    - [ ] Clears cookie
  - [ ] Test `GET /auth/me` endpoint
    - [ ] Without session → returns 401
    - [ ] With valid session → returns user info
  - [ ] Test token refresh logic
    - [ ] Expired token → auto-refreshes using refresh_token
    - [ ] Invalid refresh_token → returns error

- [ ] Create `tests/test_auth_service.py`
  - [ ] Test `initiate_oauth_flow()`
  - [ ] Test `validate_state()`
  - [ ] Test `process_oauth_callback()`
  - [ ] Test `refresh_user_token()`

- [ ] Create `tests/test_security.py`
  - [ ] Test token encryption/decryption
  - [ ] Test session token generation/validation

### Integration Tests
- [ ] Test full OAuth flow end-to-end
  - [ ] Mock Laserfiche OAuth endpoints
  - [ ] Simulate user login flow
  - [ ] Verify session and tokens created

### Frontend Tests
- [ ] Create `tests/AuthContext.test.tsx`
  - [ ] Test auth context provider
  - [ ] Test login/logout functions
  - [ ] Test auth state updates

- [ ] Create `tests/LoginPage.test.tsx`
  - [ ] Test login button triggers redirect
  - [ ] Test loading state

- [ ] Create `tests/CallbackPage.test.tsx`
  - [ ] Test successful callback handling
  - [ ] Test error handling

### Manual Testing
- [ ] Test with real Laserfiche account
  - [ ] Navigate to /login
  - [ ] Click "Login with Laserfiche"
  - [ ] Authenticate on Laserfiche
  - [ ] Verify redirect back to app
  - [ ] Verify authenticated state (check /auth/me)
  - [ ] Verify session persists across page reloads
  - [ ] Verify logout works
- [ ] Test token refresh
  - [ ] Wait for access_token to expire (or manually set short expiry)
  - [ ] Make API call
  - [ ] Verify token auto-refreshes
- [ ] Test CSRF protection
  - [ ] Attempt callback with invalid state
  - [ ] Verify rejection

---

## Phase 6: Security Hardening

### Security Review
- [ ] Verify CSRF protection (state parameter)
- [ ] Verify tokens encrypted in database
- [ ] Verify session tokens in httpOnly cookies (not localStorage)
- [ ] Verify HTTPS enforced in production
- [ ] Verify secrets not hardcoded (use environment variables)
- [ ] Verify client_secret never sent to frontend
- [ ] Review CORS configuration (only allow frontend origin)
- [ ] Test for XSS vulnerabilities
- [ ] Test for SQL injection (SQLAlchemy should prevent, but verify)

### Logging & Monitoring
- [ ] Add logging for authentication events
  - [ ] User login success
  - [ ] User login failure
  - [ ] Token refresh events
  - [ ] Logout events
- [ ] Add error logging
  - [ ] OAuth errors
  - [ ] Token validation errors
  - [ ] State validation failures

---

## Phase 7: Documentation

### Code Documentation
- [ ] Add docstrings to all functions
- [ ] Add type hints to all function parameters and returns
- [ ] Add comments for complex logic (especially OAuth flow)

### User Documentation
- [ ] Update [README.md](README.md) with setup instructions
- [ ] Document Laserfiche app registration process
- [ ] Document environment variable configuration
- [ ] Add troubleshooting section (common errors)

### API Documentation
- [ ] Verify OpenAPI docs generated by FastAPI
- [ ] Access /docs and /redoc endpoints
- [ ] Add request/response examples

---

## Phase 8: Deployment Preparation

### Environment Configuration
- [ ] Create `.env.production.example` with production placeholders
- [ ] Document production environment variables
- [ ] Set up secrets management strategy (Docker secrets, AWS Secrets Manager, etc.)

### HTTPS Setup
- [ ] Configure Caddy for auto-HTTPS (or Nginx with Let's Encrypt)
- [ ] Update `LASERFICHE_REDIRECT_URI` to HTTPS domain
- [ ] Test OAuth flow with HTTPS

### Health Checks
- [ ] Add `/health` endpoint for Docker health checks
- [ ] Verify database connectivity in health check

### Cleanup & Optimization
- [ ] Implement cleanup job for expired sessions
- [ ] Implement cleanup job for expired oauth_states
- [ ] Set up database connection pooling
- [ ] Review and optimize database queries

---

## Definition of Done

Feature 01 is complete when:

- [x] All checkboxes in this TODO are completed
- [x] All tests pass (backend + frontend)
- [x] Manual testing with real Laserfiche account successful
- [x] Security review completed, no critical issues
- [x] Code documented with docstrings and comments
- [x] User documentation updated
- [x] Deployed to development/staging environment
- [x] No blocking bugs

---

## Notes & Questions

- **Token Expiry:** How long are Laserfiche access tokens valid? (Check Laserfiche docs)
- **Refresh Token Rotation:** Does Laserfiche rotate refresh tokens? (Need to handle this)
- **Multiple Sessions:** Should users be able to have multiple concurrent sessions? (Decision: TBD)
- **Remember Me:** Should we implement "remember me" functionality? (Decision: Not in MVP)

---

**Last Updated:** 2025-11-18
**Next Update:** As tasks are completed
