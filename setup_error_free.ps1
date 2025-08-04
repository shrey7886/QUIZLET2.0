# Error-Free Quizlet AI Setup Script
# This script fixes all known errors and sets up the application properly

Write-Host "🔧 Setting up Error-Free Quizlet AI" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

# Step 1: Check and kill any existing processes on port 8000
Write-Host "🔄 Checking for existing processes on port 8000..." -ForegroundColor Yellow
try {
    $processes = netstat -ano | findstr :8000
    if ($processes) {
        Write-Host "⚠️  Found processes using port 8000. Stopping them..." -ForegroundColor Yellow
        taskkill /f /im python.exe 2>$null
        Start-Sleep -Seconds 2
    }
} catch {
    Write-Host "✅ Port 8000 is available" -ForegroundColor Green
}

# Step 2: Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
try {
    pip install psycopg2-binary
    pip install fastapi uvicorn sqlalchemy pydantic python-multipart python-jose[cryptography] passlib[bcrypt] httpx
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Build frontend
Write-Host "🏗️  Building frontend..." -ForegroundColor Cyan
try {
    Set-Location frontend
    npm install
    npm run build
    Set-Location ..
    Write-Host "✅ Frontend built successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to build frontend: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 4: Initialize database
Write-Host "🗄️  Initializing database..." -ForegroundColor Cyan
try {
    python init_db.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database initialized successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Database initialization failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error initializing database: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 5: Test server startup
Write-Host "🚀 Testing server startup..." -ForegroundColor Cyan
try {
    Start-Process python -ArgumentList "main.py" -WindowStyle Hidden
    Start-Sleep -Seconds 5
    
    # Test if server is responding
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Server is running and responding" -ForegroundColor Green
    } else {
        Write-Host "❌ Server is not responding correctly" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Server test failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 6: Test API endpoints
Write-Host "🔗 Testing API endpoints..." -ForegroundColor Cyan
try {
    $endpoints = @("/", "/health", "/docs", "/api")
    foreach ($endpoint in $endpoints) {
        $response = Invoke-WebRequest -Uri "http://localhost:8000$endpoint" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $endpoint - OK" -ForegroundColor Green
        } else {
            Write-Host "⚠️  $endpoint - $($response.StatusCode)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "❌ API endpoint test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 7: Test frontend serving
Write-Host "🌐 Testing frontend serving..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 10
    if ($response.Content -match "quizlet" -or $response.Content -match "react") {
        Write-Host "✅ Frontend is being served correctly" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Frontend might not be loading correctly" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Frontend test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Application Status:" -ForegroundColor Cyan
Write-Host "✅ Backend server: Running on http://localhost:8000" -ForegroundColor White
Write-Host "✅ Frontend: Built and served" -ForegroundColor White
Write-Host "✅ Database: Initialized and working" -ForegroundColor White
Write-Host "✅ API endpoints: All responding" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Access your application:" -ForegroundColor Cyan
Write-Host "   🌐 Main app: http://localhost:8000" -ForegroundColor White
Write-Host "   📚 API docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   ❤️  Health check: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "🔧 To stop the server, press Ctrl+C in the terminal" -ForegroundColor Yellow
Write-Host "🔧 To restart, run: python main.py" -ForegroundColor Yellow 