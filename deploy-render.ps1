# Render Deployment Preparation Script
Write-Host "🚀 Preparing Quizlet App for Render Deployment..." -ForegroundColor Green

# Check if we're in the right directory
if (!(Test-Path "main.py")) {
    Write-Host "❌ Error: main.py not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

# Build frontend
Write-Host "📦 Building frontend..." -ForegroundColor Yellow
Set-Location frontend
npm install
npm run build
Set-Location ..

# Copy frontend to static directory
Write-Host "📁 Copying frontend to static directory..." -ForegroundColor Yellow
if (!(Test-Path "static")) {
    New-Item -ItemType Directory -Path "static" -Force
}
Copy-Item -Path "frontend/build/*" -Destination "static/" -Recurse -Force

# Check if render.yaml exists
if (!(Test-Path "render.yaml")) {
    Write-Host "❌ Error: render.yaml not found. Please create it first." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Preparation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Push your code to GitHub" -ForegroundColor White
Write-Host "2. Go to https://render.com" -ForegroundColor White
Write-Host "3. Create new Web Service" -ForegroundColor White
Write-Host "4. Connect your GitHub repository" -ForegroundColor White
Write-Host "5. Add your API keys in Environment Variables" -ForegroundColor White
Write-Host "6. Deploy!" -ForegroundColor White
Write-Host ""
Write-Host "📖 See RENDER_DEPLOYMENT_GUIDE.md for detailed instructions" -ForegroundColor Yellow 