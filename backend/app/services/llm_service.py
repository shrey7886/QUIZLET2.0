import json
import asyncio
import time
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import httpx
from asyncio_throttle import Throttler

from app.core.config import settings
from app.schemas.quiz import QuizConfig, QuestionSchema

# Import LLM clients
try:
    import openai
    from anthropic import Anthropic
    import google.generativeai as genai
    from groq import Groq
    import cohere
    from mistralai.client import MistralClient
    from mistralai.models.chat_completion import ChatMessage as MistralChatMessage
    import ollama
except ImportError as e:
    print(f"Warning: Some LLM providers not available: {e}")

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, name: str, model: str, api_key: str = None):
        self.name = name
        self.model = model
        self.api_key = api_key
        self.throttler = Throttler(rate_limit=10, period=60)  # 10 requests per minute
        
    @abstractmethod
    async def generate_quiz(self, config: QuizConfig) -> List[QuestionSchema]:
        """Generate quiz questions"""
        pass
    
    @abstractmethod
    async def get_chat_response(self, message: str, context: str = None) -> str:
        """Get chatbot response"""
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self):
        super().__init__("openai", settings.openai_model, settings.openai_api_key)
        if self.api_key:
            openai.api_key = self.api_key
    
    async def generate_quiz(self, config: QuizConfig) -> List[QuestionSchema]:
        async with self.throttler:
            prompt = self._create_quiz_prompt(config)
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a quiz generation expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json"}
            )
            
            return self._parse_quiz_response(response.choices[0].message.content)
    
    async def get_chat_response(self, message: str, context: str = None) -> str:
        async with self.throttler:
            system_prompt = "You are a helpful educational tutor. Provide clear, encouraging explanations."
            user_prompt = f"Student Question: {message}\n{('Context: ' + context) if context else ''}"
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
    
    def _create_quiz_prompt(self, config: QuizConfig) -> str:
        return f"""
You are an expert quiz generator. Create a multiple choice quiz on the topic: "{config.topic}"

Requirements:
- Difficulty: {config.difficulty}
- Number of questions: {config.num_questions}
- Each question must have exactly 4 options (A, B, C, D)
- Provide clear explanations for correct answers
- Ensure questions are appropriate for the specified difficulty level

Respond ONLY with valid JSON in this exact format:
{{
  "quiz": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Detailed explanation of why this is correct."
    }}
  ]
}}

Important: Ensure all questions are unique and relevant to the topic. Make explanations educational and helpful.
"""

    def _parse_quiz_response(self, content: str) -> List[QuestionSchema]:
        quiz_data = json.loads(content)
        questions = []
        for q in quiz_data["quiz"]:
            questions.append(QuestionSchema(
                question=q["question"],
                options=q["options"],
                correct_answer=q["correct_answer"],
                explanation=q["explanation"]
            ))
        return questions

class AnthropicProvider(LLMProvider):
    def __init__(self):
        super().__init__("anthropic", settings.anthropic_model, settings.anthropic_api_key)
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
    
    async def generate_quiz(self, config: QuizConfig) -> List[QuestionSchema]:
        if not self.client:
            raise Exception("Anthropic API key not configured")
            
        async with self.throttler:
            prompt = self._create_quiz_prompt(config)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system="You are a quiz generation expert. Always respond with valid JSON.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return self._parse_quiz_response(response.content[0].text)
    
    async def get_chat_response(self, message: str, context: str = None) -> str:
        if not self.client:
            raise Exception("Anthropic API key not configured")
            
        async with self.throttler:
            system_prompt = "You are a helpful educational tutor. Provide clear, encouraging explanations."
            user_prompt = f"Student Question: {message}\n{('Context: ' + context) if context else ''}"
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            return response.content[0].text
    
    def _create_quiz_prompt(self, config: QuizConfig) -> str:
        return f"""
You are an expert quiz generator. Create a multiple choice quiz on the topic: "{config.topic}"

Requirements:
- Difficulty: {config.difficulty}
- Number of questions: {config.num_questions}
- Each question must have exactly 4 options (A, B, C, D)
- Provide clear explanations for correct answers
- Ensure questions are appropriate for the specified difficulty level

Respond ONLY with valid JSON in this exact format:
{{
  "quiz": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Detailed explanation of why this is correct."
    }}
  ]
}}

Important: Ensure all questions are unique and relevant to the topic. Make explanations educational and helpful.
"""

    def _parse_quiz_response(self, content: str) -> List[QuestionSchema]:
        quiz_data = json.loads(content)
        questions = []
        for q in quiz_data["quiz"]:
            questions.append(QuestionSchema(
                question=q["question"],
                options=q["options"],
                correct_answer=q["correct_answer"],
                explanation=q["explanation"]
            ))
        return questions

