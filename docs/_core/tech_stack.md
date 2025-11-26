# Technology Stack

**Last Updated:** 2025-11-25
**Status:** Production Ready
**Version:** 1.0 (Community Edition - Stateless)

---

## Overview

This document provides detailed rationale for technology choices in LF DataView.

**Key Design Decision:** The Community Edition uses a **stateless architecture** with no database. Authentication state is stored in encrypted httpOnly cookies, making deployment simpler.

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
| **Ecosystem** | Rich ecosystem for OAuth, testing, security |
| **Production Ready** | Used by Microsoft, Uber, Netflix for production services |

### Key Dependencies

```txt
# requirements.txt

# Core Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.4.0
pydantic-settings>=2.0.0

# OAuth & Security
cryptography>=41.0.5       # Fernet token encryption
python-multipart>=0.0.6    # Form data parsing

# HTTP Client
httpx>=0.25.0              # Async HTTP client for Laserfiche API calls

# Development
black>=23.10.0             # Code formatting
ruff>=0.1.3                # Fast linter
```

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings (from env vars)
│   ├── dependencies.py         # FastAPI dependencies (auth from cookies)
│   │
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py             # /auth/* endpoints
│   │   └── tables.py           # /tables/* endpoints
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py     # OAuth flow (stateless)
│   │   └── table_service.py    # Laserfiche API calls
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── security.py         # Token encryption, signed state
│       └── laserfiche.py       # Laserfiche API client
│
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   └── test_tables.py
│
├── requirements.txt
├── Dockerfile
└── .env.example
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

### Key Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.18.0",
    "@tanstack/react-query": "^5.8.0",
    "@mui/material": "^5.14.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.2.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "eslint": "^8.53.0",
    "prettier": "^3.0.0"
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
│   │
│   ├── pages/                  # Page components
│   │   ├── LoginPage.tsx
│   │   ├── TablesPage.tsx
│   │   └── TableDetailPage.tsx
│   │
│   ├── components/             # Reusable components
│   │   ├── Layout.tsx
│   │   ├── TableList.tsx
│   │   └── ErrorBoundary.tsx
│   │
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAuth.ts
│   │   └── useTable.ts
│   │
│   ├── services/               # API client
│   │   └── api.ts
│   │
│   └── types/                  # TypeScript types
│       ├── auth.ts
│       └── table.ts
│
├── package.json
├── vite.config.ts
├── tsconfig.json
├── Dockerfile
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

## Stateless Authentication

### Why No Database?

The Community Edition stores all authentication state in encrypted cookies:

| Benefit | Description |
|---------|-------------|
| **Simple Deployment** | No database to configure, migrate, or backup |
| **Horizontal Scaling** | Any backend instance can handle any request |
| **Fewer Dependencies** | 2 containers instead of 3 |
| **Self-Hosters Love It** | Less infrastructure to manage |

### Cookie-Based Security

| Cookie | Purpose | Security |
|--------|---------|----------|
| `lf_token` | Encrypted Laserfiche access token | Fernet encryption, httpOnly |
| `lf_state` | Signed OAuth state (CSRF protection) | HMAC-SHA256 signed |

### Trade-offs

| Trade-off | Mitigation |
|-----------|------------|
| Tokens expire in ~1 hour | Acceptable for typical usage (quick edits) |
| Can't invalidate server-side | Logout clears cookies; token auto-expires |
| State lost on server restart | Users simply log in again |

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

---

## Deployment

### Docker Compose (2 containers)

```yaml
version: '3.9'
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

### Production: Reverse Proxy with HTTPS

**Caddy (Recommended - auto-HTTPS):**
```caddyfile
yourdomain.com {
    reverse_proxy /auth/* backend:8000
    reverse_proxy /tables/* backend:8000
    reverse_proxy /health backend:8000

    root * /usr/share/caddy
    try_files {path} /index.html
    file_server
}
```

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
```

### Code Quality

**Backend (Python):**
- **Black:** Code formatting
- **Ruff:** Fast linting

**Frontend (React):**
- **ESLint:** Linting
- **Prettier:** Code formatting
- **TypeScript:** Type safety

---

## Environment Variables

### Backend (.env)

```bash
# Laserfiche OAuth
LASERFICHE_CLIENT_ID=your_client_id_here
LASERFICHE_CLIENT_SECRET=your_client_secret_here
LASERFICHE_REDIRECT_URI=http://localhost:8000/auth/callback

# Security
SECRET_KEY=your_random_secret_key_here_use_openssl_rand_hex_32
TOKEN_ENCRYPTION_KEY=your_fernet_key_here_use_Fernet_generate_key

# App Config
DEBUG=true
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000
```

---

## Development Environment Setup

### Prerequisites

- **Python:** 3.11+
- **Node.js:** 18+ (LTS)
- **Docker:** 20.10+
- **Docker Compose:** 2.0+

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

## Summary

**Tech Stack (Community Edition):**

- **Backend:** FastAPI 0.104+ (Python 3.11+)
- **Frontend:** React 18+ with Vite, Material-UI
- **Authentication:** Stateless (encrypted cookies)
- **Deployment:** Docker + Docker Compose (2 containers)
- **Reverse Proxy:** Caddy (auto-HTTPS)
- **Version Control:** Git + GitHub

**Why This Stack?**
1. **Simple:** No database to manage
2. **Modern & Performant:** Async backend, fast frontend builds
3. **Type-Safe:** Pydantic + TypeScript for fewer runtime errors
4. **Developer Experience:** Auto-generated API docs, hot reload
5. **Production-Ready:** Proven technologies
6. **Self-Hostable:** Simple Docker deployment

---

**Version:** 1.0 (Community Edition)
**Last Updated:** 2025-11-25
