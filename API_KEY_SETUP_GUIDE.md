# 🔑 API Key Setup Guide for Quizlet AI Quiz Generator

## 🎯 **Quick Start: Get Free API Keys**

### **Step 1: Google AI (Gemini) - FREE**
1. **Visit**: https://makersuite.google.com/app/apikey
2. **Sign in** with your Google account
3. **Click** "Create API Key"
4. **Copy** the API key
5. **Free tier**: 15 requests/minute, 1500 requests/day

### **Step 2: Groq - FREE**
1. **Visit**: https://console.groq.com/keys
2. **Sign up** for a free account
3. **Click** "Create API Key"
4. **Copy** the API key
5. **Free tier**: 100 requests/minute, unlimited requests

### **Step 3: Cohere - FREE**
1. **Visit**: https://dashboard.cohere.com/api-keys
2. **Sign up** for a free account
3. **Click** "Create API Key"
4. **Copy** the API key
5. **Free tier**: 100 requests/minute, 1000 requests/day

## 📝 **Update Your .env File**

After getting your API keys, update your `.env` file:

```env
# Security
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./quizlet.db

# LLM Provider API Keys
GOOGLE_API_KEY=your-google-api-key-here
GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
COHERE_API_KEY=your-cohere-api-key-here

# Optional (paid providers)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
MISTRAL_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434

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
```

## 🧪 **Test Your API Keys**

After setting up your API keys, test them:

```bash
python test-api-keys.py
```

## 🚀 **Restart Your Application**

After updating the API keys:

```bash
# Stop the current server (Ctrl+C)
# Then restart
python main.py
```

## 📊 **Provider Comparison**

| Provider | Free Tier | Speed | Quality | Setup Difficulty |
|----------|-----------|-------|---------|------------------|
| **Google AI** | ✅ 15 req/min | Fast | High | Easy |
| **Groq** | ✅ 100 req/min | Very Fast | High | Easy |
| **Cohere** | ✅ 100 req/min | Fast | High | Easy |
| OpenAI | ❌ Paid | Fast | Very High | Easy |
| Anthropic | ❌ Paid | Fast | Very High | Easy |
| Mistral | ❌ Paid | Fast | High | Easy |
| Ollama | ✅ Local | Slow | Medium | Hard |

## 🎯 **Recommended Setup**

**For beginners**: Start with **Google AI** and **Groq**
- Both are free
- Both are fast
- Both have high-quality models
- Easy to set up

**For advanced users**: Add **Cohere** for additional variety

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **"API key not found"**
   - Make sure you copied the entire API key
   - Check for extra spaces in the .env file

2. **"Rate limit exceeded"**
   - Free tiers have limits
   - Wait a minute and try again
   - Consider upgrading to paid plans

3. **"Model not available"**
   - Check the model name in your .env file
   - Some models may be region-restricted

### **Testing Individual Providers:**

```python
# Test Google AI
curl -X POST "http://localhost:8000/api/quiz/generate" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python basics", "difficulty": "easy", "num_questions": 3}'
```

## 🎉 **Success!**

Once you have API keys configured, you'll be able to:
- ✅ Generate AI-powered quizzes
- ✅ Get chatbot responses
- ✅ Create learning recommendations
- ✅ Analyze performance with AI insights

## 📞 **Need Help?**

- Check the application logs for error messages
- Verify your API keys are correct
- Test with the `test-api-keys.py` script
- Review the provider documentation

---

**Happy Learning! 🎓** 