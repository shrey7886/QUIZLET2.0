from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class FlashcardStatus(enum.Enum):
    NEW = "new"
    LEARNING = "learning"
    REVIEWING = "reviewing"
    MASTERED = "mastered"

class FlashcardDifficulty(enum.Enum):
    AGAIN = "again"
    HARD = "hard"
    GOOD = "good"
    EASY = "easy"

class Flashcard(Base):
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # Flashcard Content
    front_content = Column(Text, nullable=False)  # Question or concept
    back_content = Column(Text, nullable=False)   # Answer or explanation
    hint = Column(Text, nullable=True)            # Optional hint
    tags = Column(JSON, default=list)             # Categories/tags
    
    # Learning Algorithm Data
    status = Column(Enum(FlashcardStatus), default=FlashcardStatus.NEW)
    difficulty_level = Column(Float, default=2.5)  # 1-5 scale
    interval = Column(Integer, default=0)          # Days until next review
    ease_factor = Column(Float, default=2.5)       # Ease factor for spaced repetition
    review_count = Column(Integer, default=0)      # Number of reviews
    correct_count = Column(Integer, default=0)     # Number of correct answers
    incorrect_count = Column(Integer, default=0)   # Number of incorrect answers
    
    # Timing
    next_review = Column(DateTime(timezone=True), nullable=True)
    last_reviewed = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="flashcards")
    question = relationship("Question", back_populates="flashcards")
    review_history = relationship("FlashcardReview", back_populates="flashcard")

class FlashcardReview(Base):
    __tablename__ = "flashcard_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    flashcard_id = Column(Integer, ForeignKey("flashcards.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Review Data
    difficulty_rating = Column(Enum(FlashcardDifficulty), nullable=False)
    response_time = Column(Float, nullable=True)  # Time taken to answer in seconds
    was_correct = Column(Boolean, nullable=False)
    confidence_level = Column(Integer, nullable=True)  # 1-5 scale
    
    # Review Context
    review_session_id = Column(String, nullable=True)  # Group reviews by session
    review_method = Column(String, default="manual")   # manual, spaced_repetition, etc.
    
    # Timestamps
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    flashcard = relationship("Flashcard", back_populates="review_history")
    user = relationship("User", back_populates="flashcard_reviews")

class FlashcardDeck(Base):
    __tablename__ = "flashcard_decks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Deck Information
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    topic = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    
    # Deck Statistics
    total_cards = Column(Integer, default=0)
    mastered_cards = Column(Integer, default=0)
    learning_cards = Column(Integer, default=0)
    review_cards = Column(Integer, default=0)
    
    # Study Settings
    daily_limit = Column(Integer, default=20)  # Cards per day
    new_cards_per_day = Column(Integer, default=10)
    review_cards_per_day = Column(Integer, default=50)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_studied = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="flashcard_decks")
    flashcards = relationship("Flashcard", secondary="deck_flashcards")

class DeckFlashcard(Base):
    __tablename__ = "deck_flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("flashcard_decks.id"), nullable=False)
    flashcard_id = Column(Integer, ForeignKey("flashcards.id"), nullable=False)
    
    # Position in deck
    position = Column(Integer, nullable=False)
    
    # Timestamps
    added_at = Column(DateTime(timezone=True), server_default=func.now())

class StudySession(Base):
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    deck_id = Column(Integer, ForeignKey("flashcard_decks.id"), nullable=True)
    
    # Session Data
    session_type = Column(String, nullable=False)  # spaced_repetition, cram, review
    total_cards = Column(Integer, default=0)
    correct_cards = Column(Integer, default=0)
    incorrect_cards = Column(Integer, default=0)
    
    # Timing
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Float, nullable=True)  # in minutes
    
    # Performance
    accuracy = Column(Float, default=0.0)
    average_response_time = Column(Float, default=0.0)
    
    # Relationships
    user = relationship("User", back_populates="study_sessions")
    deck = relationship("FlashcardDeck", back_populates="study_sessions") 