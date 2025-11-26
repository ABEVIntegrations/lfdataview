# Docker Development Setup

**Last Updated:** 2025-11-25
**Version:** 1.0 (Community Edition - Stateless)

## Overview

Use Docker Compose for local development with FastAPI backend and React frontend.

**Note:** The Community Edition uses stateless authentication (no database required).

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/yourusername/lfdataview.git
cd lfdataview

# 2. Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Edit .env files with your Laserfiche credentials

# 4. Start all services
docker-compose up -d

# 5. Access application
# Frontend: http://localhost:3000
# Backend API docs: http://localhost:8000/docs
```

## Docker Compose Configuration

```yaml
# docker-compose.yml

version: '3.9'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    env_file:
      - ./backend/.env
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend

networks:
  lfdataview-network:
    driver: bridge
```

## Backend Dockerfile

```dockerfile
# backend/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Frontend Dockerfile (Development)

```dockerfile
# frontend/Dockerfile.dev

FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json .
RUN npm install

# Copy application
COPY . .

# Start dev server
CMD ["npm", "run", "dev", "--", "--host"]
```

## Useful Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Run backend tests
docker-compose exec backend pytest

# Run frontend tests
docker-compose exec frontend npm run test
```

## Environment Variables

### Backend (.env)

```bash
# Laserfiche OAuth
LASERFICHE_CLIENT_ID=your_client_id
LASERFICHE_CLIENT_SECRET=your_client_secret
LASERFICHE_REDIRECT_URI=http://localhost:8000/auth/callback

# Security (generate with: openssl rand -hex 32)
SECRET_KEY=your_random_secret_key

# Token encryption (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
TOKEN_ENCRYPTION_KEY=your_fernet_key

# App Config
DEBUG=true
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Troubleshooting

### Backend won't start
- Check `.env` file has all required variables
- Check logs: `docker-compose logs backend`

### Frontend won't start
- Check `VITE_API_BASE_URL` in frontend/.env
- Clear and rebuild: `docker-compose down && docker-compose up --build`

### OAuth redirect fails
- Ensure `LASERFICHE_REDIRECT_URI` matches your Laserfiche app registration
- Check CORS: `ALLOWED_ORIGINS` should include your frontend URL