class GoogleProvider(LLMProvider):
    def __init__(self):
        super().__init__("google", settings.google_model, settings.google_api_key)
        if self.api_key:
            genai.configure(api_key=self.api_key)
    
    async def generate_quiz(self, config: QuizConfig) -> List[QuestionSchema]:
        async with self.throttler:
            prompt = self._create_quiz_prompt(config)
            
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            
            return self._parse_quiz_response(response.text)
    
    async def get_chat_response(self, message: str, context: str = None) -> str:
        async with self.throttler:
            system_prompt = "You are a helpful educational tutor. Provide clear, encouraging explanations."
            user_prompt = f"Student Question: {message}\n{('Context: ' + context) if context else ''}"
            
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(user_prompt)
            
            return response.text
    
    def _create_quiz_prompt(self, config: QuizConfig) -> str:
        return f"""
You are an expert quiz generator. Create a multiple choice quiz on the topic: "{config.topic}"

Requirements:
- Difficulty: {config.difficulty}
- Number of questions: {config.num_questions}
- Each question must have exactly 4 options (A, B, C, D)
- Provide clear explanations for correct answers
- Ensure questions are appropriate for the specified difficulty level

Respond ONLY with valid JSON in this exact format:
{{
  "quiz": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Detailed explanation of why this is correct."
    }}
  ]
}}

Important: Ensure all questions are unique and relevant to the topic. Make explanations educational and helpful.
"""

    def _parse_quiz_response(self, content: str) -> List[QuestionSchema]:
        try:
            # Clean the content - remove markdown code blocks if present
            cleaned_content = content.strip()
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]  # Remove ```json
            if cleaned_content.startswith('```'):
                cleaned_content = cleaned_content[3:]  # Remove ```
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]  # Remove ```
            cleaned_content = cleaned_content.strip()
            
            # Try to parse as JSON
            quiz_data = json.loads(cleaned_content)
            questions = []
            for q in quiz_data["quiz"]:
                questions.append(QuestionSchema(
                    question=q["question"],
                    options=q["options"],
                    correct_answer=q["correct_answer"],
                    explanation=q["explanation"]
                ))
            return questions
        except json.JSONDecodeError as e:
            print(f"Google AI JSON parsing error: {e}")
            print(f"Raw response: {content}")
            # Fallback: try to extract JSON from the response
            try:
                # Look for JSON-like content between curly braces
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != 0:
                    json_content = content[start:end]
                    quiz_data = json.loads(json_content)
                    questions = []
                    for q in quiz_data["quiz"]:
                        questions.append(QuestionSchema(
                            question=q["question"],
                            options=q["options"],
                            correct_answer=q["correct_answer"],
                            explanation=q["explanation"]
                        ))
                    return questions
            except Exception as fallback_error:
                print(f"Fallback parsing also failed: {fallback_error}")
                raise Exception(f"Failed to parse Google AI response as JSON: {content[:200]}...")

class GroqProvider(LLMProvider):
    def __init__(self):
        super().__init__("groq", settings.groq_model, settings.groq_api_key)
        try:
            self.client = Groq(api_key=self.api_key) if self.api_key else None
        except Exception as e:
            print(f"Warning: Failed to initialize Groq client: {e}")
            self.client = None
    
    async def generate_quiz(self, config: QuizConfig) -> List[QuestionSchema]:
        if not self.client:
            raise Exception("Groq API key not configured")
            
        async with self.throttler:
            prompt = self._create_quiz_prompt(config)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a quiz generation expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return self._parse_quiz_response(response.choices[0].message.content)
    
    async def get_chat_response(self, message: str, context: str = None) -> str:
        if not self.client:
            raise Exception("Groq API key not configured")
            
        async with self.throttler:
            system_prompt = "You are a helpful educational tutor. Provide clear, encouraging explanations."
            user_prompt = f"Student Question: {message}\n{('Context: ' + context) if context else ''}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
    
    def _create_quiz_prompt(self, config: QuizConfig) -> str:
        return f"""
You are an expert quiz generator. Create a multiple choice quiz on the topic: "{config.topic}"

Requirements:
- Difficulty: {config.difficulty}
- Number of questions: {config.num_questions}
- Each question must have exactly 4 options (A, B, C, D)
- Provide clear explanations for correct answers
- Ensure questions are appropriate for the specified difficulty level

Respond ONLY with valid JSON in this exact format:
{{
  "quiz": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Detailed explanation of why this is correct."
    }}
  ]
}}

Important: Ensure all questions are unique and relevant to the topic. Make explanations educational and helpful.
"""

    def _parse_quiz_response(self, content: str) -> List[QuestionSchema]:
        quiz_data = json.loads(content)
        questions = []
        for q in quiz_data["quiz"]:
            questions.append(QuestionSchema(
                question=q["question"],
                options=q["options"],
                correct_answer=q["correct_answer"],
                explanation=q["explanation"]
            ))
        return questions

