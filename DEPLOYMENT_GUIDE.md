# 🚀 Quizlet AI Quiz Generator - Vercel Deployment Guide

## Overview
This guide will help you deploy both the backend (FastAPI) and frontend (React) of the Quizlet AI Quiz Generator to Vercel.

## 📋 Prerequisites
- [Vercel CLI](https://vercel.com/cli) installed
- [Git](https://git-scm.com/) installed
- Vercel account
- API keys for LLM providers (Google, Groq, Cohere)

## 🔧 Step 1: Prepare Environment Variables

### Backend Environment Variables
Create a `.env` file in the `backend/` directory with your API keys:

```env
# Database Configuration
DATABASE_URL=sqlite:///./quizlet.db

# Redis Configuration (optional for Vercel)
REDIS_URL=redis://localhost:6379

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Providers Configuration
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

# LLM Strategy Configuration
QUIZ_GENERATION_MODELS=groq,google,cohere
CHATBOT_MODELS=cohere,google,groq
ENABLE_FALLBACK=true
MAX_RETRIES=3
TIMEOUT_SECONDS=30

# App Configuration
APP_NAME=Dynamic Quiz API
DEBUG=False
```

### Frontend Environment Variables
Create a `.env` file in the `frontend/` directory:

```env
REACT_APP_API_URL=https://your-backend-url.vercel.app
```

## 🚀 Step 2: Deploy Backend to Vercel

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy the backend:**
   ```bash
   vercel --prod
   ```

4. **Set environment variables in Vercel dashboard:**
   - Go to your Vercel project dashboard
   - Navigate to Settings > Environment Variables
   - Add all the environment variables from the backend `.env` file

5. **Redeploy with environment variables:**
   ```bash
   vercel --prod
   ```

## 🌐 Step 3: Deploy Frontend to Vercel

1. **Navigate to frontend directory:**
   ```bash
   cd ../frontend
   ```

2. **Update the API URL:**
   - Replace `REACT_APP_API_URL` in the frontend `.env` file with your backend URL from Step 2

3. **Deploy the frontend:**
   ```bash
   vercel --prod
   ```

4. **Set environment variables in Vercel dashboard:**
   - Go to your frontend Vercel project dashboard
   - Navigate to Settings > Environment Variables
   - Add `REACT_APP_API_URL` with your backend URL

5. **Redeploy with environment variables:**
   ```bash
   vercel --prod
   ```

## 🔗 Step 4: Connect Frontend to Backend

1. **Update CORS settings in backend:**
   - In `backend/main.py`, update the CORS origins to include your frontend URL:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:3000",
           "http://127.0.0.1:3000",
           "https://your-frontend-url.vercel.app"  # Add this
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Redeploy backend with updated CORS:**
   ```bash
   cd backend
   vercel --prod
   ```

## 🧪 Step 5: Test the Deployment

1. **Test Backend API:**
   ```bash
   curl https://your-backend-url.vercel.app/health
   ```

2. **Test Frontend:**
   - Open your frontend URL in a browser
   - Try to register/login
   - Test quiz generation
   - Test all features

## 📊 Step 6: Monitor and Optimize

1. **Check Vercel Analytics:**
   - Monitor performance in Vercel dashboard
   - Check function execution times
   - Monitor API usage

2. **Set up monitoring:**
   - Enable Vercel Analytics
   - Set up error tracking
   - Monitor API response times

## 🔧 Troubleshooting

### Common Issues:

1. **CORS Errors:**
   - Ensure CORS origins include your frontend URL
   - Check that credentials are properly configured

2. **Environment Variables:**
   - Verify all environment variables are set in Vercel dashboard
   - Check that API keys are valid

3. **Database Issues:**
   - SQLite works for development but consider PostgreSQL for production
   - Use Vercel Postgres or external database service

4. **API Timeouts:**
   - Increase timeout settings for LLM API calls
   - Implement proper error handling

### Performance Optimization:

1. **Enable Caching:**
   - Implement Redis caching for quiz generation
   - Cache user sessions and data

2. **Optimize Bundle Size:**
   - Use code splitting in React
   - Optimize images and assets

3. **API Optimization:**
   - Implement request batching
   - Use connection pooling for database

## 🎉 Success!

Your Quizlet AI Quiz Generator is now deployed and ready to use!

### URLs:
- **Frontend:** https://your-frontend-url.vercel.app
- **Backend API:** https://your-backend-url.vercel.app
- **API Documentation:** https://your-backend-url.vercel.app/docs

### Next Steps:
1. Set up custom domain (optional)
2. Configure monitoring and analytics
3. Set up CI/CD pipeline
4. Implement advanced features

## 📞 Support

If you encounter any issues:
1. Check Vercel deployment logs
2. Verify environment variables
3. Test API endpoints individually
4. Check browser console for frontend errors

---

**Happy Learning! 🎓** 