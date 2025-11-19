# System Architecture

**Last Updated:** 2025-11-18
**Status:** Planning Phase
**Version:** 1.0 (Single-Tenant MVP)

---

## Overview

Laserfiche Data View is a self-hosted web application that provides a user interface for viewing and managing Laserfiche lookup table data. The application uses OAuth 2.0 for secure authentication and the Laserfiche OData Table API for data operations.

**Deployment Model:**
- **Phase 1 (MVP):** Single-tenant, self-hosted - Each organization deploys their own instance
- **Phase 2 (Future):** Multi-tenant SaaS option on roadmap

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          User's Browser                          │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │                                                         │      │
│  │              React SPA (Frontend)                       │      │
│  │                                                         │      │
│  │  - OAuth callback handling                             │      │
│  │  - Table browsing UI                                   │      │
│  │  - CRUD forms (create, update, delete)                │      │
│  │  - Error display                                       │      │
│  │                                                         │      │
│  └───────────────────────────────────────────────────────┘      │
│         │                                          ▲              │
│         │ HTTP/HTTPS                               │              │
│         ▼                                          │              │
└─────────────────────────────────────────────────────────────────┘
          │                                          │
          │ 1. OAuth redirect                        │ 4. Access token in
          │    (user → Laserfiche)                   │    Authorization header
          │                                          │
          ▼                                          │
┌─────────────────────────────────────────────────────────────────┐
│                    Laserfiche Cloud                              │
│                                                                   │
│  - signin.laserfiche.com (OAuth server)                          │
│  - api.laserfiche.com/odata4 (OData Table API)                   │
│                                                                   │
│  2. User authenticates                                           │
│  3. Returns authorization code                                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
          │                                          ▲
          │                                          │
          ▼                                          │
┌─────────────────────────────────────────────────────────────────┐
│                    Your Server (Docker Host)                     │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │                                                         │      │
│  │            FastAPI Backend (Python)                     │      │
│  │                                                         │      │
│  │  Endpoints:                                            │      │
│  │  - /auth/login (redirect to Laserfiche)               │      │
│  │  - /auth/callback (receive OAuth code)                │      │
│  │  - /auth/logout (clear session)                       │      │
│  │  - /auth/me (current user info)                       │      │
│  │  - /tables (list available tables)                    │      │
│  │  - /tables/{name} (CRUD operations)                   │      │
│  │                                                         │      │
│  │  Responsibilities:                                     │      │
│  │  - OAuth token exchange (code → access_token)         │      │
│  │  - Token refresh (when access_token expires)          │      │
│  │  - Session management                                 │      │
│  │  - Proxy OData API requests                           │      │
│  │  - Error handling & transformation                    │      │
│  │                                                         │      │
│  └───────────────────────────────────────────────────────┘      │
│         │                                          ▲              │
│         │                                          │              │
│         ▼                                          │              │
│  ┌───────────────────────────────────────────────────────┐      │
│  │                                                         │      │
│  │              PostgreSQL Database                        │      │
│  │                                                         │      │
│  │  Tables:                                               │      │
│  │  - users (user info from Laserfiche)                   │      │
│  │  - sessions (session tracking)                         │      │
│  │  - tokens (access_token, refresh_token, expiry)        │      │
│  │  - projects (cached project-scope mappings)            │      │
│  │                                                         │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend: FastAPI (Python)

**Why FastAPI:**
- High performance (comparable to Node.js and Go)
- Automatic API documentation (OpenAPI/Swagger)
- Built-in request/response validation with Pydantic
- Excellent async support (needed for proxying API calls)
- Type hints and modern Python features
- Easy to test and maintain

**Key Libraries:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM for PostgreSQL
- `alembic` - Database migrations
- `pydantic` - Data validation
- `httpx` - Async HTTP client for Laserfiche API calls
- `python-jose` or `authlib` - OAuth/JWT handling
- `python-multipart` - Form data handling
- `passlib` - Password hashing (if needed for future features)

### Frontend: React SPA

**Why React SPA:**
- Modern, component-based UI development
- Large ecosystem and community
- Excellent tooling (Vite, Create React App)
- Clear separation of concerns (backend API, frontend UI)
- Can be served statically or by FastAPI

**Key Libraries (tentative):**
- `react` + `react-dom` - Core framework
- `react-router-dom` - Client-side routing
- `axios` or `fetch` - API calls to FastAPI backend
- `react-query` or `swr` - Server state management
- UI library: TBD (Material-UI, Ant Design, Chakra UI, or custom)
- Form handling: TBD (React Hook Form, Formik, or native)

