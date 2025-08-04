import json
import openai
from typing import List, Dict, Any
from app.core.config import settings
from app.services.llm_service import llm_service
from app.schemas.quiz import QuizConfig, QuestionSchema

openai.api_key = settings.openai_api_key

class OpenAIService:
    @staticmethod
    async def generate_quiz(config: QuizConfig) -> List[QuestionSchema]:
        """
        Generate a quiz using multiple LLM providers with fallback strategy.
        """
        return await llm_service.generate_quiz(config)
    
    @staticmethod
    async def get_chat_response(message: str, context: str = None) -> str:
        """
        Generate a helpful response for the AI tutor chatbot using multiple providers.
        """
        return await llm_service.get_chat_response(message, context) 