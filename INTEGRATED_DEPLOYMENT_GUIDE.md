# Quizlet AI Quiz Generator - Integrated Deployment Guide

## 🚀 Overview

This guide will help you deploy the integrated Quizlet AI Quiz Generator application, which combines a React frontend with a FastAPI backend into a single, production-ready application.

## 📋 Prerequisites

- GitHub account
- Render account (free tier available)
- API keys for LLM providers (Google AI, Groq, Cohere)

## 🛠️ Local Development Setup

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd Quizlet

# Run the integrated deployment script
./deploy-integrated.ps1
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./quizlet.db

# LLM Provider API Keys
GOOGLE_API_KEY=your-google-api-key
GROQ_API_KEY=your-groq-api-key
COHERE_API_KEY=your-cohere-api-key

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
DEBUG=false
ENVIRONMENT=development
ALLOWED_ORIGINS=*
```

### 3. Test Locally

```bash
# Start the integrated server
python main.py
```

Visit `http://localhost:8000` to see your application running!

## 🌐 Production Deployment on Render

### 1. Prepare Your Repository

Ensure your repository contains:
- `main.py` (integrated FastAPI app)
- `requirements.txt` (Python dependencies)
- `frontend/` directory (React app)
- `render.yaml` (deployment configuration)
- `app/` directory (backend modules)

### 2. Push to GitHub

```bash
git add .
git commit -m "Integrated frontend and backend for deployment"
git push origin main
```

### 3. Deploy on Render

1. **Go to [Render Dashboard](https://dashboard.render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service:**
   - **Name**: `quizlet-app`
   - **Environment**: `Python`
   - **Build Command**: (auto-detected from render.yaml)
   - **Start Command**: (auto-detected from render.yaml)

### 4. Set Environment Variables

In the Render dashboard, go to your service → Environment → Environment Variables and add:

#### Required Variables:
- `SECRET_KEY` (auto-generated)
- `GOOGLE_API_KEY` (your Google AI API key)
- `GROQ_API_KEY` (your Groq API key)
- `COHERE_API_KEY` (your Cohere API key)

#### Optional Variables:
- `DATABASE_URL` (default: SQLite)
- `REDIS_URL` (for caching, optional)
- `DEBUG` (set to false for production)

### 5. Deploy

Click "Create Web Service" and wait for the build to complete.

## 🔧 Application Features

### Core Features:
1. **AI-Powered Quiz Generation**
   - Multiple LLM providers (Google AI, Groq, Cohere)
   - Customizable difficulty levels
   - Topic-based question generation

2. **Comprehensive Analytics**
   - Performance tracking
   - Progress visualization
   - Weak area identification
   - Learning recommendations

3. **Flashcard Learning System**
   - Spaced repetition algorithm
   - Custom flashcard creation
   - Study session tracking
   - Progress monitoring

4. **Real-time Community Chat**
   - Study group creation
   - Topic-based discussions
   - Collaborative learning
   - Real-time messaging

5. **User Management**
   - Secure authentication
   - Profile management
   - Progress tracking
   - Achievement system

### API Endpoints:

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

#### Quiz Management
- `POST /api/quiz/generate` - Generate new quiz
- `POST /api/quiz/{id}/submit-answer` - Submit answer
- `POST /api/quiz/{id}/complete` - Complete quiz
- `GET /api/quiz/history` - Get quiz history

#### Analytics
- `GET /api/analytics/dashboard` - Analytics dashboard
- `GET /api/analytics/progress` - Progress tracking
- `GET /api/analytics/history` - Performance history
- `GET /api/analytics/topics` - Topic analytics

#### Flashcards
- `POST /api/flashcards` - Create flashcard
- `GET /api/flashcards` - Get flashcards
- `POST /api/flashcards/{id}/review` - Review flashcard
- `GET /api/flashcards/due` - Get due cards

#### Chat
- `POST /api/chat/rooms` - Create chat room
- `GET /api/chat/rooms` - Get user rooms
- `POST /api/chat/messages` - Send message
- `GET /api/chat/rooms/{id}/messages` - Get room messages

## 🎯 Testing Your Deployment

### 1. Health Check
Visit `https://your-app-name.onrender.com/health`

### 2. API Documentation
Visit `https://your-app-name.onrender.com/docs`

### 3. Frontend Application
Visit `https://your-app-name.onrender.com/`

### 4. Test Features
1. **Register/Login**: Create an account
2. **Generate Quiz**: Test AI-powered quiz generation
3. **Take Quiz**: Complete a quiz and see results
4. **View Analytics**: Check your performance dashboard
5. **Create Flashcards**: Test the flashcard system
6. **Join Chat**: Test the community features

## 🔍 Troubleshooting

### Common Issues:

1. **Build Fails**
   - Check Node.js version compatibility
   - Ensure all dependencies are in package.json
   - Verify Python requirements.txt

2. **API Errors**
   - Verify API keys are set correctly
   - Check CORS configuration
   - Review server logs in Render dashboard

3. **Frontend Not Loading**
   - Ensure frontend build completed successfully
   - Check static file serving configuration
   - Verify React Router configuration

4. **Database Issues**
   - Check DATABASE_URL configuration
   - Ensure database tables are created
   - Review database connection settings

### Debug Commands:

```bash
# Check local build
cd frontend && npm run build

# Test API locally
curl http://localhost:8000/health

# Check database
python -c "from app.core.database import engine; print('Database connected')"
```

## 📊 Monitoring and Maintenance

### Render Dashboard Features:
- **Logs**: Real-time application logs
- **Metrics**: Performance monitoring
- **Environment Variables**: Secure configuration management
- **Auto-deploy**: Automatic deployments on git push

### Recommended Monitoring:
1. **Health Checks**: Monitor `/health` endpoint
2. **Error Logs**: Review application errors
3. **Performance**: Monitor response times
4. **API Usage**: Track LLM provider usage

## 🚀 Scaling Considerations

### Free Tier Limitations:
- 750 hours/month
- 512MB RAM
- Shared CPU
- No persistent storage

### Upgrade Options:
- **Starter Plan**: $7/month for dedicated resources
- **Standard Plan**: $25/month for better performance
- **Pro Plan**: $85/month for production workloads

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Render documentation
3. Check application logs
4. Verify environment configuration

## 🎉 Success!

Your integrated Quizlet AI Quiz Generator is now deployed and ready to use! Users can access all features through the web interface, and the application will automatically scale based on usage.

---

**Happy Learning! 🎓** 