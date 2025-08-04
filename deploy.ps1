# 🚀 Quizlet AI Quiz Generator - Vercel Deployment Script (PowerShell)
# This script automates the deployment process to Vercel on Windows

Write-Host "🚀 Starting Quizlet AI Quiz Generator Deployment to Vercel" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Check if Vercel CLI is installed
try {
    $vercelVersion = vercel --version
    Write-Host "✅ Vercel CLI is installed: $vercelVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Vercel CLI is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "npm i -g vercel" -ForegroundColor Yellow
    exit 1
}

# Check if user is logged in to Vercel
try {
    $user = vercel whoami
    Write-Host "✅ Logged in as: $user" -ForegroundColor Green
} catch {
    Write-Host "❌ Not logged in to Vercel. Please login first:" -ForegroundColor Red
    Write-Host "vercel login" -ForegroundColor Yellow
    exit 1
}

# Step 1: Deploy Backend
Write-Host ""
Write-Host "🔧 Step 1: Deploying Backend to Vercel" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

Set-Location backend

Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "🚀 Deploying backend..." -ForegroundColor Yellow
vercel --prod

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend deployed successfully!" -ForegroundColor Green
    
    # Get the backend URL (you'll need to manually note this)
    Write-Host "📍 Please note your backend URL from the deployment output above" -ForegroundColor Yellow
    $BACKEND_URL = Read-Host "Enter your backend URL (e.g., https://your-app.vercel.app)"
} else {
    Write-Host "❌ Backend deployment failed!" -ForegroundColor Red
    exit 1
}

Set-Location ..

# Step 2: Deploy Frontend
Write-Host ""
Write-Host "🌐 Step 2: Deploying Frontend to Vercel" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

Set-Location frontend

# Update the API URL in the environment
Write-Host "🔗 Updating API URL to: $BACKEND_URL" -ForegroundColor Yellow
"REACT_APP_API_URL=$BACKEND_URL" | Out-File -FilePath ".env" -Encoding UTF8

Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

Write-Host "🏗️ Building frontend..." -ForegroundColor Yellow
npm run build

Write-Host "🚀 Deploying frontend..." -ForegroundColor Yellow
vercel --prod

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend deployed successfully!" -ForegroundColor Green
    
    # Get the frontend URL
    Write-Host "📍 Please note your frontend URL from the deployment output above" -ForegroundColor Yellow
    $FRONTEND_URL = Read-Host "Enter your frontend URL (e.g., https://your-app.vercel.app)"
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
vercel --prod

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
Write-Host "1. Set up environment variables in Vercel dashboard" -ForegroundColor White
Write-Host "2. Test the application" -ForegroundColor White
Write-Host "3. Configure custom domain (optional)" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Environment Variables to set in Vercel Dashboard:" -ForegroundColor Yellow
Write-Host "Backend:" -ForegroundColor White
Write-Host "- GOOGLE_API_KEY" -ForegroundColor White
Write-Host "- GROQ_API_KEY" -ForegroundColor White
Write-Host "- COHERE_API_KEY" -ForegroundColor White
Write-Host "- SECRET_KEY" -ForegroundColor White
Write-Host ""
Write-Host "Frontend:" -ForegroundColor White
Write-Host "- REACT_APP_API_URL=$BACKEND_URL" -ForegroundColor White
Write-Host ""
Write-Host "Happy Learning! 🎓" -ForegroundColor Green 