**Frontend Structure Options:**
1. **Separate deployment:** React build served by Nginx/Caddy, calls FastAPI API
2. **FastAPI serves SPA:** FastAPI serves React build at `/` and API at `/api/*`

Decision: TBD during implementation

### Database: PostgreSQL

**Why PostgreSQL:**
- Robust, production-ready relational database
- Excellent support for JSON data (for storing token metadata)
- ACID compliance
- Strong SQLAlchemy integration
- Free and open-source
- Easy to containerize with Docker

**Data Storage:**
- User sessions (session_id, user_id, created_at, expires_at)
- OAuth tokens (access_token, refresh_token, expires_at, scopes)
- User information from Laserfiche (user_id, username, email)
- Project-scope mappings (cached for performance)

See [data_models.md](data_models.md) for detailed schema.

### External APIs: Laserfiche

**OAuth Server:**
- `https://signin.laserfiche.com/oauth/Authorize` - User authorization
- `https://signin.laserfiche.com/oauth/Token` - Token exchange and refresh

**OData Table API:**
- `https://api.laserfiche.com/odata4/table` - Table operations
- Requires `Authorization: Bearer {access_token}` header
- Project-based security enforced

---

## Request Flow: OAuth Authentication

### Initial Login Flow

```
1. User visits React SPA → not authenticated → redirects to /auth/login

2. Frontend: GET /auth/login (FastAPI endpoint)
   ├─ FastAPI generates random `state` parameter (CSRF protection)
   ├─ Stores state in session/database
   └─ Returns redirect URL to frontend

3. Frontend redirects user to:
   https://signin.laserfiche.com/oauth/Authorize?
     client_id={YOUR_CLIENT_ID}
     &redirect_uri={YOUR_CALLBACK_URL}
     &response_type=code
     &scope=table.Read table.Write project/{PROJECT_NAME}
     &state={STATE_PARAMETER}

4. User authenticates on Laserfiche:
   ├─ Enters username/password
   ├─ Grants permissions to the app
   └─ Laserfiche redirects to: {YOUR_CALLBACK_URL}?code={AUTH_CODE}&state={STATE}

5. Frontend: Receives redirect, extracts code and state
   ├─ Calls FastAPI: POST /auth/callback { code, state }

6. FastAPI: Processes callback
   ├─ Validates state parameter (CSRF check)
   ├─ Exchanges code for access_token:
   │   POST https://signin.laserfiche.com/oauth/Token
   │   Authorization: Basic {base64(client_id:client_secret)}
   │   Body: { grant_type: "authorization_code", code: {AUTH_CODE} }
   │
   ├─ Receives response: { access_token, refresh_token, expires_in, token_type }
   ├─ Stores tokens in PostgreSQL (tokens table)
   ├─ Creates session record
   └─ Returns session token to frontend (JWT or session ID)

7. Frontend: Stores session token
   ├─ In memory + httpOnly cookie (most secure)
   └─ Redirects user to main app page

8. User is authenticated ✅
```

### Subsequent Authenticated Requests

```
1. Frontend: Makes API call with session token
   GET /tables
   Cookie: session_token={JWT_OR_SESSION_ID}

2. FastAPI: Validates session
   ├─ Checks session token from cookie
   ├─ Looks up user session in PostgreSQL
   ├─ Retrieves access_token for this user
   ├─ Checks if access_token is expired
   │   ├─ If expired: Use refresh_token to get new access_token
   │   └─ If valid: Proceed
   │
   └─ Makes request to Laserfiche API:
       GET https://api.laserfiche.com/odata4/table
       Authorization: Bearer {access_token}

3. Laserfiche API: Returns table list

4. FastAPI: Transforms response (if needed)
   └─ Returns to frontend

5. Frontend: Displays data to user
```

### Token Refresh Flow (Automatic)

```
1. FastAPI detects access_token is expired or about to expire

2. FastAPI: Refreshes token
   POST https://signin.laserfiche.com/oauth/Token
   Authorization: Basic {base64(client_id:client_secret)}
   Body: { grant_type: "refresh_token", refresh_token: {REFRESH_TOKEN} }

3. Receives new access_token (and potentially new refresh_token)

4. Updates tokens table in PostgreSQL

5. Continues with original request using new access_token

6. User experiences no interruption ✅
```

---

## Request Flow: Table CRUD Operations

### Read Tables List

```
User → Frontend → GET /tables → FastAPI → GET /odata4/table → Laserfiche
                                    ↓
                                PostgreSQL (session validation)
                                    ↓
Frontend ← FastAPI ← Laserfiche API (table list)
```