class CohereProvider(LLMProvider):
    def __init__(self):
        super().__init__("cohere", settings.cohere_model, settings.cohere_api_key)
        self.client = cohere.Client(self.api_key) if self.api_key else None
    
    async def generate_quiz(self, config: QuizConfig) -> List[QuestionSchema]:
        if not self.client:
            raise Exception("Cohere API key not configured")
            
        async with self.throttler:
            prompt = self._create_quiz_prompt(config)
            
            response = self.client.chat(
                model=self.model,
                message=prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            return self._parse_quiz_response(response.text)
    
    async def get_chat_response(self, message: str, context: str = None) -> str:
        if not self.client:
            raise Exception("Cohere API key not configured")
            
        async with self.throttler:
            user_prompt = f"Student Question: {message}\n{('Context: ' + context) if context else ''}"
            
            response = self.client.chat(
                model=self.model,
                message=user_prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.text
    
    def _create_quiz_prompt(self, config: QuizConfig) -> str:
        return f"""
You are an expert quiz generator. Create a multiple choice quiz on the topic: "{config.topic}"

Requirements:
- Difficulty: {config.difficulty}
- Number of questions: {config.num_questions}
- Each question must have exactly 4 options (A, B, C, D)
- Provide clear explanations for correct answers
- Ensure questions are appropriate for the specified difficulty level

Respond ONLY with valid JSON in this exact format:
{{
  "quiz": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Detailed explanation of why this is correct."
    }}
  ]
}}

Important: Ensure all questions are unique and relevant to the topic. Make explanations educational and helpful.
"""

    def _parse_quiz_response(self, content: str) -> List[QuestionSchema]:
        quiz_data = json.loads(content)
        questions = []
        for q in quiz_data["quiz"]:
            questions.append(QuestionSchema(
                question=q["question"],
                options=q["options"],
                correct_answer=q["correct_answer"],
                explanation=q["explanation"]
            ))
        return questions

class MistralProvider(LLMProvider):
    def __init__(self):
        super().__init__("mistral", settings.mistral_model, settings.mistral_api_key)
        self.client = MistralClient(api_key=self.api_key) if self.api_key else None
    
    async def generate_quiz(self, config: QuizConfig) -> List[QuestionSchema]:
        if not self.client:
            raise Exception("Mistral API key not configured")
            
        async with self.throttler:
            prompt = self._create_quiz_prompt(config)
            
            messages = [
                MistralChatMessage(role="system", content="You are a quiz generation expert. Always respond with valid JSON."),
                MistralChatMessage(role="user", content=prompt)
            ]
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return self._parse_quiz_response(response.choices[0].message.content)
    
    async def get_chat_response(self, message: str, context: str = None) -> str:
        if not self.client:
            raise Exception("Mistral API key not configured")
            
        async with self.throttler:
            system_prompt = "You are a helpful educational tutor. Provide clear, encouraging explanations."
            user_prompt = f"Student Question: {message}\n{('Context: ' + context) if context else ''}"
            
            messages = [
                MistralChatMessage(role="system", content=system_prompt),
                MistralChatMessage(role="user", content=user_prompt)
            ]
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
    
    def _create_quiz_prompt(self, config: QuizConfig) -> str:
        return f"""
You are an expert quiz generator. Create a multiple choice quiz on the topic: "{config.topic}"

Requirements:
- Difficulty: {config.difficulty}
- Number of questions: {config.num_questions}
- Each question must have exactly 4 options (A, B, C, D)
- Provide clear explanations for correct answers
- Ensure questions are appropriate for the specified difficulty level

Respond ONLY with valid JSON in this exact format:
{{
  "quiz": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Detailed explanation of why this is correct."
    }}
  ]
}}

Important: Ensure all questions are unique and relevant to the topic. Make explanations educational and helpful.
"""

    def _parse_quiz_response(self, content: str) -> List[QuestionSchema]:
        quiz_data = json.loads(content)
        questions = []
        for q in quiz_data["quiz"]:
            questions.append(QuestionSchema(
                question=q["question"],
                options=q["options"],
                correct_answer=q["correct_answer"],
                explanation=q["explanation"]
            ))
        return questions

class OllamaProvider(LLMProvider):
    def __init__(self):
        super().__init__("ollama", settings.ollama_model, None)
        self.base_url = settings.ollama_base_url or "http://localhost:11434"
    
    async def generate_quiz(self, config: QuizConfig) -> List[QuestionSchema]:
        async with self.throttler:
            prompt = self._create_quiz_prompt(config)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=settings.timeout_seconds
                )
                response.raise_for_status()
                result = response.json()
                
                return self._parse_quiz_response(result["response"])
    
    async def get_chat_response(self, message: str, context: str = None) -> str:
        async with self.throttler:
            user_prompt = f"Student Question: {message}\n{('Context: ' + context) if context else ''}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": user_prompt,
                        "stream": False
                    },
                    timeout=settings.timeout_seconds
                )
                response.raise_for_status()
                result = response.json()
                
                return result["response"]
    
    def _create_quiz_prompt(self, config: QuizConfig) -> str:
        return f"""
You are an expert quiz generator. Create a multiple choice quiz on the topic: "{config.topic}"

Requirements:
- Difficulty: {config.difficulty}
- Number of questions: {config.num_questions}
- Each question must have exactly 4 options (A, B, C, D)
- Provide clear explanations for correct answers
- Ensure questions are appropriate for the specified difficulty level

Respond ONLY with valid JSON in this exact format:
{{
  "quiz": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Detailed explanation of why this is correct."
    }}
  ]
}}

Important: Ensure all questions are unique and relevant to the topic. Make explanations educational and helpful.
"""

    def _parse_quiz_response(self, content: str) -> List[QuestionSchema]:
        quiz_data = json.loads(content)
        questions = []
        for q in quiz_data["quiz"]:
            questions.append(QuestionSchema(
                question=q["question"],
                options=q["options"],
                correct_answer=q["correct_answer"],
                explanation=q["explanation"]
            ))
        return questions

