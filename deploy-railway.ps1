# 🚂 Railway Deployment Script for Quizlet AI Quiz Generator (PowerShell)
# This script automates the deployment process to Railway

Write-Host "🚂 Starting Quizlet AI Quiz Generator Deployment to Railway" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Check if Railway CLI is installed
try {
    $railwayVersion = railway --version
    Write-Host "✅ Railway CLI is installed: $railwayVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Railway CLI is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "npm install -g @railway/cli" -ForegroundColor Yellow
    exit 1
}

# Check if user is logged in to Railway
try {
    $user = railway whoami
    Write-Host "✅ Logged in as: $user" -ForegroundColor Green
} catch {
    Write-Host "❌ Not logged in to Railway. Please login first:" -ForegroundColor Red
    Write-Host "railway login" -ForegroundColor Yellow
    exit 1
}

# Step 1: Deploy Backend
Write-Host ""
Write-Host "📦 Step 1: Deploying Backend to Railway" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

Set-Location backend

Write-Host "🚀 Deploying backend service..." -ForegroundColor Yellow
railway up

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend deployed successfully!" -ForegroundColor Green
    
    # Get the backend URL
    Write-Host "📍 Getting backend URL..." -ForegroundColor Yellow
    $BACKEND_URL = railway domain
    Write-Host "📍 Backend URL: $BACKEND_URL" -ForegroundColor Green
    
    # Set environment variables for backend
    Write-Host "🔧 Setting backend environment variables..." -ForegroundColor Yellow
    Write-Host "Please set the following environment variables in Railway dashboard:" -ForegroundColor Yellow
    Write-Host "GOOGLE_API_KEY=your_google_api_key_here" -ForegroundColor White
    Write-Host "GROQ_API_KEY=your_groq_api_key_here" -ForegroundColor White
    Write-Host "COHERE_API_KEY=your_cohere_api_key_here" -ForegroundColor White
    Write-Host "SECRET_KEY=your_secret_key_here" -ForegroundColor White
    Write-Host "DATABASE_URL=postgresql://..." -ForegroundColor White
} else {
    Write-Host "❌ Backend deployment failed!" -ForegroundColor Red
    exit 1
}

Set-Location ..

# Step 2: Deploy Frontend
Write-Host ""
Write-Host "🌐 Step 2: Deploying Frontend to Railway" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

Set-Location frontend

# Set the backend URL as environment variable
Write-Host "🔗 Setting frontend API URL to: $BACKEND_URL/api" -ForegroundColor Yellow
railway variables set REACT_APP_API_URL="$BACKEND_URL/api"

Write-Host "🚀 Deploying frontend service..." -ForegroundColor Yellow
railway up

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend deployed successfully!" -ForegroundColor Green
    
    # Get the frontend URL
    Write-Host "📍 Getting frontend URL..." -ForegroundColor Yellow
    $FRONTEND_URL = railway domain
    Write-Host "📍 Frontend URL: $FRONTEND_URL" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend deployment failed!" -ForegroundColor Red
    exit 1
}

Set-Location ..

# Step 3: Update CORS and redeploy backend
Write-Host ""
Write-Host "🔗 Step 3: Updating CORS settings" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

Set-Location backend

# Update CORS in main.py
Write-Host "🔧 Updating CORS origins to include frontend URL..." -ForegroundColor Yellow
$mainContent = Get-Content "main.py" -Raw
$newCorsOrigins = "allow_origins=[`"http://localhost:3000`", `"http://127.0.0.1:3000`", `"$FRONTEND_URL`"]"
$mainContent = $mainContent -replace 'allow_origins=\[.*?\]', $newCorsOrigins
$mainContent | Set-Content "main.py"

Write-Host "🚀 Redeploying backend with updated CORS..." -ForegroundColor Yellow
railway up

Set-Location ..

# Final Summary
Write-Host ""
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green
Write-Host "📍 Frontend URL: $FRONTEND_URL" -ForegroundColor Cyan
Write-Host "📍 Backend URL: $BACKEND_URL" -ForegroundColor Cyan
Write-Host "📍 API Documentation: $BACKEND_URL/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Set up environment variables in Railway dashboard" -ForegroundColor White
Write-Host "2. Test the application" -ForegroundColor White
Write-Host "3. Configure custom domain (optional)" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Environment Variables to set in Railway Dashboard:" -ForegroundColor Yellow
Write-Host "Backend:" -ForegroundColor White
Write-Host "- GOOGLE_API_KEY" -ForegroundColor White
Write-Host "- GROQ_API_KEY" -ForegroundColor White
Write-Host "- COHERE_API_KEY" -ForegroundColor White
Write-Host "- SECRET_KEY" -ForegroundColor White
Write-Host "- DATABASE_URL" -ForegroundColor White
Write-Host ""
Write-Host "Frontend:" -ForegroundColor White
Write-Host "- REACT_APP_API_URL=$BACKEND_URL/api" -ForegroundColor White
Write-Host ""
Write-Host "Happy Learning! 🎓" -ForegroundColor Green 