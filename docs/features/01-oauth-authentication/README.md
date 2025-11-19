# Feature 01: OAuth Authentication

**Phase:** 1 - MVP
**Priority:** Critical
**Status:** 📋 Planned
**Last Updated:** 2025-11-18

---

## Overview

This feature implements secure user authentication using the **Laserfiche OAuth 2.0 Authorization Code Flow**. It is the foundation of the entire application, enabling users to securely authenticate and authorizing the application to access Laserfiche lookup table data on their behalf.

---

## What This Feature Does

### For End Users

1. **Login Flow:**
   - User clicks "Login with Laserfiche" button
   - Redirected to Laserfiche login page
   - Enters Laserfiche credentials
   - Grants permissions to the application
   - Redirected back to application (now authenticated)

2. **Session Management:**
   - User stays logged in across page reloads
   - Session expires after configurable period (default: 7 days)
   - Can manually logout

3. **Transparent Token Management:**
   - Access tokens automatically refreshed when expired
   - No interruption to user experience

### For Developers

- Secure OAuth 2.0 implementation with CSRF protection
- Token encryption at rest in PostgreSQL
- Session management with httpOnly cookies
- Protected API endpoints requiring authentication
- Automatic token refresh logic

---

## OAuth 2.0 Authorization Code Flow

```
┌──────────┐
│   User   │
└─────┬────┘
      │
      │ 1. Clicks "Login"
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  React Frontend                                  │
│                                                                   │
│  GET /auth/login                                                 │
└─────┬───────────────────────────────────────────────────────────┘
      │
      │ 2. Request login URL
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FastAPI Backend                                 │
│                                                                   │
│  - Generate state (UUID)                                         │
│  - Store state in database (expires in 10 min)                   │
│  - Return redirect URL                                           │
└─────┬───────────────────────────────────────────────────────────┘
      │
      │ 3. Redirect to:
      │    https://signin.laserfiche.com/oauth/Authorize?
      │      client_id={ID}&redirect_uri={CALLBACK}&state={STATE}&...
      ▼
┌─────────────────────────────────────────────────────────────────┐
│              Laserfiche OAuth Server                             │
│                                                                   │
│  - User enters credentials                                       │
│  - User grants permissions                                       │
│  - Generates authorization code                                  │
└─────┬───────────────────────────────────────────────────────────┘
      │
      │ 4. Redirect to:
      │    {CALLBACK}?code={AUTH_CODE}&state={STATE}
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FastAPI Backend                                 │
│                  GET /auth/callback                              │
│                                                                   │
│  - Validate state (CSRF check) ✅                                │
│  - Exchange code for tokens:                                     │
│      POST https://signin.laserfiche.com/oauth/Token              │
│      { grant_type: "authorization_code", code: {CODE} }          │
│  - Receive: access_token, refresh_token, expires_in              │
│  - Create or update user in database                             │
│  - Store tokens (encrypted) in database                          │
│  - Create session                                                │
│  - Set httpOnly cookie with session token                        │
│  - Redirect to frontend home page                                │
└─────┬───────────────────────────────────────────────────────────┘
      │
      │ 5. User authenticated! ✅
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  React Frontend                                  │
│                                                                   │
│  - Session cookie automatically included in API requests         │
│  - User can access protected features                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Components

### Backend (FastAPI)

**Endpoints:**
- `GET /auth/login` - Initiate OAuth flow, return redirect URL
- `GET /auth/callback` - Handle OAuth callback, create session
- `POST /auth/logout` - Logout user, clear session
- `GET /auth/me` - Get current user info (protected)
- `GET /auth/status` - Check authentication status

**Services:**
- `auth_service.py` - OAuth flow logic, token management
- `laserfiche.py` - Laserfiche API client

**Database Tables:**
- `users` - User records from Laserfiche
- `tokens` - Access and refresh tokens (encrypted)
- `sessions` - Active user sessions
- `oauth_states` - Temporary CSRF protection states

### Frontend (React)

**Context:**
- `AuthContext` - Global authentication state

**Pages:**
- `LoginPage` - Login button, redirect to OAuth
- `CallbackPage` - Handle OAuth callback

**Hooks:**
- `useAuth()` - Access auth state and functions

**Components:**
- `ProtectedRoute` - Wrapper for authenticated routes

---

## Security Features

### 1. CSRF Protection
- **State Parameter:** Random UUID generated for each OAuth request
- **Validation:** State verified on callback, marked as used
- **Expiry:** States expire after 10 minutes

### 2. Secure Token Storage
- **Backend:** Tokens encrypted in PostgreSQL database
- **Frontend:** Session token in httpOnly cookie (not accessible via JavaScript)
- **Never Exposed:** Access tokens never sent to frontend

### 3. Client Secret Protection
- **Server-Side Only:** Client secret stored in backend environment variables
- **Never Exposed:** Never sent to frontend or included in responses

### 4. Session Security
- **httpOnly Cookies:** Prevents XSS attacks from stealing session tokens
- **Secure Flag:** Cookies only sent over HTTPS in production
- **Expiry:** Sessions auto-expire after configurable period

### 5. HTTPS Enforcement
- **Development:** HTTP allowed on localhost
- **Production:** HTTPS required, enforced by Caddy

---

## Token Refresh Flow

```
User makes API request → Backend checks access_token expiry
                         ↓
                   Is expired or about to expire?
                         ↓
                   YES ─────→ Use refresh_token to get new access_token
                    │         POST /oauth/Token with refresh_token
                    │         ↓
                    │         Update tokens in database
                    │         ↓
                    │         Continue with original request ✅
                    │
                   NO ──────→ Use existing access_token ✅
