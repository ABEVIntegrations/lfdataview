# System Architecture

**Last Updated:** 2025-11-25
**Status:** Production Ready
**Version:** 1.0 (Community Edition - Stateless)

---

## Overview

LF DataView is a self-hosted web application for viewing and managing Laserfiche Cloud lookup tables. It uses OAuth 2.0 for authentication and the Laserfiche OData Table API for data operations.

**Key Design Decision:** The Community Edition uses a **stateless architecture** with no database required. Authentication state is stored in encrypted httpOnly cookies.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          User's Browser                          │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              React SPA (Frontend)                          │  │
│  │                                                            │  │
│  │  - Table browsing with filtering & pagination              │  │
│  │  - CRUD operations (create, update, delete rows)          │  │
│  │  - CSV import/export                                       │  │
│  │  - OAuth login flow                                        │  │
│  └───────────────────────────────────────────────────────────┘  │
│         │                                                        │
│         │ HTTP/HTTPS (cookies: lf_token, lf_state)              │
│         ▼                                                        │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Host (Your Server)                     │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │            FastAPI Backend (Python)                        │  │
│  │                                                            │  │
│  │  Auth Endpoints:                                           │  │
│  │  - GET  /auth/login    → Redirect to Laserfiche OAuth     │  │
│  │  - GET  /auth/callback → Exchange code, set token cookie  │  │
│  │  - POST /auth/logout   → Clear cookies                    │  │
│  │  - GET  /auth/status   → Check if authenticated           │  │
│  │                                                            │  │
│  │  Table Endpoints:                                          │  │
│  │  - GET    /tables                → List tables            │  │
│  │  - GET    /tables/{name}         → Get rows (paginated)   │  │
│  │  - POST   /tables/{name}         → Create row             │  │
│  │  - PATCH  /tables/{name}/{key}   → Update row             │  │
│  │  - DELETE /tables/{name}/{key}   → Delete row             │  │
│  │  - POST   /tables/{name}/batch   → Batch create           │  │
│  │  - POST   /tables/{name}/replace → Replace all rows       │  │
│  │                                                            │  │
│  │  Security:                                                 │  │
│  │  - Fernet encryption for access tokens                    │  │
│  │  - HMAC-signed OAuth state (CSRF protection)              │  │
│  │  - httpOnly cookies (XSS protection)                      │  │
│  │                                                            │  │
│  └───────────────────────────────────────────────────────────┘  │
│         │                                                        │
│         │ HTTPS (Bearer token)                                   │
│         ▼                                                        │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Laserfiche Cloud                              │
│                                                                   │
│  - signin.laserfiche.com (OAuth server)                          │
│  - api.laserfiche.com/odata4/table (OData Table API)            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Stateless Authentication

The Community Edition stores all auth state in cookies - no database required.

### Cookie Structure

| Cookie | Purpose | Encryption | Max Age |
|--------|---------|------------|---------|
| `lf_token` | Encrypted Laserfiche access token | Fernet | ~1 hour |
| `lf_state` | Signed OAuth state (CSRF protection) | HMAC-SHA256 | 10 min |

### OAuth Flow

```
1. User clicks "Login"
   └─ GET /auth/login
      ├─ Generate random state
      ├─ Sign state with HMAC → lf_state cookie
      └─ Return Laserfiche OAuth URL

2. User authenticates on Laserfiche
   └─ Laserfiche redirects to /auth/callback?code=XXX&state=YYY

3. Backend processes callback
   └─ GET /auth/callback
      ├─ Verify state from cookie matches callback state
      ├─ Exchange code for access token
      ├─ Encrypt token with Fernet → lf_token cookie
      ├─ Delete lf_state cookie
      └─ Redirect to frontend

4. Subsequent API requests
   └─ GET /tables (with lf_token cookie)
      ├─ Decrypt token from cookie
      ├─ Call Laserfiche API with Bearer token
      └─ Return data

5. Token expires (~1 hour)
   └─ User must login again
```

### Why Stateless?

| Benefit | Description |
|---------|-------------|
| **Simple Deployment** | No database to configure, migrate, or backup |
| **Horizontal Scaling** | Any backend instance can handle any request |
| **Fewer Dependencies** | 2 containers instead of 3 |
| **Self-Hosters Love It** | Less infrastructure to manage |

### Trade-offs

| Trade-off | Mitigation |
|-----------|------------|
| Tokens expire in ~1 hour | Acceptable for typical usage (quick edits) |
| Can't invalidate server-side | Logout clears cookies; token auto-expires |
| State lost on server restart | Users simply log in again |

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, TypeScript, Material-UI, React Query, Vite |
| **Backend** | Python 3.11, FastAPI, Pydantic, httpx |
| **Security** | Fernet (token encryption), HMAC-SHA256 (state signing) |
| **Deployment** | Docker, Docker Compose |

---

## Request Flow: Table Operations

### Read Table Rows

```
Frontend → GET /tables/{name}?limit=50&offset=0
           Cookie: lf_token=<encrypted>
              │
              ▼
Backend:   Decrypt lf_token → access_token
              │
              ▼
           GET api.laserfiche.com/odata4/table/{name}?$top=50&$skip=0
           Authorization: Bearer {access_token}
              │
              ▼
           Return paginated rows to frontend
```

### CSV Export (Client-Side)

```
Frontend: Fetch all rows (paginated)
          Transform to CSV format
          Trigger browser download
          (No backend involvement for export)
```

### CSV Import (Batch Create)

```
Frontend: Parse CSV file
          POST /tables/{name}/batch
          Body: { rows: [...] }
              │
              ▼
Backend:   For each row, POST to Laserfiche API
           Return success/failure per row
```

---

## Security Architecture

### Authentication

1. **OAuth 2.0 Authorization Code Flow**
   - Client secret stored server-side only
   - Short-lived authorization codes

2. **CSRF Protection**
   - OAuth state parameter signed with HMAC
   - Validated before token exchange

3. **Token Security**
   - Access tokens encrypted with Fernet before cookie storage
   - httpOnly cookies prevent JavaScript access
   - Secure flag enabled in production (HTTPS only)

### Secrets Management

| Secret | Purpose | Storage |
|--------|---------|---------|
| `LASERFICHE_CLIENT_ID` | OAuth app ID | `.env` file |
| `LASERFICHE_CLIENT_SECRET` | OAuth app secret | `.env` file |
| `SECRET_KEY` | Signs OAuth state cookies | `.env` file |
| `TOKEN_ENCRYPTION_KEY` | Encrypts access tokens | `.env` file |

---

## Deployment

### Docker Compose (2 containers)

```yaml
services:
  backend:
    build: ./backend
    env_file: ./backend/.env
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

### Production Considerations

1. **HTTPS Required**
   - Use reverse proxy (Caddy, Nginx) with SSL
   - Set `ENVIRONMENT=production` for secure cookies

2. **Cookie Security**
   - `secure=True` in production (HTTPS only)
   - `samesite=lax` prevents CSRF
   - `httponly=True` prevents XSS token theft

---

## Future: Managed Edition

The Managed Edition (Phase 2) will add:

- PostgreSQL for multi-tenant state
- Subdomain-based tenant routing
- Per-tenant OAuth configuration
- Audit logging
- Admin dashboard

The core API and frontend remain unchanged - only the auth layer is swapped.

---

**Version:** 1.0 (Community Edition)
**Last Updated:** 2025-11-25
