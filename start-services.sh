#!/bin/bash

# Startup script for Laserfiche Data View
# This script starts all services and initializes the database

set -e  # Exit on error

echo "🚀 Starting Laserfiche Data View..."
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Start services
echo "📦 Starting PostgreSQL and Backend services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Services failed to start. Check logs with: docker-compose logs"
    exit 1
fi

echo "✅ Services are running"
echo ""

# Create database migration (if needed)
echo "📝 Creating database migration..."
if docker-compose exec -T backend alembic revision --autogenerate -m "Create initial auth tables" 2>&1 | grep -q "Generating"; then
    echo "✅ Migration created"
else
    echo "ℹ️  Migration may already exist or no changes detected"
fi

echo ""

# Apply migrations
echo "🔄 Applying database migrations..."
docker-compose exec -T backend alembic upgrade head

echo ""
echo "✅ Database migrations applied"
echo ""

# Test health endpoint
echo "🏥 Testing API health..."
sleep 2
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API is healthy"
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "📍 Available endpoints:"
    echo "   - API Health: http://localhost:8000/health"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - OAuth Login: http://localhost:8000/auth/login"
    echo ""
    echo "💡 Next steps:"
    echo "   1. Visit http://localhost:8000/docs to see all API endpoints"
    echo "   2. Test OAuth login at http://localhost:8000/auth/login"
    echo ""
    echo "📊 View logs:"
    echo "   docker-compose logs -f backend"
    echo ""
    echo "🛑 Stop services:"
    echo "   docker-compose down"
else
    echo "❌ API is not responding. Check logs with: docker-compose logs backend"
    exit 1
fi
