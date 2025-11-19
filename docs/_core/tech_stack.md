# Technology Stack

**Last Updated:** 2025-11-18
**Status:** Planning Phase
**Deployment Target:** Self-hosted Docker containers

---

## Overview

This document provides detailed rationale for technology choices in the Laserfiche Data View application.

---

## Backend: FastAPI (Python 3.11+)

### Why FastAPI?

| Criterion | Evaluation |
|-----------|------------|
| **Performance** | High-performance async framework, comparable to Node.js and Go |
| **Developer Experience** | Excellent DX with automatic API docs, type hints, and validation |
| **Async Support** | Native async/await for efficient I/O (API calls to Laserfiche) |
| **API Documentation** | Auto-generates OpenAPI (Swagger) and ReDoc documentation |
| **Type Safety** | Built-in with Pydantic models and Python type hints |
| **Learning Curve** | Moderate - requires Python knowledge and async understanding |
| **Ecosystem** | Rich ecosystem for OAuth, database ORMs, testing |
| **Production Ready** | Used by Microsoft, Uber, Netflix for production services |

### Key Dependencies

```toml
# pyproject.toml or requirements.txt

# Core Framework
fastapi = "^0.104.0"           # Web framework
uvicorn[standard] = "^0.24.0"  # ASGI server with WebSocket support
pydantic = "^2.4.0"            # Data validation
pydantic-settings = "^2.0.0"   # Settings management from env vars

# Database
sqlalchemy = "^2.0.22"         # ORM
alembic = "^1.12.0"            # Database migrations
psycopg2-binary = "^2.9.9"     # PostgreSQL driver
# OR: asyncpg = "^0.29.0"      # Async PostgreSQL driver (if using async SQLAlchemy)

# OAuth & Security
authlib = "^1.2.1"             # OAuth 2.0 client
python-jose[cryptography] = "^3.3.0"  # JWT handling
passlib[bcrypt] = "^1.7.4"     # Password hashing (future use)
cryptography = "^41.0.5"       # Token encryption

# HTTP Client
httpx = "^0.25.0"              # Async HTTP client for Laserfiche API calls

# CORS
python-multipart = "^0.0.6"    # Form data parsing

# Testing
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
httpx-mock = "^0.14.0"         # Mock HTTP requests in tests

# Development
black = "^23.10.0"             # Code formatting
ruff = "^0.1.3"                # Fast linter (replaces flake8, pylint)
mypy = "^1.6.0"                # Static type checking
pre-commit = "^3.5.0"          # Git hooks
```

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings (from env vars)
│   ├── database.py             # Database connection, session management
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── session.py
│   │   ├── token.py
│   │   └── oauth_state.py
│   │
│   ├── schemas/                # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── table.py
│   │   └── user.py
│   │
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py             # /auth/* endpoints
│   │   └── tables.py           # /tables/* endpoints
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py     # OAuth flow, token management
│   │   └── table_service.py    # Laserfiche API calls
│   │
│   ├── utils/                  # Utilities
│   │   ├── __init__.py
│   │   ├── security.py         # Token encryption, CSRF
│   │   └── laserfiche.py       # Laserfiche API client
│   │
│   └── dependencies.py         # FastAPI dependencies (DB session, current user, etc.)
│
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   └── test_tables.py
│
├── alembic.ini                 # Alembic config
├── pyproject.toml              # Python dependencies and project metadata
├── Dockerfile                  # Docker image for backend
└── .env.example                # Example environment variables
```

---

## Frontend: React SPA (React 18+)

### Why React?

| Criterion | Evaluation |
|-----------|------------|
| **Popularity** | Most popular UI framework, large community |
| **Ecosystem** | Mature ecosystem for routing, state, UI components |
| **Component Reusability** | Excellent component model |
| **Performance** | Virtual DOM, efficient updates |
| **Developer Tools** | React DevTools, extensive debugging support |
| **Hiring** | Easier to find React developers |
| **Alternatives** | Vue (simpler), Angular (opinionated), Svelte (smaller bundle) |

**Decision:** React chosen for balance of features, ecosystem, and community support. Can be swapped for Vue or Angular if preferred.

### Key Dependencies

```json
// package.json