class MultiLLMService:
    """Service that manages multiple LLM providers with load balancing and fallback"""
    
    def __init__(self):
        self.providers = {}
        self.quiz_providers = []
        self.chatbot_providers = []
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available LLM providers"""
        
        # Initialize all providers
        if settings.openai_api_key:
            self.providers["openai"] = OpenAIProvider()
        
        if settings.anthropic_api_key:
            self.providers["anthropic"] = AnthropicProvider()
        
        if settings.google_api_key:
            self.providers["google"] = GoogleProvider()
        
        if settings.groq_api_key:
            self.providers["groq"] = GroqProvider()
        
        if settings.cohere_api_key:
            self.providers["cohere"] = CohereProvider()
        
        if settings.mistral_api_key:
            self.providers["mistral"] = MistralProvider()
        
        if settings.ollama_base_url:
            self.providers["ollama"] = OllamaProvider()
        
        # Set up quiz generation providers
        for provider_name in settings.quiz_generation_models:
            if provider_name in self.providers:
                self.quiz_providers.append(self.providers[provider_name])
        
        # Set up chatbot providers
        for provider_name in settings.chatbot_models:
            if provider_name in self.providers:
                self.chatbot_providers.append(self.providers[provider_name])
    
    async def generate_quiz(self, config: QuizConfig) -> List[QuestionSchema]:
        """Generate quiz using multiple providers with fallback"""
        
        if not self.quiz_providers:
            raise Exception("No LLM providers configured for quiz generation")
        
        # Try providers in order with fallback
        for provider in self.quiz_providers:
            try:
                start_time = time.time()
                questions = await provider.generate_quiz(config)
                generation_time = time.time() - start_time
                
                print(f"Quiz generated by {provider.name} in {generation_time:.2f}s")
                return questions
                
            except Exception as e:
                print(f"Error with {provider.name}: {str(e)}")
                if not settings.enable_fallback:
                    raise e
                continue
        
        raise Exception("All LLM providers failed to generate quiz")
    
    async def get_chat_response(self, message: str, context: str = None) -> str:
        """Get chatbot response using multiple providers with fallback"""
        
        if not self.chatbot_providers:
            raise Exception("No LLM providers configured for chatbot")
        
        # Try providers in order with fallback
        for provider in self.chatbot_providers:
            try:
                start_time = time.time()
                response = await provider.get_chat_response(message, context)
                response_time = time.time() - start_time
                
                print(f"Chat response from {provider.name} in {response_time:.2f}s")
                return response
                
            except Exception as e:
                print(f"Error with {provider.name}: {str(e)}")
                if not settings.enable_fallback:
                    raise e
                continue
        
        return "I'm sorry, I'm having trouble responding right now. Please try again later."

# Global instance
llm_service = MultiLLMService() 