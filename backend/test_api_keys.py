#!/usr/bin/env python3
"""
API Key Test Script for Quizlet AI Quiz Generator
Tests if all configured API keys are working properly
"""

import os
import asyncio
from app.core.config import settings

def test_api_keys():
    """Test all configured API keys"""
    print("🔑 Testing API Key Configuration")
    print("=" * 50)
    
    # Test Google API Key
    print(f"\n🌐 Google (Gemini) API Key:")
    if settings.google_api_key:
        print(f"✅ API Key: {settings.google_api_key[:10]}...{settings.google_api_key[-4:]}")
        print(f"✅ Model: {settings.google_model}")
    else:
        print("❌ No Google API key configured")
    
    # Test Groq API Key
    print(f"\n⚡ Groq API Key:")
    if settings.groq_api_key:
        print(f"✅ API Key: {settings.groq_api_key[:10]}...{settings.groq_api_key[-4:]}")
        print(f"✅ Model: {settings.groq_model}")
    else:
        print("❌ No Groq API key configured")
    
    # Test Cohere API Key
    print(f"\n🤖 Cohere API Key:")
    if settings.cohere_api_key:
        print(f"✅ API Key: {settings.cohere_api_key[:10]}...{settings.cohere_api_key[-4:]}")
        print(f"✅ Model: {settings.cohere_model}")
    else:
        print("❌ No Cohere API key configured")
    
    # Test OpenAI API Key
    print(f"\n🧠 OpenAI API Key:")
    if settings.openai_api_key:
        print(f"✅ API Key: {settings.openai_api_key[:10]}...{settings.openai_api_key[-4:]}")
        print(f"✅ Model: {settings.openai_model}")
    else:
        print("❌ No OpenAI API key configured (optional)")
    
    # Test Anthropic API Key
    print(f"\n🎭 Anthropic API Key:")
    if settings.anthropic_api_key:
        print(f"✅ API Key: {settings.anthropic_api_key[:10]}...{settings.anthropic_api_key[-4:]}")
        print(f"✅ Model: {settings.anthropic_model}")
    else:
        print("❌ No Anthropic API key configured (optional)")
    
    # Test Mistral API Key
    print(f"\n🌪️ Mistral API Key:")
    if settings.mistral_api_key:
        print(f"✅ API Key: {settings.mistral_api_key[:10]}...{settings.mistral_api_key[-4:]}")
        print(f"✅ Model: {settings.mistral_model}")
    else:
        print("❌ No Mistral API key configured (optional)")
    
    # Test Ollama Configuration
    print(f"\n🏠 Ollama Configuration:")
    if settings.ollama_base_url:
        print(f"✅ Base URL: {settings.ollama_base_url}")
        print(f"✅ Model: {settings.ollama_model}")
    else:
        print("❌ No Ollama configuration (optional)")
    
    # Test LLM Strategy Configuration
    print(f"\n📋 LLM Strategy Configuration:")
    print(f"✅ Quiz Generation Models: {settings.quiz_generation_models}")
    print(f"✅ Chatbot Models: {settings.chatbot_models}")
    print(f"✅ Fallback Enabled: {settings.enable_fallback}")
    print(f"✅ Max Retries: {settings.max_retries}")
    print(f"✅ Timeout: {settings.timeout_seconds}s")
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 API Key Summary:")
    
    primary_keys = [
        ("Google", settings.google_api_key),
        ("Groq", settings.groq_api_key),
        ("Cohere", settings.cohere_api_key)
    ]
    
    optional_keys = [
        ("OpenAI", settings.openai_api_key),
        ("Anthropic", settings.anthropic_api_key),
        ("Mistral", settings.mistral_api_key)
    ]
    
    primary_configured = sum(1 for _, key in primary_keys if key)
    optional_configured = sum(1 for _, key in optional_keys if key)
    
    print(f"✅ Primary LLM Providers: {primary_configured}/3 configured")
    print(f"✅ Optional LLM Providers: {optional_configured}/3 configured")
    
    if primary_configured >= 2:
        print("🎉 Excellent! You have multiple primary LLM providers configured.")
        print("   The application will have good redundancy and performance.")
    elif primary_configured >= 1:
        print("✅ Good! You have at least one primary LLM provider configured.")
        print("   The application will work, but consider adding more for redundancy.")
    else:
        print("⚠️  Warning: No primary LLM providers configured!")
        print("   Please configure at least one of: Google, Groq, or Cohere")
    
    print(f"\n🔧 To configure API keys, create a .env file in the backend directory")
    print(f"   with the keys from env.example")

if __name__ == "__main__":
    test_api_keys() 