### Read Table Rows

```
User → Frontend → GET /tables/{tableName} → FastAPI → GET /odata4/table/{tableName} → Laserfiche
                                              ↓
                                        PostgreSQL (session)
                                              ↓
Frontend ← FastAPI ← Laserfiche (rows data)
```

### Create Row

```
User → Frontend → POST /tables/{tableName} → FastAPI → POST /odata4/table/{tableName} → Laserfiche
         Body: { field1: value1, field2: value2, ... }
                                               ↓
                                         PostgreSQL (session)
                                               ↓
Frontend ← FastAPI ← Laserfiche (created row)
```

### Update Row

```
User → Frontend → PATCH /tables/{tableName}/{key} → FastAPI → PATCH /odata4/table/{tableName}('{key}') → Laserfiche
         Body: { field1: newValue1, ... }
         Header: If-Match: * (for update, not upsert)
                                                       ↓
                                                 PostgreSQL (session)
                                                       ↓
Frontend ← FastAPI ← Laserfiche (updated row)
```

### Delete Row

```
User → Frontend → DELETE /tables/{tableName}/{key} → FastAPI → DELETE /odata4/table/{tableName}('{key}') → Laserfiche
                                                       ↓
                                                 PostgreSQL (session)
                                                       ↓
Frontend ← FastAPI ← Laserfiche (204 No Content)
```

---

## Security Architecture

### Authentication & Authorization

1. **OAuth 2.0 Authorization Code Flow**
   - Industry standard, secure for web applications
   - Client secret stored server-side only (never exposed to browser)
   - Short-lived authorization code (10 minutes)

2. **CSRF Protection**
   - `state` parameter in OAuth flow (random UUID)
   - Stored in backend session, validated on callback
   - Prevents authorization code interception attacks

3. **Session Management**
   - Session tokens stored in httpOnly cookies (XSS protection)
   - Session data in PostgreSQL with expiration
   - Secure flag for HTTPS-only cookies (production)

4. **Token Storage**
   - Access tokens and refresh tokens in PostgreSQL
   - Never sent to frontend (backend-only)
   - Consider encryption at rest for sensitive tokens

5. **API Authorization**
   - All Laserfiche API calls authenticated with Bearer token
   - Scopes validated on Laserfiche side
   - User permissions enforced by Laserfiche (table rights)

### Transport Security