{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.18.0",   // Client-side routing
    "axios": "^1.6.0",                 // HTTP client (or use fetch)
    "@tanstack/react-query": "^5.8.0", // Server state management
    // UI Library (choose one):
    // "@mui/material": "^5.14.0",     // Material-UI (option 1)
    // "antd": "^5.11.0",              // Ant Design (option 2)
    // "@chakra-ui/react": "^2.8.0",   // Chakra UI (option 3)
    // OR: Custom CSS/TailwindCSS
  },
  "devDependencies": {
    "vite": "^5.0.0",                  // Build tool (faster than CRA)
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.2.0",            // Optional but recommended
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "eslint": "^8.53.0",
    "prettier": "^3.0.0",
    "vitest": "^0.34.0",               // Testing framework
    "@testing-library/react": "^14.1.0",
    "@testing-library/jest-dom": "^6.1.0",
    "playwright": "^1.40.0"            // E2E testing (optional)
  }
}
```

### Project Structure

```
frontend/
├── public/
│   └── index.html
│
├── src/
│   ├── main.tsx                # App entry point
│   ├── App.tsx                 # Root component
│   ├── router.tsx              # React Router configuration
│   │
│   ├── pages/                  # Page components
│   │   ├── LoginPage.tsx
│   │   ├── CallbackPage.tsx    # OAuth callback handler
│   │   ├── TablesPage.tsx      # Table list
│   │   └── TableDetailPage.tsx # Table CRUD view
│   │
│   ├── components/             # Reusable components
│   │   ├── Layout.tsx          # App layout (header, nav, footer)
│   │   ├── TableList.tsx
│   │   ├── TableRow.tsx
│   │   └── ErrorBoundary.tsx
│   │
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAuth.ts          # Authentication state
│   │   └── useTable.ts         # Table data fetching
│   │
│   ├── services/               # API client
│   │   └── api.ts              # Axios instance, API calls to FastAPI
│   │
│   ├── types/                  # TypeScript types
│   │   ├── auth.ts
│   │   └── table.ts
│   │
│   ├── utils/                  # Utilities
│   │   └── formatters.ts
│   │
│   └── styles/                 # Global styles (if not using UI library)
│       └── global.css
│
├── tests/
│   └── App.test.tsx
│
├── package.json
├── vite.config.ts              # Vite configuration
├── tsconfig.json               # TypeScript config
├── Dockerfile                  # Docker image for frontend (if served separately)
└── .env.example
```

### Build Tool: Vite

**Why Vite over Create React App (CRA)?**
- Faster development server (instant hot module reload)
- Faster builds (using esbuild and Rollup)
- Better TypeScript support
- More modern and actively maintained
- Smaller bundle sizes

---

## Database: PostgreSQL 15+

### Why PostgreSQL?

| Criterion | Evaluation |
|-----------|------------|
| **Reliability** | ACID-compliant, production-tested for decades |
| **JSON Support** | Native JSONB for storing scopes, metadata |
| **Performance** | Excellent query performance with proper indexing |
| **Extensions** | pgcrypto for encryption, UUID support |
| **ORM Support** | Excellent SQLAlchemy integration |
| **Licensing** | Open-source (PostgreSQL License) |
| **Alternatives** | MySQL (less JSON support), SQLite (not multi-user) |

### Configuration

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: lfdataview
      POSTGRES_USER: lfdataview
      POSTGRES_PASSWORD: ${DB_PASSWORD}  # From .env file
      POSTGRES_INITDB_ARGS: "-E UTF8"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"  # Expose for local dev (remove in production)
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U lfdataview"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

---

## External APIs: Laserfiche Cloud

### OAuth Endpoints

- **Authorization:** `https://signin.laserfiche.com/oauth/Authorize`
- **Token Exchange:** `https://signin.laserfiche.com/oauth/Token`

### OData Table API

- **Base URL:** `https://api.laserfiche.com/odata4`
- **Endpoints:**
  - `GET /table` - List tables
  - `GET /table/{tableName}` - Read rows
  - `POST /table/{tableName}` - Create row
  - `PATCH /table/{tableName}('{key}')` - Update row
  - `DELETE /table/{tableName}('{key}')` - Delete row

### Rate Limits
- To be determined (check Laserfiche documentation)
- Implement exponential backoff for retries
- Consider caching frequently accessed data

---

## Development Tools

### Version Control: Git + GitHub

```bash
# .gitignore essentials
.env
*.pyc
__pycache__/
node_modules/
dist/
build/
.venv/
.pytest_cache/
.mypy_cache/
```

### Code Quality

**Backend (Python):**
- **Black:** Code formatting (opinionated, no config needed)
- **Ruff:** Fast linting (replaces flake8, isort, pylint)
- **mypy:** Static type checking
- **pre-commit:** Run checks before commits

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.10.0
    hooks:
      - id: black
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.3
    hooks:
      - id: ruff
```

**Frontend (React):**
- **ESLint:** Linting
- **Prettier:** Code formatting
- **TypeScript:** Type safety

### Testing

**Backend:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

**Frontend:**
```bash
# Unit tests (Vitest)
npm run test

# E2E tests (Playwright)
npx playwright test
```

---

## Deployment

### Containerization: Docker + Docker Compose

**Why Docker?**
- Consistent environment (dev, staging, prod)
- Easy deployment (single command)
- Dependency isolation
- Portable across platforms

**Docker Compose Services:**

```yaml
services:
  postgres:
    # See above

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://lfdataview:${DB_PASSWORD}@postgres/lfdataview
      LASERFICHE_CLIENT_ID: ${LASERFICHE_CLIENT_ID}
      LASERFICHE_CLIENT_SECRET: ${LASERFICHE_CLIENT_SECRET}
      LASERFICHE_REDIRECT_URI: ${LASERFICHE_REDIRECT_URI}
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "8000:8000"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"  # Nginx serving React build
    depends_on:
      - backend
