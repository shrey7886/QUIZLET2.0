# Render Deployment Script for Quizlet AI Quiz Generator
Write-Host "🚀 Preparing Quizlet App for Render Deployment..." -ForegroundColor Green

# Check if we're in the right directory
if (!(Test-Path "main.py")) {
    Write-Host "❌ Error: main.py not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

# Check if render.yaml exists
if (!(Test-Path "render.yaml")) {
    Write-Host "❌ Error: render.yaml not found. Please create it first." -ForegroundColor Red
    exit 1
}

# Build frontend
Write-Host "📦 Building frontend..." -ForegroundColor Yellow
Set-Location frontend
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: npm install failed" -ForegroundColor Red
    exit 1
}

npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: npm run build failed" -ForegroundColor Red
    exit 1
}
Set-Location ..

# Copy frontend to static directory
Write-Host "📁 Copying frontend to static directory..." -ForegroundColor Yellow
if (!(Test-Path "static")) {
    New-Item -ItemType Directory -Path "static" -Force
}
Copy-Item -Path "frontend/build/*" -Destination "static/" -Recurse -Force

# Test the application locally
Write-Host "🧪 Testing application..." -ForegroundColor Yellow
python -c "from app.api.routes import auth, quiz, user, analytics, flashcards, chat; print('✅ All routes imported successfully')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Application test failed" -ForegroundColor Red
    exit 1
}

# Test LLM providers
Write-Host "🤖 Testing LLM providers..." -ForegroundColor Yellow
python test-working-llm.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Warning: Some LLM providers may not be working" -ForegroundColor Yellow
}

# Check git status
Write-Host "📋 Checking git status..." -ForegroundColor Yellow
if (!(Test-Path ".git")) {
    Write-Host "🔧 Initializing git repository..." -ForegroundColor Cyan
    git init
    git add .
    git commit -m "Initial commit for Render deployment"
} else {
    Write-Host "📝 Current git status:" -ForegroundColor Cyan
    git status
}

Write-Host ""
Write-Host "✅ Preparation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Next Steps for Render Deployment:" -ForegroundColor Cyan
Write-Host "1. Push your code to GitHub:" -ForegroundColor White
Write-Host "   git remote add origin <your-github-repo-url>" -ForegroundColor Gray
Write-Host "   git push -u origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Go to https://render.com" -ForegroundColor White
Write-Host "3. Create new Web Service" -ForegroundColor White
Write-Host "4. Connect your GitHub repository" -ForegroundColor White
Write-Host "5. Add your API keys in Environment Variables:" -ForegroundColor White
Write-Host "   - GOOGLE_API_KEY: $env:GOOGLE_API_KEY" -ForegroundColor Gray
Write-Host "   - GROQ_API_KEY: $env:GROQ_API_KEY" -ForegroundColor Gray
Write-Host "   - MISTRAL_API_KEY: $env:MISTRAL_API_KEY" -ForegroundColor Gray
Write-Host "6. Deploy!" -ForegroundColor White
Write-Host ""
Write-Host "📖 See RENDER_DEPLOYMENT_GUIDE.md for detailed instructions" -ForegroundColor Yellow 