```

**Benefits:**
- Transparent to user (no re-authentication needed)
- Automatic and efficient
- Handles expired tokens gracefully

---

## Configuration

### Environment Variables (Backend)

```bash
# Laserfiche OAuth
LASERFICHE_CLIENT_ID=your_client_id
LASERFICHE_CLIENT_SECRET=your_client_secret
LASERFICHE_REDIRECT_URI=http://localhost:8000/auth/callback

# Security
SECRET_KEY=your_secret_key_here_use_openssl_rand
TOKEN_ENCRYPTION_KEY=your_fernet_key_here

# Session
SESSION_EXPIRY_DAYS=7

# Database
DATABASE_URL=postgresql://user:pass@localhost/lfdataview
```

### Laserfiche App Registration

1. Go to [Laserfiche Developer Console](https://developers.laserfiche.com/)
2. Create new application
3. Set **Application Type:** Web App
4. Set **Redirect URI:** `http://localhost:8000/auth/callback` (dev) or `https://yourdomain.com/auth/callback` (prod)
5. Set **Scopes:** `table.Read table.Write project/{YOUR_PROJECT}`
6. Save `client_id` and `client_secret`

---

## Testing Strategy

### Unit Tests
- OAuth state generation and validation
- Token encryption/decryption
- Session creation and validation
- Laserfiche API client functions

### Integration Tests
- Full OAuth flow (mocked Laserfiche responses)
- Token refresh logic
- Session expiry

### Manual Testing
- Real Laserfiche account authentication
- Session persistence across page reloads
- Logout functionality
- Token auto-refresh (wait for expiry or manually shorten)

### Security Tests
- CSRF attack prevention (invalid state)
- XSS prevention (httpOnly cookies)
- SQL injection prevention (SQLAlchemy)

---

## Error Handling

| Error | Cause | Response |
|-------|-------|----------|
| Invalid state | State mismatch or expired | 400 Bad Request - "Invalid or expired state" |
| OAuth code exchange fails | Invalid code or credentials | 400 Bad Request - "Authentication failed" |
| Expired session | Session expired or doesn't exist | 401 Unauthorized - "Session expired, please login" |
| Invalid refresh token | Refresh token revoked or expired | 401 Unauthorized - "Re-authentication required" |
| Missing scopes | User didn't grant required scopes | 403 Forbidden - "Insufficient permissions" |

---

## Future Enhancements (Post-MVP)

1. **Multi-Session Support**
   - Allow users to be logged in on multiple devices
   - Session management dashboard

2. **Remember Me**
   - Extended session expiry for "remember me" option
   - Separate long-lived tokens

3. **SSO Integration**
   - Support for SAML or other SSO providers
   - Multi-tenant with different auth providers

4. **2FA Support**
   - If Laserfiche adds 2FA support

5. **Audit Logging**
   - Track all authentication events
   - User login history

---

## Related Documentation

- [STATUS.md](STATUS.md) - Current feature status
- [TODO.md](TODO.md) - Detailed task breakdown
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Technical implementation details
- [../../_core/architecture.md](../../_core/architecture.md) - System architecture
- [../../_core/data_models.md](../../_core/data_models.md) - Database schema
- [../../_security/SECURITY_ANALYSIS.md](../../_security/SECURITY_ANALYSIS.md) - Security analysis

---

**Last Updated:** 2025-11-18
**Next Review:** After implementation
