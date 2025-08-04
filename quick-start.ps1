# Quick Start Script for Quizlet AI Quiz Generator
Write-Host "🚀 Quick Start - Quizlet AI Quiz Generator" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Check if we're in the right directory
if (!(Test-Path "main.py")) {
    Write-Host "❌ Error: main.py not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python from https://python.org/" -ForegroundColor Red
    exit 1
}

# Install backend dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install frontend dependencies
Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..

# Build frontend
Write-Host "🔨 Building frontend..." -ForegroundColor Yellow
Set-Location frontend
npm run build
Set-Location ..

# Create static directory and copy frontend build
Write-Host "📁 Setting up static files..." -ForegroundColor Yellow
if (!(Test-Path "static")) {
    New-Item -ItemType Directory -Path "static" -Force
}
Copy-Item -Path "frontend/build/*" -Destination "static/" -Recurse -Force

# Create environment file if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "⚙️ Creating .env file..." -ForegroundColor Yellow
    
    $envContent = @"
# Security
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./quizlet.db

# LLM Provider API Keys (optional for testing)
GOOGLE_API_KEY=
GROQ_API_KEY=
COHERE_API_KEY=

# LLM Models
GOOGLE_MODEL=gemini-1.5-flash
GROQ_MODEL=mixtral-8x7b-32768
COHERE_MODEL=command-r-plus

# Feature Configuration
QUIZ_GENERATION_MODELS=groq,google,cohere
CHATBOT_MODELS=cohere,google,groq
ENABLE_FALLBACK=true
MAX_RETRIES=3
TIMEOUT_SECONDS=30

# App Configuration
APP_NAME=Quizlet AI Quiz Generator
DEBUG=true
ENVIRONMENT=development
ALLOWED_ORIGINS=*
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "📝 Created .env file. You can add your API keys later." -ForegroundColor Cyan
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Starting the application..." -ForegroundColor Cyan
Write-Host "🌐 The app will be available at: http://localhost:8000" -ForegroundColor White
Write-Host "📚 API documentation at: http://localhost:8000/docs" -ForegroundColor White
Write-Host "💚 Health check at: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the application
try {
    python main.py
} catch {
    Write-Host "❌ Error starting the application: $_" -ForegroundColor Red
    Write-Host "💡 Make sure you have uvicorn installed: pip install uvicorn[standard]" -ForegroundColor Yellow
} 