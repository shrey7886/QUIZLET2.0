# Integrated Quizlet App Deployment Script
Write-Host "🚀 Preparing Quizlet App for Integrated Deployment..." -ForegroundColor Green

# Check if we're in the right directory
if (!(Test-Path "main.py")) {
    Write-Host "❌ Error: main.py not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

# Install backend dependencies
Write-Host "📦 Installing backend dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install frontend dependencies and build
Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
Write-Host "🔨 Building frontend..." -ForegroundColor Yellow
npm run build
Set-Location ..

# Create static directory and copy frontend build
Write-Host "📁 Copying frontend to static directory..." -ForegroundColor Yellow
if (!(Test-Path "static")) {
    New-Item -ItemType Directory -Path "static" -Force
}
Copy-Item -Path "frontend/build/*" -Destination "static/" -Recurse -Force

# Create environment file for local testing
Write-Host "⚙️ Creating environment configuration..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item "backend/env.example" ".env" -Force
    Write-Host "📝 Created .env file from template. Please configure your API keys." -ForegroundColor Cyan
}

# Test the application locally
Write-Host "🧪 Testing application locally..." -ForegroundColor Yellow
Write-Host "Starting backend server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan

# Start the backend server
try {
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
} catch {
    Write-Host "❌ Error starting server: $_" -ForegroundColor Red
    Write-Host "💡 Make sure you have uvicorn installed: pip install uvicorn[standard]" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Local setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Next Steps for Production Deployment:" -ForegroundColor Cyan
Write-Host "1. Configure your API keys in .env file" -ForegroundColor White
Write-Host "2. Push your code to GitHub" -ForegroundColor White
Write-Host "3. Deploy to Render using render.yaml" -ForegroundColor White
Write-Host "4. Set environment variables in Render dashboard" -ForegroundColor White
Write-Host ""
Write-Host "📖 See DEPLOYMENT_GUIDE.md for detailed instructions" -ForegroundColor Yellow 