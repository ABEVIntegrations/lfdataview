# Laserfiche Data View

A self-hosted web application for viewing and managing Laserfiche lookup table data using OAuth 2.0 and the OData Table API.

## Quick Start

### Prerequisites

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Laserfiche Developer Console** account
- **Python** 3.11+ (for local development without Docker)
- **Node.js** 18+ (for frontend development)

### Step 1: Register Laserfiche Application

1. Go to [Laserfiche Developer Console](https://developers.laserfiche.com/)
2. Create a new application
3. Set **Application Type:** Web App
4. Set **Redirect URI:** `http://localhost:8000/auth/callback`
5. Set **Scopes:** `table.Read table.Write project/{YOUR_PROJECT_NAME}`
   - Replace `{YOUR_PROJECT_NAME}` with your actual project name
   - Use `+` instead of spaces (e.g., `project/My+Project`)
6. Save your `client_id` and `client_secret`

### Step 2: Environment Configuration

```bash
# Create environment files from examples
cp .env.example .env
cp backend/.env.example backend/.env

# Edit backend/.env with your credentials
nano backend/.env
```

**Required values in `backend/.env`:**

```bash
# Update these with your Laserfiche app credentials
LASERFICHE_CLIENT_ID=your_client_id_from_step_1
LASERFICHE_CLIENT_SECRET=your_client_secret_from_step_1
LASERFICHE_REDIRECT_URI=http://localhost:8000/auth/callback

# Generate a secret key
SECRET_KEY=$(openssl rand -hex 32)

# Generate token encryption key
# Run: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
TOKEN_ENCRYPTION_KEY=your_generated_fernet_key
```

**Optional: Update `DB_PASSWORD` in root `.env`:**
```bash
DB_PASSWORD=your_strong_database_password
```

### Step 3: Start the Application

```bash
# Start PostgreSQL and backend
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Access API docs
# http://localhost:8000/docs
```

### Step 4: Initialize Database

```bash
# Run database migrations (after models are created)
docker-compose exec backend alembic upgrade head
```

## Project Structure

```
lfdataview/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── utils/        # Utilities
│   │   ├── config.py     # Configuration
│   │   ├── database.py   # Database setup
│   │   └── main.py       # FastAPI app
│   ├── tests/            # Backend tests
│   ├── alembic/          # Database migrations
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile
│
├── frontend/             # React frontend (to be created)
│   └── (React app files)
│
├── docs/                 # Documentation
│   ├── 00-RESUME-HERE.md # Project status
│   ├── README.md         # Docs navigation
│   ├── _core/            # Architecture docs
│   ├── features/         # Feature documentation
│   │   ├── 01-oauth-authentication/
│   │   ├── 02-table-crud-operations/
│   │   └── 03-basic-react-ui/
│   └── _deployment/      # Deployment guides
│
├── docker-compose.yml    # Docker services
└── README.md             # This file
```

## Development

### Backend Development

```bash
# Start backend with hot reload
docker-compose up backend

# Run tests
docker-compose exec backend pytest

# Format code
docker-compose exec backend black app/

# Lint code
docker-compose exec backend ruff app/
```

### Database

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U lfdataview -d lfdataview

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1
```

## Documentation

- **Project Status:** [docs/00-RESUME-HERE.md](docs/00-RESUME-HERE.md)
- **Documentation Guide:** [docs/README.md](docs/README.md)
- **Architecture:** [docs/_core/architecture.md](docs/_core/architecture.md)
- **API Reference:** [docs/_api/API_REFERENCE.md](docs/_api/API_REFERENCE.md)

## Current Status

**Phase:** Development - Feature 01 ✅ COMPLETE | Feature 02 ⚠️ NEEDS TESTING

**Completed:**
- ✅ **Feature 01: OAuth Authentication (100%)**
  - Complete OAuth 2.0 integration with Laserfiche
  - Secure token storage and session management
  - CSRF protection and automatic token refresh
  - 5 working API endpoints
  - Successfully tested end-to-end!
- ⚠️ **Feature 02: Table CRUD Operations (95%)**
  - Extended Laserfiche client for OData Table API
  - 6 table CRUD endpoints (list, get, create, update, delete)
  - Pagination support with limit/offset
  - Authentication + automatic token refresh
  - Comprehensive error handling
  - **Implementation complete - needs user testing!**
- ✅ Project documentation structure
- ✅ Backend scaffolding (FastAPI)
- ✅ Docker Compose setup
- ✅ Database models and migrations
- ✅ Environment configuration

**Next:**
- ⚠️ **Test Feature 02** - See [FEATURE_02_TEST_GUIDE.md](FEATURE_02_TEST_GUIDE.md)
- 📋 Feature 03: Basic React UI

**Quick Start:**
```powershell
cd D:\anthony\projects\lfdataview
docker-compose -f docker-compose.simple.yml up -d
```

**Test OAuth:** http://localhost:8000/test

See [docs/00-RESUME-HERE.md](docs/00-RESUME-HERE.md) for detailed status.

## Tech Stack

- **Backend:** FastAPI (Python 3.11+)
- **Frontend:** React 18+ with Vite
- **Database:** PostgreSQL 15+
- **Deployment:** Docker + Docker Compose
- **OAuth:** Laserfiche OAuth 2.0 Authorization Code Flow

## License

TBD

## Support

For issues or questions:
- Check [docs/README.md](docs/README.md) for documentation
- Review [docs/features/01-oauth-authentication/](docs/features/01-oauth-authentication/) for OAuth setup

---

**Version:** 1.0.0-dev
**Last Updated:** 2025-11-18
