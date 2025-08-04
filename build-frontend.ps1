# Build Frontend and Copy to Backend
Write-Host "🚀 Building Quizlet Frontend..." -ForegroundColor Green

# Navigate to frontend directory
Set-Location frontend

# Install dependencies if needed
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
npm install

# Build the frontend
Write-Host "🔨 Building production version..." -ForegroundColor Yellow
npm run build

# Navigate back to root
Set-Location ..

# Create static directory if it doesn't exist
if (!(Test-Path "backend/static")) {
    New-Item -ItemType Directory -Path "backend/static" -Force
}

# Copy built files to backend static directory
Write-Host "📁 Copying built files to backend..." -ForegroundColor Yellow
Copy-Item -Path "frontend/build/*" -Destination "backend/static/" -Recurse -Force

Write-Host "✅ Frontend built and copied successfully!" -ForegroundColor Green
Write-Host "🎯 Ready to deploy to Railway!" -ForegroundColor Cyan 