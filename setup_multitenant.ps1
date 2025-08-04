# Multitenant Neon Database Setup Script
# This script sets up the multitenant Quizlet AI application

Write-Host "🚀 Setting up Multitenant Quizlet AI with Neon Database" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "Please create a .env file with your Neon database URL:" -ForegroundColor Yellow
    Write-Host "NEON_DATABASE_URL=postgresql://username:password@host/database?sslmode=require" -ForegroundColor White
    exit 1
}

# Check if NEON_DATABASE_URL is set
$envContent = Get-Content ".env" -Raw
if ($envContent -notmatch "NEON_DATABASE_URL") {
    Write-Host "❌ NEON_DATABASE_URL not found in .env file!" -ForegroundColor Red
    Write-Host "Please add your Neon database URL to the .env file." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Environment configuration found" -ForegroundColor Green

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
try {
    pip install psycopg2-binary
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test Neon connection
Write-Host "🔗 Testing Neon database connection..." -ForegroundColor Cyan
try {
    python test_neon_connection.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Neon connection successful" -ForegroundColor Green
    } else {
        Write-Host "❌ Neon connection failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error testing Neon connection: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Initialize multitenant database
Write-Host "🏗️ Initializing multitenant database..." -ForegroundColor Cyan
try {
    python init_multitenant_db.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Multitenant database initialized" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to initialize multitenant database" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error initializing database: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Start the server
Write-Host "🚀 Starting the multitenant server..." -ForegroundColor Cyan
Write-Host "The server will start on http://localhost:8000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

try {
    python main.py
} catch {
    Write-Host "❌ Error starting server: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 Multitenant setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Visit http://localhost:8000 to see the API" -ForegroundColor White
Write-Host "2. Visit http://localhost:8000/docs for API documentation" -ForegroundColor White
Write-Host "3. Run 'python test_multitenant.py' to test the setup" -ForegroundColor White
Write-Host "4. Use the tenant IDs from the initialization to make API requests" -ForegroundColor White
Write-Host ""
Write-Host "🔧 API Usage:" -ForegroundColor Cyan
Write-Host "All API requests must include the X-Tenant-ID header:" -ForegroundColor White
Write-Host "curl -H 'X-Tenant-ID: your-tenant-id' http://localhost:8000/api/users" -ForegroundColor Gray 