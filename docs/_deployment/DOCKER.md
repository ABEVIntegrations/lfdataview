# Docker Development Setup

**Last Updated:** 2025-11-18

## Overview

Use Docker Compose for local development with PostgreSQL, FastAPI, and React.

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

# 5. Run database migrations
docker-compose exec backend alembic upgrade head

# 6. Access application
# Frontend: http://localhost:3000
# Backend API docs: http://localhost:8000/docs
# PostgreSQL: localhost:5432
```

## Docker Compose Configuration

```yaml
# docker-compose.yml

version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: lfdataview
      POSTGRES_USER: lfdataview
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U lfdataview"]
      interval: 10s
      timeout: 5s
      retries: 5

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
      TOKEN_ENCRYPTION_KEY: ${TOKEN_ENCRYPTION_KEY}
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    environment:
      VITE_API_BASE_URL: http://localhost:8000
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

volumes:
  postgres_data:
```

## Backend Dockerfile

```dockerfile
# backend/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations and start server
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
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

# Stop and remove volumes (fresh start)
docker-compose down -v

# Run migrations
docker-compose exec backend alembic upgrade head

# Access PostgreSQL
docker-compose exec postgres psql -U lfdataview -d lfdataview

# Run backend tests
docker-compose exec backend pytest

# Run frontend tests
docker-compose exec frontend npm run test
```

## Troubleshooting

### Backend won't start
- Check `.env` file has all required variables
- Check database connection: `docker-compose logs postgres`
- Check migrations: `docker-compose exec backend alembic current`

### Frontend won't start
- Check `VITE_API_BASE_URL` in frontend/.env
- Clear node_modules: `docker-compose down && docker-compose up --build`

### Database connection refused
- Ensure postgres service is healthy: `docker-compose ps`
- Check DATABASE_URL format

