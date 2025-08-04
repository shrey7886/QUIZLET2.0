from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class FlashcardStatus(str, Enum):
    NEW = "new"
    LEARNING = "learning"
    REVIEWING = "reviewing"
    MASTERED = "mastered"

class FlashcardDifficulty(str, Enum):
    AGAIN = "again"
    HARD = "hard"
    GOOD = "good"
    EASY = "easy"

# Flashcard Schemas
class FlashcardBase(BaseModel):
    front_content: str = Field(..., description="Question or concept")
    back_content: str = Field(..., description="Answer or explanation")
    hint: Optional[str] = Field(None, description="Optional hint")
    tags: List[str] = Field(default_factory=list, description="Categories/tags")

class FlashcardCreate(FlashcardBase):
    question_id: int = Field(..., description="ID of the original question")

class FlashcardUpdate(BaseModel):
    front_content: Optional[str] = None
    back_content: Optional[str] = None
    hint: Optional[str] = None
    tags: Optional[List[str]] = None

class Flashcard(FlashcardBase):
    id: int
    user_id: int
    question_id: int
    status: FlashcardStatus
    difficulty_level: float
    interval: int
    ease_factor: float
    review_count: int
    correct_count: int
    incorrect_count: int
    next_review: Optional[datetime] = None
    last_reviewed: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Flashcard Review Schemas
class FlashcardReviewBase(BaseModel):
    difficulty_rating: FlashcardDifficulty
    response_time: Optional[float] = Field(None, description="Time taken to answer in seconds")
    was_correct: bool
    confidence_level: Optional[int] = Field(None, ge=1, le=5, description="1-5 scale")
    review_method: str = Field(default="manual", description="manual, spaced_repetition, etc.")

class FlashcardReviewCreate(FlashcardReviewBase):
    flashcard_id: int
    review_session_id: Optional[str] = None

class FlashcardReview(FlashcardReviewBase):
    id: int
    flashcard_id: int
    user_id: int
    review_session_id: Optional[str] = None
    reviewed_at: datetime
    
    class Config:
        from_attributes = True

# Flashcard Deck Schemas
class FlashcardDeckBase(BaseModel):
    name: str = Field(..., description="Deck name")
    description: Optional[str] = Field(None, description="Deck description")
    topic: str = Field(..., description="Topic of the deck")
    difficulty: str = Field(..., description="Difficulty level")
    daily_limit: int = Field(default=20, ge=1, le=100, description="Cards per day")
    new_cards_per_day: int = Field(default=10, ge=1, le=50, description="New cards per day")
    review_cards_per_day: int = Field(default=50, ge=1, le=200, description="Review cards per day")

class FlashcardDeckCreate(FlashcardDeckBase):
    pass

class FlashcardDeckUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    daily_limit: Optional[int] = Field(None, ge=1, le=100)
    new_cards_per_day: Optional[int] = Field(None, ge=1, le=50)
    review_cards_per_day: Optional[int] = Field(None, ge=1, le=200)

class FlashcardDeck(FlashcardDeckBase):
    id: int
    user_id: int
    total_cards: int
    mastered_cards: int
    learning_cards: int
    review_cards: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_studied: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Study Session Schemas
class StudySessionBase(BaseModel):
    session_type: str = Field(..., description="spaced_repetition, cram, review")
    deck_id: Optional[int] = None

class StudySessionCreate(StudySessionBase):
    pass

class StudySession(StudySessionBase):
    id: int
    user_id: int
    total_cards: int
    correct_cards: int
    incorrect_cards: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    accuracy: float
    average_response_time: float
    
    class Config:
        from_attributes = True

# Study Session Update
class StudySessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    total_cards: Optional[int] = None
    correct_cards: Optional[int] = None
    incorrect_cards: Optional[int] = None
    accuracy: Optional[float] = None
    average_response_time: Optional[float] = None

# Flashcard Study Schemas
class StudyCard(BaseModel):
    flashcard: Flashcard
    is_new: bool
    is_review: bool
    is_learning: bool
    interval: int
    ease_factor: float

class StudySessionResponse(BaseModel):
    session_id: str
    cards: List[StudyCard]
    total_new: int
    total_review: int
    total_learning: int
    session_type: str

class StudyProgress(BaseModel):
    session_id: str
    completed_cards: int
    total_cards: int
    correct_answers: int
    incorrect_answers: int
    accuracy: float
    average_response_time: float
    time_remaining: Optional[int] = None  # in seconds

# Spaced Repetition Algorithm Schemas
class SpacedRepetitionSettings(BaseModel):
    initial_ease_factor: float = Field(default=2.5, ge=1.3, le=5.0)
    minimum_ease_factor: float = Field(default=1.3, ge=1.0, le=2.0)
    ease_bonus: float = Field(default=0.15, ge=0.0, le=1.0)
    interval_modifier: float = Field(default=1.0, ge=0.1, le=10.0)
    maximum_interval: int = Field(default=36500, ge=1, le=36500)  # 100 years max

class SpacedRepetitionResult(BaseModel):
    new_interval: int
    new_ease_factor: float
    next_review: datetime
    status: FlashcardStatus

# Flashcard Statistics
class FlashcardStats(BaseModel):
    total_cards: int
    new_cards: int
    learning_cards: int
    review_cards: int
    mastered_cards: int
    total_reviews: int
    correct_reviews: int
    accuracy: float
    average_response_time: float
    cards_due_today: int
    cards_due_tomorrow: int

class DeckStats(BaseModel):
    deck: FlashcardDeck
    stats: FlashcardStats
    recent_performance: List[Dict[str, Any]]
    learning_curve: List[Dict[str, Any]]

# Export Schemas
class FlashcardExport(BaseModel):
    deck_name: str
    topic: str
    difficulty: str
    created_at: datetime
    cards: List[Dict[str, Any]]
    statistics: FlashcardStats

# Search and Filter Schemas
class FlashcardSearch(BaseModel):
    query: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[FlashcardStatus] = None
    difficulty_min: Optional[float] = None
    difficulty_max: Optional[float] = None
    due_before: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class FlashcardSearchResult(BaseModel):
    flashcards: List[Flashcard]
    total_count: int
    has_more: bool 