```

### Reverse Proxy: Nginx or Caddy

**Option 1: Nginx (Traditional)**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Serve React SPA
    location / {
        root /usr/share/nginx/html;
        try_files $uri /index.html;
    }

    # Proxy API requests to FastAPI
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Option 2: Caddy (Modern, auto-HTTPS)**
```caddyfile
yourdomain.com {
    # Serve React SPA
    root * /usr/share/caddy
    try_files {path} /index.html
    file_server

    # Proxy API requests to FastAPI
    reverse_proxy /api/* backend:8000
}
```

**Decision:** Caddy recommended for automatic HTTPS (Let's Encrypt)

---

## CI/CD (Future Enhancement)

### GitHub Actions (Proposed)

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm run test
```

---

## Monitoring & Logging (Future)

### Logging

**Backend:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("User authenticated", extra={"user_id": user.id})
```

**Frontend:**
```typescript
// Simple console logging for MVP
console.log('[Auth]', 'User logged in', { userId })

// Future: Integrate with Sentry, LogRocket, etc.
```

### Error Tracking

**Phase 2:** Integrate Sentry
- Backend: `sentry-sdk` for Python
- Frontend: `@sentry/react`

---

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://lfdataview:password@localhost:5432/lfdataview

# Laserfiche OAuth
LASERFICHE_CLIENT_ID=your_client_id_here
LASERFICHE_CLIENT_SECRET=your_client_secret_here
LASERFICHE_REDIRECT_URI=http://localhost:8000/auth/callback

# Security
SECRET_KEY=your_random_secret_key_here_use_openssl_rand_hex_32
TOKEN_ENCRYPTION_KEY=your_fernet_key_here_use_Fernet_generate_key

# App Config
DEBUG=true  # Set to false in production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173  # CORS origins
SESSION_EXPIRY_DAYS=7
```

### Frontend (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000  # FastAPI backend URL
```

---

## Development Environment Setup

### Prerequisites

- **Python:** 3.11+
- **Node.js:** 18+ (LTS)
- **Docker:** 20.10+
- **Docker Compose:** 2.0+
- **PostgreSQL:** 15+ (via Docker or local install)

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/yourusername/lfdataview.git
cd lfdataview

# 2. Set up environment variables
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit .env files with your Laserfiche app credentials

# 3. Start services with Docker Compose
docker-compose up -d

# 4. Access application
# Frontend: http://localhost:3000
# Backend API docs: http://localhost:8000/docs
```

---

## Alternatives Considered

### Backend Alternatives

| Framework | Pros | Cons | Decision |
|-----------|------|------|----------|
| **Django** | Full-featured, admin panel, ORM | Heavier, more opinionated | ❌ Too heavyweight for API-only |
| **Flask** | Lightweight, flexible | Less async support, manual setup | ❌ Less modern than FastAPI |
| **Node.js (Express)** | JavaScript everywhere | Callback hell, weaker typing | ❌ Prefer Python ecosystem |

### Frontend Alternatives

| Framework | Pros | Cons | Decision |
|-----------|------|------|----------|
| **Vue** | Simpler than React, good docs | Smaller ecosystem | ✅ Valid alternative |
| **Angular** | Full framework, TypeScript first | Steeper learning curve | ❌ Overkill for this app |
| **Svelte** | Smaller bundles, simpler syntax | Smaller ecosystem | ❌ Less mature |

### Database Alternatives

| Database | Pros | Cons | Decision |
|----------|------|------|----------|
| **MySQL** | Popular, good performance | Weaker JSON support | ❌ PostgreSQL better for this use case |
| **SQLite** | Simple, file-based | Not suitable for multi-user | ❌ Not production-ready for web apps |
| **MongoDB** | NoSQL, flexible schema | Not ACID, overkill | ❌ Relational data fits SQL better |

---

## Summary

**Tech Stack (Final Decision):**

- **Backend:** FastAPI 0.104+ (Python 3.11+)
- **Frontend:** React 18+ with Vite
- **Database:** PostgreSQL 15+
- **Deployment:** Docker + Docker Compose
- **Reverse Proxy:** Caddy (auto-HTTPS)
- **Version Control:** Git + GitHub

**Why This Stack?**
1. **Modern & Performant:** Async backend, fast frontend builds
2. **Type-Safe:** Pydantic + TypeScript for fewer runtime errors
3. **Developer Experience:** Auto-generated API docs, hot reload, easy testing
4. **Production-Ready:** Proven technologies used by major companies
5. **Self-Hostable:** Simple Docker deployment for single-tenant use case
6. **Scalable:** Can scale to multi-tenant SaaS in Phase 2

---

**Last Updated:** 2025-11-18
**Next Review:** After initial implementation
**Version:** 1.0