1. **HTTPS Enforcement**
   - Development: Self-signed certificate or HTTP (localhost only)
   - Production: Valid TLS certificate (Let's Encrypt, commercial CA)
   - HSTS header recommended for production

2. **CORS Configuration**
   - If SPA served separately from FastAPI:
     - Whitelist SPA origin only
     - Credentials allowed (cookies)
   - If SPA served by FastAPI: CORS not needed

### Secrets Management

1. **Environment Variables**
   - `LASERFICHE_CLIENT_ID` - OAuth app client ID
   - `LASERFICHE_CLIENT_SECRET` - OAuth app secret (sensitive)
   - `LASERFICHE_REDIRECT_URI` - Callback URL
   - `DATABASE_URL` - PostgreSQL connection string (sensitive)
   - `SECRET_KEY` - Session encryption key (sensitive)

2. **Storage:**
   - Development: `.env` file (git-ignored)
   - Production: Docker secrets, environment variables, or secrets manager

See [_security/SECURITY_ANALYSIS.md](../_security/SECURITY_ANALYSIS.md) for detailed security analysis.

---

## Deployment Architecture (Phase 1: Single-Tenant)

### Docker Compose Setup

```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: lfdataview
      POSTGRES_USER: lfdataview
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://lfdataview:${DB_PASSWORD}@postgres/lfdataview
      LASERFICHE_CLIENT_ID: ${LASERFICHE_CLIENT_ID}
      LASERFICHE_CLIENT_SECRET: ${LASERFICHE_CLIENT_SECRET}
      LASERFICHE_REDIRECT_URI: ${LASERFICHE_REDIRECT_URI}
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - postgres
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    # OR: Served by backend, no separate service needed
```

**Deployment Steps:**
1. User clones GitHub repository
2. User registers Laserfiche app in Developer Console
3. User creates `.env` file with credentials
4. User runs `docker-compose up -d`
5. Application available at `http://localhost:3000` (or configured domain)

See [_deployment/DOCKER.md](../_deployment/DOCKER.md) for detailed setup.

---

## Scalability Considerations

### Phase 1 (Single-Tenant MVP)
- **Expected load:** Low (single organization, <50 users)
- **Scaling strategy:** Vertical scaling (more CPU/RAM for Docker host)
- **Database:** Single PostgreSQL instance sufficient
- **Caching:** Minimal (consider caching table schemas if needed)

### Phase 2 (Multi-Tenant SaaS)
- **Expected load:** Medium to high (multiple organizations, 100s of users)
- **Scaling strategy:**
  - Horizontal scaling (multiple FastAPI instances behind load balancer)
  - PostgreSQL read replicas
  - Redis for session caching and token storage
  - CDN for static assets
- **Tenant isolation:**
  - Row-level security in PostgreSQL (tenant_id column)
  - Separate Laserfiche app registrations per tenant (or shared with scoping)
- **Monitoring:** Application monitoring, error tracking, usage metrics

---

## Error Handling Strategy

### Backend (FastAPI)

1. **HTTP Error Codes:**
   - `400 Bad Request` - Invalid input data
   - `401 Unauthorized` - Missing or invalid session
   - `403 Forbidden` - Insufficient Laserfiche permissions
   - `404 Not Found` - Table/row not found
   - `500 Internal Server Error` - Unexpected errors

2. **Laserfiche API Errors:**
   - Catch and transform Laserfiche API errors
   - Add context for frontend display
   - Log errors for debugging

3. **Token Expiration:**
   - Automatically refresh access_token if refresh_token valid
   - If refresh_token expired: Return 401, trigger re-authentication
   - Transparent to user when possible

### Frontend (React)

1. **API Error Display:**
   - User-friendly error messages
   - Specific guidance for 403 errors (contact admin for permissions)
   - Retry mechanisms for transient errors

2. **Loading States:**
   - Spinner/skeleton screens during API calls
   - Disable forms during submission

3. **Offline Handling:**
   - Detect network errors
   - Show "connection lost" message
   - Allow retry when online

---

## Performance Considerations

1. **Database:**
   - Indexes on session_id, user_id, token_id
   - Connection pooling (SQLAlchemy default)
   - Query optimization (select only needed columns)

2. **API Calls:**
   - Minimize round trips to Laserfiche API
   - Use OData query parameters ($select, $filter, $top) efficiently
   - Consider caching frequently accessed data (table schemas)

3. **Frontend:**
   - Lazy loading for large table data
   - Pagination for table rows
   - Code splitting for React bundles

---

## Future Enhancements (Post-MVP)

### Phase 2: Multi-Tenancy
- Tenant onboarding flow
- Subdomain-based tenant identification
- Tenant admin dashboard
- Usage billing/metering

### Phase 3: Advanced Features
- Bulk operations (import CSV, export Excel)
- Advanced filtering and sorting
- Data visualization (charts, graphs)
- Audit logging (who changed what, when)
- Webhooks (notify external systems on data changes)
- Mobile-responsive design improvements

---

## Development Workflow

1. **Local Development:**
   - Run Docker Compose for PostgreSQL
   - Run FastAPI with `uvicorn --reload` for hot reload
   - Run React with `npm run dev` for hot reload
   - Use Laserfiche sandbox/test environment

2. **Testing:**
   - Backend: pytest for unit/integration tests
   - Frontend: Jest + React Testing Library
   - E2E: Playwright or Cypress

3. **Version Control:**
   - Git repository
   - Feature branches for new features
   - Main branch protected, requires PR review

4. **CI/CD:**
   - GitHub Actions or GitLab CI
   - Run tests on every PR
   - Auto-deploy to staging on main branch merge
   - Manual deploy to production

---

## Monitoring & Observability

### Phase 1 (MVP)
- **Logging:** Python logging to stdout (captured by Docker)
- **Health checks:** `/health` endpoint for Docker health checks
- **Error tracking:** Basic error logs

### Phase 2 (Multi-Tenant)
- **Application monitoring:** Sentry, Datadog, or similar
- **Metrics:** Request rates, latency, error rates
- **Alerting:** On critical errors or downtime
- **User analytics:** Usage patterns, feature adoption

---

## Documentation & Maintenance

1. **Code Documentation:**
   - Python docstrings for all functions
   - OpenAPI docs auto-generated by FastAPI
   - React component documentation (Storybook or similar)

2. **User Documentation:**
   - Self-hosting guide
   - Admin configuration guide
   - End-user manual (how to use the UI)

3. **Maintenance:**
   - Dependency updates (Dependabot or Renovate)
   - Security patches
   - Database migrations with Alembic

---

**Last Updated:** 2025-11-18
**Next Review:** After Feature 01 implementation
**Version:** 1.0 (Single-Tenant MVP Architecture)
