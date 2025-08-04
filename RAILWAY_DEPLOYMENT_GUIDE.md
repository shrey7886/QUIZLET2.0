# 🚂 Railway Deployment Guide for Quizlet AI Quiz Generator

## Overview
This guide will help you deploy your Quizlet AI Quiz Generator to Railway, which provides excellent support for full-stack applications with built-in databases.

## 📋 Prerequisites
- [Railway CLI](https://docs.railway.app/develop/cli) installed
- [Git](https://git-scm.com/) installed
- Railway account
- API keys for LLM providers (Google, Groq, Cohere)

## 🔧 Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

## 🚀 Step 2: Login to Railway

```bash
railway login
```

## 🏗️ Step 3: Initialize Railway Project

```bash
# In your project root
railway init
```

## 📦 Step 4: Deploy Backend Service

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Deploy backend service:**
   ```bash
   railway up
   ```

3. **Get your backend URL:**
   ```bash
   railway domain
   ```

4. **Set environment variables for backend:**
   ```bash
   railway variables set GOOGLE_API_KEY=your_google_api_key
   railway variables set GROQ_API_KEY=your_groq_api_key
   railway variables set COHERE_API_KEY=your_cohere_api_key
   railway variables set SECRET_KEY=your_secret_key_here
   railway variables set DATABASE_URL=postgresql://...
   ```

## 🌐 Step 5: Deploy Frontend Service

1. **Navigate to frontend directory:**
   ```bash
   cd ../frontend
   ```

2. **Set the backend URL as environment variable:**
   ```bash
   railway variables set REACT_APP_API_URL=https://your-backend-url.railway.app/api
   ```

3. **Deploy frontend service:**
   ```bash
   railway up
   ```

4. **Get your frontend URL:**
   ```bash
   railway domain
   ```

## 🗄️ Step 6: Set Up Database (Optional but Recommended)

1. **Add PostgreSQL database:**
   ```bash
   railway add
   # Select PostgreSQL
   ```

2. **Get database URL:**
   ```bash
   railway variables
   ```

3. **Update backend DATABASE_URL:**
   ```bash
   railway variables set DATABASE_URL=postgresql://...
   ```

## 🔗 Step 7: Update CORS Settings

1. **Update backend CORS in `backend/main.py`:**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:3000",
           "http://127.0.0.1:3000",
           "https://your-frontend-url.railway.app"  # Add this
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Redeploy backend:**
   ```bash
   cd backend
   railway up
   ```

## 🧪 Step 8: Test Your Deployment

1. **Test Backend API:**
   ```bash
   curl https://your-backend-url.railway.app/health
   ```

2. **Test Frontend:**
   - Open your frontend URL in a browser
   - Try to register/login
   - Test quiz generation
   - Test all features

## 📊 Step 9: Monitor and Optimize

1. **Check Railway Dashboard:**
   - Monitor service logs
   - Check resource usage
   - View deployment status

2. **Set up monitoring:**
   - Enable Railway Analytics
   - Set up error tracking
   - Monitor API response times

## 🔧 Environment Variables Reference

### Backend Variables:
```bash
# Database
DATABASE_URL=postgresql://...

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Providers
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-1.5-flash

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=mixtral-8x7b-32768

COHERE_API_KEY=your_cohere_api_key_here
COHERE_MODEL=command-r-plus

# Optional LLM Providers
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here

# LLM Strategy
QUIZ_GENERATION_MODELS=groq,google,cohere
CHATBOT_MODELS=cohere,google,groq
ENABLE_FALLBACK=true
MAX_RETRIES=3
TIMEOUT_SECONDS=30

# App Configuration
APP_NAME=Dynamic Quiz API
DEBUG=False
```

### Frontend Variables:
```bash
REACT_APP_API_URL=https://your-backend-url.railway.app/api
```

## 🚀 Quick Deploy Script

Create a `deploy-railway.sh` script:

```bash
#!/bin/bash

echo "🚂 Deploying Quizlet AI Quiz Generator to Railway"

# Deploy backend
echo "📦 Deploying backend..."
cd backend
railway up

# Get backend URL
BACKEND_URL=$(railway domain)
echo "📍 Backend URL: $BACKEND_URL"

# Deploy frontend
echo "🌐 Deploying frontend..."
cd ../frontend
railway variables set REACT_APP_API_URL="$BACKEND_URL/api"
railway up

# Get frontend URL
FRONTEND_URL=$(railway domain)
echo "📍 Frontend URL: $FRONTEND_URL"

echo "🎉 Deployment complete!"
echo "Backend: $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo "API Docs: $BACKEND_URL/docs"
```

## 🔧 Troubleshooting

### Common Issues:

1. **Build Failures:**
   - Check Railway logs: `railway logs`
   - Verify all dependencies are in requirements.txt/package.json

2. **Environment Variables:**
   - Verify all variables are set: `railway variables`
   - Check for typos in variable names

3. **CORS Errors:**
   - Ensure frontend URL is in backend CORS origins
   - Check that credentials are properly configured

4. **Database Issues:**
   - Verify DATABASE_URL is correct
   - Check database connection in Railway dashboard

### Performance Optimization:

1. **Enable Caching:**
   - Use Railway's built-in Redis
   - Implement proper caching strategies

2. **Optimize Build:**
   - Use .railwayignore to exclude unnecessary files
   - Optimize Docker images if using custom builds

## 🎉 Success!

Your Quizlet AI Quiz Generator is now deployed on Railway!

### URLs:
- **Frontend:** https://your-frontend-url.railway.app
- **Backend API:** https://your-backend-url.railway.app
- **API Documentation:** https://your-backend-url.railway.app/docs

### Next Steps:
1. Set up custom domain (optional)
2. Configure monitoring and analytics
3. Set up CI/CD pipeline
4. Implement advanced features

## 📞 Support

If you encounter any issues:
1. Check Railway deployment logs
2. Verify environment variables
3. Test API endpoints individually
4. Check browser console for frontend errors
5. Visit [Railway Documentation](https://docs.railway.app/)

---

**Happy Learning! 🎓** 