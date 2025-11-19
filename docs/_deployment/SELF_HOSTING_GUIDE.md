# Self-Hosting Guide

**Last Updated:** 2025-11-18

## Overview

Guide for deploying Laserfiche Data View as a single-tenant application on your own server.

## Prerequisites

- Linux server (Ubuntu 22.04 recommended)
- Docker and Docker Compose installed
- Domain name (or IP address)
- Laserfiche Developer Console app registration

## Step 1: Register Laserfiche App

1. Go to [Laserfiche Developer Console](https://developers.laserfiche.com/)
2. Create new application
3. Set **Application Type:** Web App
4. Set **Redirect URI:** `https://yourdomain.com/auth/callback`
5. Set **Scopes:** `table.Read table.Write project/{YOUR_PROJECT}`
6. Save `client_id` and `client_secret`

## Step 2: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

## Step 3: Clone and Configure

```bash
# Clone repository
git clone https://github.com/yourusername/lfdataview.git
cd lfdataview

# Create .env file
cp backend/.env.example backend/.env
nano backend/.env
```

**Edit backend/.env:**
```bash
DATABASE_URL=postgresql://lfdataview:CHANGE_ME_STRONG_PASSWORD@postgres/lfdataview
LASERFICHE_CLIENT_ID=your_client_id_from_step_1
LASERFICHE_CLIENT_SECRET=your_client_secret_from_step_1
LASERFICHE_REDIRECT_URI=https://yourdomain.com/auth/callback
SECRET_KEY=$(openssl rand -hex 32)
TOKEN_ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com
```

**Create docker-compose.override.yml for production:**
```yaml
version: '3.9'

services:
  backend:
    environment:
      - ENVIRONMENT=production
    restart: unless-stopped

  frontend:
    restart: unless-stopped

  postgres:
    restart: unless-stopped
```

## Step 4: Deploy with Caddy (Auto-HTTPS)

**Create Caddyfile:**
```
yourdomain.com {
    # Serve React SPA
    root * /var/www/html
    try_files {path} /index.html
    file_server

    # Proxy API requests
    reverse_proxy /api/* backend:8000
    reverse_proxy /auth/* backend:8000
}
```

**Add Caddy to docker-compose.yml:**
```yaml
  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - ./frontend/dist:/var/www/html
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  caddy_data:
  caddy_config:
```

## Step 5: Build and Deploy

```bash
# Build frontend
cd frontend
npm install
npm run build

# Start services
cd ..
docker compose up -d

# Run database migrations
docker compose exec backend alembic upgrade head

# Check logs
docker compose logs -f
```

## Step 6: Verify Deployment

1. Visit `https://yourdomain.com`
2. Click "Login with Laserfiche"
3. Authenticate
4. Verify you can view/edit tables

## Maintenance

### Backup Database
```bash
# Backup
docker compose exec postgres pg_dump -U lfdataview lfdataview > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20251118.sql | docker compose exec -T postgres psql -U lfdataview lfdataview
```

### Update Application
```bash
git pull
docker compose down
docker compose up -d --build
docker compose exec backend alembic upgrade head
```

### View Logs
```bash
docker compose logs -f backend
```

## Troubleshooting

**OAuth redirect fails:** Check `LASERFICHE_REDIRECT_URI` matches Developer Console

**Database connection error:** Check `DATABASE_URL` and postgres service status

**HTTPS not working:** Ensure port 80 and 443 are open in firewall
