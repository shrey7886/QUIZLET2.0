import os
from pydantic_settings import BaseSettings
from typing import Optional, Dict, List

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./quizlet.db"
    
    # For Vercel deployment - use environment variable if available
    @property
    def database_url_property(self):
        return os.getenv("DATABASE_URL", self.database_url)
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # LLM Providers Configuration
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    
    # Anthropic (Claude)
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # Google (Gemini)
    google_api_key: Optional[str] = None
    google_model: str = "gemini-1.5-flash"
    
    # Groq (Ultra-fast)
    groq_api_key: Optional[str] = None
    groq_model: str = "mixtral-8x7b-32768"
    
    # Cohere
    cohere_api_key: Optional[str] = None
    cohere_model: str = "command-r-plus"
    
    # Mistral AI
    mistral_api_key: Optional[str] = None
    mistral_model: str = "mistral-large-latest"
    
    # Ollama (Local)
    ollama_base_url: Optional[str] = None
    ollama_model: str = "llama3.1:8b"
    
    # LLM Strategy Configuration
    quiz_generation_models: str = "groq,google,cohere"
    chatbot_models: str = "cohere,google,groq"
    
    # Fallback Strategy
    enable_fallback: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30
    
    # App
    app_name: str = "Dynamic Quiz API"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings() 