#!/bin/bash

# 🚀 Quizlet AI Quiz Generator - Vercel Deployment Script
# This script automates the deployment process to Vercel

echo "🚀 Starting Quizlet AI Quiz Generator Deployment to Vercel"
echo "=================================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed. Please install it first:"
    echo "npm i -g vercel"
    exit 1
fi

# Check if user is logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "❌ Not logged in to Vercel. Please login first:"
    echo "vercel login"
    exit 1
fi

echo "✅ Vercel CLI is installed and user is logged in"

# Step 1: Deploy Backend
echo ""
echo "🔧 Step 1: Deploying Backend to Vercel"
echo "======================================"

cd backend

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🚀 Deploying backend..."
vercel --prod

if [ $? -eq 0 ]; then
    echo "✅ Backend deployed successfully!"
    BACKEND_URL=$(vercel ls | grep -o 'https://[^[:space:]]*' | head -1)
    echo "📍 Backend URL: $BACKEND_URL"
else
    echo "❌ Backend deployment failed!"
    exit 1
fi

cd ..

# Step 2: Deploy Frontend
echo ""
echo "🌐 Step 2: Deploying Frontend to Vercel"
echo "======================================"

cd frontend

# Update the API URL in the environment
echo "🔗 Updating API URL to: $BACKEND_URL"
echo "REACT_APP_API_URL=$BACKEND_URL" > .env

echo "📦 Installing Node.js dependencies..."
npm install

echo "🏗️ Building frontend..."
npm run build

echo "🚀 Deploying frontend..."
vercel --prod

if [ $? -eq 0 ]; then
    echo "✅ Frontend deployed successfully!"
    FRONTEND_URL=$(vercel ls | grep -o 'https://[^[:space:]]*' | head -1)
    echo "📍 Frontend URL: $FRONTEND_URL"
else
    echo "❌ Frontend deployment failed!"
    exit 1
fi

cd ..

# Step 3: Update CORS and redeploy backend
echo ""
echo "🔗 Step 3: Updating CORS settings"
echo "================================="

cd backend

# Update CORS in main.py
echo "🔧 Updating CORS origins to include frontend URL..."
sed -i "s|allow_origins=\[.*\]|allow_origins=[\"http://localhost:3000\", \"http://127.0.0.1:3000\", \"$FRONTEND_URL\"]|" main.py

echo "🚀 Redeploying backend with updated CORS..."
vercel --prod

cd ..

# Final Summary
echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo "📍 Frontend URL: $FRONTEND_URL"
echo "📍 Backend URL: $BACKEND_URL"
echo "📍 API Documentation: $BACKEND_URL/docs"
echo ""
echo "📋 Next Steps:"
echo "1. Set up environment variables in Vercel dashboard"
echo "2. Test the application"
echo "3. Configure custom domain (optional)"
echo ""
echo "🔧 Environment Variables to set in Vercel Dashboard:"
echo "Backend:"
echo "- GOOGLE_API_KEY"
echo "- GROQ_API_KEY"
echo "- COHERE_API_KEY"
echo "- SECRET_KEY"
echo ""
echo "Frontend:"
echo "- REACT_APP_API_URL=$BACKEND_URL"
echo ""
echo "Happy Learning! 🎓" 