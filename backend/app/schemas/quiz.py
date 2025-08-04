from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class QuizConfig(BaseModel):
    topic: str = Field(..., description="Quiz topic")
    difficulty: str = Field(..., description="Easy, Medium, or Hard")
    num_questions: int = Field(..., ge=1, le=15, description="Number of questions (1-15)")
    time_limit: int = Field(..., ge=1, le=120, description="Time limit in minutes")

class QuestionSchema(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str

class QuizResponse(BaseModel):
    quiz: List[QuestionSchema]

class QuizCreate(BaseModel):
    user_id: int
    topic: str
    difficulty: str
    num_questions: int
    time_limit: int

class Quiz(BaseModel):
    id: int
    user_id: int
    topic: str
    difficulty: str
    num_questions: int
    time_limit: int
    score: Optional[float] = None
    accuracy: Optional[float] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserAnswerCreate(BaseModel):
    question_id: int
    selected_answer: str
    time_taken: Optional[float] = None

class QuizResult(BaseModel):
    quiz_id: int
    score: float
    accuracy: float
    total_questions: int
    correct_answers: int
    time_taken: float
    completed_at: datetime

class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = None  # Quiz context or question context 