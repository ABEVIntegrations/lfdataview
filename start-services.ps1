# PowerShell script to start Laserfiche Data View services
# Run this from PowerShell in the project directory

Write-Host "🚀 Starting Laserfiche Data View..." -ForegroundColor Green
Write-Host ""

# Navigate to project directory
Set-Location $PSScriptRoot

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🧹 Cleaning up old containers..." -ForegroundColor Yellow
docker stop lfdataview-backend lfdataview-postgres 2>$null
docker rm lfdataview-backend lfdataview-postgres 2>$null

Write-Host ""
Write-Host "📦 Starting PostgreSQL..." -ForegroundColor Cyan
docker run -d `
  --name lfdataview-postgres `
  -e POSTGRES_DB=lfdataview `
  -e POSTGRES_USER=lfdataview `
  -e POSTGRES_PASSWORD=changeme_strong_password `
  -p 5432:5432 `
  postgres:15-alpine

Write-Host "⏳ Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "🔨 Building backend..." -ForegroundColor Cyan
docker build -t lfdataview-backend ./backend

Write-Host ""
Write-Host "🚀 Starting backend..." -ForegroundColor Cyan
docker run -d `
  --name lfdataview-backend `
  --link lfdataview-postgres:postgres `
  -p 8000:8000 `
  -v "${PWD}/backend:/app" `
  -e DATABASE_URL="postgresql://lfdataview:changeme_strong_password@postgres:5432/lfdataview" `
  -e LASERFICHE_CLIENT_ID="c7189273-598e-4810-b4ca-61aabf168d94" `
  -e LASERFICHE_CLIENT_SECRET="sROiC62aKgvqn00IX7YCDtQVHMBuI2aUnQ8YV1iZYh3B8IJ7" `
  -e LASERFICHE_REDIRECT_URI="http://localhost:8000/auth/callback" `
  -e SECRET_KEY="beebe6464c4826c2148a795e985b9936772ef4b23f486dc21fc8032d5acac17d" `
  -e TOKEN_ENCRYPTION_KEY="KuimxltuTV7LiAvcunF6YgDAszV6ilc4eujHvRy1QdM=" `
  -e ENVIRONMENT="development" `
  -e DEBUG="true" `
  -e ALLOWED_ORIGINS="http://localhost:3000,http://localhost:5173" `
  -e SESSION_EXPIRY_DAYS="7" `
  lfdataview-backend `
  sh -c "sleep 5 && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Write-Host ""
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "🏥 Testing API health..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
    Write-Host "✅ API is healthy!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 Setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 Available endpoints:" -ForegroundColor Cyan
    Write-Host "   - API Health: http://localhost:8000/health"
    Write-Host "   - API Docs: http://localhost:8000/docs"
    Write-Host "   - OAuth Login: http://localhost:8000/auth/login"
    Write-Host ""
    Write-Host "📊 View logs:" -ForegroundColor Cyan
    Write-Host "   docker logs -f lfdataview-backend"
    Write-Host ""
    Write-Host "🛑 Stop services:" -ForegroundColor Cyan
    Write-Host "   docker stop lfdataview-backend lfdataview-postgres"
} catch {
    Write-Host "❌ API is not responding. Check logs:" -ForegroundColor Red
    Write-Host "   docker logs lfdataview-backend"
}
