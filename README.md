# LFDataView Community Edition

A free, open-source, self-hosted web application for viewing Laserfiche Cloud lookup tables.

## Community Edition Features

- Browse and search Laserfiche lookup tables
- View table rows with pagination (beyond LF's UI limits)
- Server-side and client-side filtering
- Sort and paginate through large tables
- Export to CSV
- Basic table metadata
- OAuth 2.0 authentication with Laserfiche Cloud

**This is a read-only edition.** For write capabilities (add, edit, delete rows, CSV import), check out **LFDataView Managed**.

## Security & Privacy

**Your credentials stay with Laserfiche.** This application:

- **Does not store passwords** - Authentication is handled entirely by Laserfiche Cloud via OAuth 2.0. Your password is never sent to or seen by this application.
- **Does not have a database** - No user accounts, profiles, or personal information are stored.
- **Only stores a temporary access token** - After you log in through Laserfiche, an encrypted access token is stored in a browser cookie for ~1 hour. This token is encrypted and cannot be read by JavaScript.

When you log out or close your browser, the token is cleared. There is no persistent user data.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- A Laserfiche Cloud account
- A registered app in the [Laserfiche Developer Console](https://developers.laserfiche.com/)

### 1. Register Your Laserfiche App

1. Go to [developers.laserfiche.com](https://developers.laserfiche.com/)
2. Create a new **Web App**
3. Set **Redirect URI** to: `http://localhost:8000/auth/callback`
4. Add scopes: `table.Read`, `project/{YOUR_PROJECT}`
5. Save your **Client ID** and **Client Secret**

### 2. Configure Environment

```bash
# Clone the repository
git clone https://github.com/ABEVIntegrations/lfdataview.git
cd lfdataview

# Copy the example environment file
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your credentials:

```bash
# Your Laserfiche app credentials
LASERFICHE_CLIENT_ID=your_client_id
LASERFICHE_CLIENT_SECRET=your_client_secret
LASERFICHE_REDIRECT_URI=http://localhost:8000/auth/callback

# Generate these keys (instructions below)
SECRET_KEY=your_secret_key
TOKEN_ENCRYPTION_KEY=your_fernet_key
```

Generate the security keys:

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate TOKEN_ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Start the Application

```bash
docker-compose up -d
```

### 4. Access the App

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs (development mode only)

Click "Login with Laserfiche" to authenticate and start viewing your tables.

## Architecture

LFDataView uses a stateless architecture with no database required:

- **Frontend:** React 18, Material-UI, React Query
- **Backend:** FastAPI (Python 3.11)
- **Auth:** OAuth 2.0 tokens stored in encrypted httpOnly cookies
- **Deployment:** 2 Docker containers (backend + frontend)

## Documentation

- [Self-Hosting Guide](docs/_deployment/SELF_HOSTING_GUIDE.md) - Production deployment with HTTPS
- [API Reference](docs/_api/API_REFERENCE.md) - Backend API endpoints
- [Architecture](docs/_core/architecture.md) - System design overview

## Environment Variables

| Variable | Description |
|----------|-------------|
| `LASERFICHE_CLIENT_ID` | OAuth Client ID from Developer Console |
| `LASERFICHE_CLIENT_SECRET` | OAuth Client Secret |
| `LASERFICHE_REDIRECT_URI` | OAuth callback URL |
| `SECRET_KEY` | Signs OAuth state cookies (use `openssl rand -hex 32`) |
| `TOKEN_ENCRYPTION_KEY` | Encrypts access tokens (use Fernet.generate_key()) |
| `ALLOWED_ORIGINS` | CORS origins (e.g., `http://localhost:3000`) |
| `ENVIRONMENT` | `development` or `production` |

## Editions

| Feature | Community Edition | Managed Edition |
|---------|-------------------|-----------------|
| View tables | Yes | Yes |
| Search & filter | Yes | Yes |
| Pagination | Yes | Yes |
| CSV export | Yes | Yes |
| Add/Edit/Delete rows | No | Yes |
| CSV import | No | Yes |
| Bulk operations | No | Yes |
| Support | Community | Professional |

## License

MIT License - see [LICENSE](LICENSE)

## Support

- [GitHub Issues](https://github.com/ABEVIntegrations/lfdataview/issues)
- [Documentation](docs/)
