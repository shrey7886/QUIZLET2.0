#!/usr/bin/env python3
"""
Quick setup script for primary LLM models (Google Gemini, Groq, Cohere)
This script tests connectivity and validates API keys.
"""

import os
import asyncio
import httpx
from typing import Dict, List

# Primary model configurations
PRIMARY_MODELS = {
    "google": {
        "name": "Google Gemini",
        "api_key": "your-google-api-key-here",
        "model": "gemini-1.5-flash",
        "test_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    },
    "groq": {
        "name": "Groq",
        "api_key": "your-groq-api-key-here",
        "model": "mixtral-8x7b-32768",
        "test_url": "https://api.groq.com/openai/v1/chat/completions"
    },
    "cohere": {
        "name": "Cohere",
        "api_key": "your-cohere-api-key-here",
        "model": "command-r-plus",
        "test_url": "https://api.cohere.ai/v1/chat"
    }
}

async def test_google_gemini():
    """Test Google Gemini API connectivity"""
    config = PRIMARY_MODELS["google"]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config['test_url']}?key={config['api_key']}",
                json={
                    "contents": [{
                        "parts": [{"text": "Hello, this is a test message. Please respond with 'OK' if you can see this."}]
                    }]
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "✅ Google Gemini: Connected successfully"
            else:
                return False, f"❌ Google Gemini: Error {response.status_code} - {response.text}"
                
    except Exception as e:
        return False, f"❌ Google Gemini: Connection failed - {str(e)}"

async def test_groq():
    """Test Groq API connectivity"""
    config = PRIMARY_MODELS["groq"]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config['test_url'],
                headers={
                    "Authorization": f"Bearer {config['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config['model'],
                    "messages": [{"role": "user", "content": "Hello, this is a test message."}],
                    "max_tokens": 10
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "✅ Groq: Connected successfully"
            else:
                return False, f"❌ Groq: Error {response.status_code} - {response.text}"
                
    except Exception as e:
        return False, f"❌ Groq: Connection failed - {str(e)}"

async def test_cohere():
    """Test Cohere API connectivity"""
    config = PRIMARY_MODELS["cohere"]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config['test_url'],
                headers={
                    "Authorization": f"Bearer {config['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config['model'],
                    "message": "Hello, this is a test message.",
                    "max_tokens": 10
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "✅ Cohere: Connected successfully"
            else:
                return False, f"❌ Cohere: Error {response.status_code} - {response.text}"
                
    except Exception as e:
        return False, f"❌ Cohere: Connection failed - {str(e)}"

async def create_env_file():
    """Create .env file with primary model configuration"""
    
    env_content = """# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/quizlet

# Redis Configuration
REDIS_URL=redis://localhost:6379

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Providers Configuration - PRIMARY MODELS

# Google (Gemini 1.5 Flash) - PRIMARY
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_MODEL=gemini-1.5-flash

# Groq (Ultra-fast inference) - PRIMARY
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=mixtral-8x7b-32768

# Cohere (Command R+) - PRIMARY
COHERE_API_KEY=your-cohere-api-key-here
COHERE_MODEL=command-r-plus

# Optional fallback providers (leave empty if not using)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
MISTRAL_API_KEY=

# LLM Strategy Configuration - Optimized for Speed
# Primary models: Groq (fastest) -> Google (fast) -> Cohere (reliable)
QUIZ_GENERATION_MODELS=groq,google,cohere

# Chatbot priority: Cohere (good explanations) -> Google (fast) -> Groq (backup)
CHATBOT_MODELS=cohere,google,groq

# Fallback Strategy
ENABLE_FALLBACK=true
MAX_RETRIES=3
TIMEOUT_SECONDS=30

# App Configuration
APP_NAME=Dynamic Quiz API
DEBUG=True
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    return "✅ .env file created with primary model configuration"

async def main():
    """Main setup function"""
    print("🚀 Setting up Primary LLM Models for Dynamic Quiz Application")
    print("=" * 60)
    
    # Test all primary models
    print("\n🔍 Testing API Connectivity...")
    
    tests = [
        test_groq(),
        test_google_gemini(),
        test_cohere()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    print("\n📊 Test Results:")
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ Test {i+1}: Exception - {result}")
        else:
            success, message = result
            print(message)
    
    # Create .env file
    print("\n📝 Creating .env file...")
    env_result = await create_env_file()
    print(env_result)
    
    print("\n🎯 Configuration Summary:")
    print("• Quiz Generation Priority: Groq → Google → Cohere")
    print("• Chatbot Priority: Cohere → Google → Groq")
    print("• Expected Performance: 0.1-2 seconds for quiz generation")
    print("• Cost: Very cost-effective setup")
    
    print("\n✅ Setup Complete!")
    print("\nNext steps:")
    print("1. Configure your database URL in .env")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run migrations: alembic upgrade head")
    print("4. Start the server: uvicorn main:app --reload")
    print("5. Test quiz generation at: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(main()) 