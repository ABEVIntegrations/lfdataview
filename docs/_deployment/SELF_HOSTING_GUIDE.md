# Self-Hosting Guide

**Last Updated:** 2025-11-25
**Version:** 1.0 (Community Edition - Stateless)

## Overview

Guide for deploying LF DataView on your own server. The Community Edition uses stateless authentication with no database required.

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
# Laserfiche OAuth
LASERFICHE_CLIENT_ID=your_client_id_from_step_1
LASERFICHE_CLIENT_SECRET=your_client_secret_from_step_1
LASERFICHE_REDIRECT_URI=https://yourdomain.com/auth/callback

# Security - generate these keys!
SECRET_KEY=run_this_command: openssl rand -hex 32
TOKEN_ENCRYPTION_KEY=run_this_command: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Production settings
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=https://yourdomain.com
```

## Step 4: Deploy with Caddy (Auto-HTTPS)

**Create Caddyfile:**
```caddyfile
yourdomain.com {
    # Proxy API requests to backend
    reverse_proxy /auth/* backend:8000
    reverse_proxy /tables/* backend:8000
    reverse_proxy /health backend:8000

    # Serve React SPA
    root * /var/www/html
    try_files {path} /index.html
    file_server
}
```

**Create docker-compose.prod.yml:**
```yaml
version: '3.9'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    env_file:
      - ./backend/.env
    restart: unless-stopped
    networks:
      - lfdataview-network

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
    restart: unless-stopped
    networks:
      - lfdataview-network

networks:
  lfdataview-network:
    driver: bridge

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
docker compose -f docker-compose.prod.yml up -d

# Check logs
docker compose -f docker-compose.prod.yml logs -f
```

## Step 6: Verify Deployment

1. Visit `https://yourdomain.com`
2. Click "Login with Laserfiche"
3. Authenticate
4. Verify you can view/edit tables

## Maintenance

### Update Application
```bash
git pull
docker compose -f docker-compose.prod.yml down
cd frontend && npm run build && cd ..
docker compose -f docker-compose.prod.yml up -d --build
```

### View Logs
```bash
docker compose -f docker-compose.prod.yml logs -f backend
```

### Restart Services
```bash
docker compose -f docker-compose.prod.yml restart
```

## Troubleshooting

**OAuth redirect fails:**
- Check `LASERFICHE_REDIRECT_URI` matches Developer Console exactly
- Ensure HTTPS is working (Caddy handles this automatically)

**HTTPS not working:**
- Ensure ports 80 and 443 are open in firewall
- Check Caddy logs: `docker compose logs caddy`
- Ensure domain DNS points to your server

**Session expires quickly:**
- This is expected behavior - Laserfiche tokens expire after ~1 hour
- Users simply log in again when needed

## Security Notes

- Tokens are encrypted with Fernet before storing in cookies
- OAuth state is signed with HMAC-SHA256 to prevent CSRF
- All cookies are httpOnly (not accessible via JavaScript)
- In production, cookies are marked Secure (HTTPS only)
