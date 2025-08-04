from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class DifficultyLevel(enum.Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

class TopicCategory(enum.Enum):
    PROGRAMMING = "Programming"
    MATHEMATICS = "Mathematics"
    SCIENCE = "Science"
    HISTORY = "History"
    LITERATURE = "Literature"
    LANGUAGES = "Languages"
    BUSINESS = "Business"
    TECHNOLOGY = "Technology"
    OTHER = "Other"

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Overall Statistics
    total_quizzes_taken = Column(Integer, default=0)
    total_questions_answered = Column(Integer, default=0)
    total_correct_answers = Column(Integer, default=0)
    total_time_spent = Column(Float, default=0.0)  # in minutes
    average_score = Column(Float, default=0.0)
    average_accuracy = Column(Float, default=0.0)
    
    # Streak Information
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_quiz_date = Column(DateTime(timezone=True), nullable=True)
    
    # Learning Progress
    topics_covered = Column(JSON, default=list)  # List of topics
    difficulty_progress = Column(JSON, default=dict)  # {"Easy": 0.8, "Medium": 0.6, "Hard": 0.4}
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="progress")
    topic_analytics = relationship("TopicAnalytics", back_populates="user_progress")
    difficulty_analytics = relationship("DifficultyAnalytics", back_populates="user_progress")

class TopicAnalytics(Base):
    __tablename__ = "topic_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id"), nullable=False)
    
    # Topic Information
    topic = Column(String, nullable=False)
    category = Column(Enum(TopicCategory), nullable=False)
    
    # Performance Metrics
    quizzes_taken = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    total_time_spent = Column(Float, default=0.0)  # in minutes
    
    # Scores by Difficulty
    easy_score = Column(Float, default=0.0)
    medium_score = Column(Float, default=0.0)
    hard_score = Column(Float, default=0.0)
    
    # Trend Analysis
    improvement_rate = Column(Float, default=0.0)  # Percentage improvement over time
    last_quiz_date = Column(DateTime(timezone=True), nullable=True)
    best_score = Column(Float, default=0.0)
    average_score = Column(Float, default=0.0)
    
    # Weak Areas
    weak_areas = Column(JSON, default=list)  # List of specific concepts user struggles with
    recommended_topics = Column(JSON, default=list)  # Topics to focus on next
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="topic_analytics")
    user_progress = relationship("UserProgress", back_populates="topic_analytics")

class DifficultyAnalytics(Base):
    __tablename__ = "difficulty_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id"), nullable=False)
    
    # Difficulty Level
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    
    # Performance Metrics
    quizzes_taken = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    total_time_spent = Column(Float, default=0.0)  # in minutes
    
    # Score Analysis
    average_score = Column(Float, default=0.0)
    best_score = Column(Float, default=0.0)
    worst_score = Column(Float, default=0.0)
    
    # Time Analysis
    average_time_per_question = Column(Float, default=0.0)  # in seconds
    fastest_completion = Column(Float, default=0.0)  # in minutes
    slowest_completion = Column(Float, default=0.0)  # in minutes
    
    # Progress Tracking
    improvement_trend = Column(JSON, default=list)  # List of scores over time
    readiness_score = Column(Float, default=0.0)  # How ready user is for next difficulty
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="difficulty_analytics")
    user_progress = relationship("UserProgress", back_populates="difficulty_analytics")

class QuizHistory(Base):
    __tablename__ = "quiz_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    
    # Quiz Details
    topic = Column(String, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    num_questions = Column(Integer, nullable=False)
    time_limit = Column(Integer, nullable=False)  # in minutes
    
    # Performance Results
    score = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    time_taken = Column(Float, nullable=False)  # in minutes
    
    # Detailed Analysis
    question_breakdown = Column(JSON, nullable=False)  # Detailed analysis of each question
    weak_areas_identified = Column(JSON, default=list)  # Areas that need improvement
    strengths_identified = Column(JSON, default=list)  # Areas of strength
    
    # Time Analysis
    average_time_per_question = Column(Float, nullable=False)  # in seconds
    questions_answered_quickly = Column(Integer, default=0)  # Questions answered in <30 seconds
    questions_answered_slowly = Column(Integer, default=0)  # Questions answered in >2 minutes
    
    # Difficulty Progression
    difficulty_level = Column(String, nullable=False)  # Easy, Medium, Hard
    next_recommended_difficulty = Column(String, nullable=True)
    
    # Learning Insights
    concepts_mastered = Column(JSON, default=list)
    concepts_to_review = Column(JSON, default=list)
    recommended_next_topics = Column(JSON, default=list)
    
    # Timestamps
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="quiz_history")
    quiz = relationship("Quiz", back_populates="history")

class QuestionAnalytics(Base):
    __tablename__ = "question_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # Question Performance
    times_answered = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    average_time_taken = Column(Float, default=0.0)  # in seconds
    
    # Difficulty Analysis
    perceived_difficulty = Column(Float, default=0.0)  # User's perceived difficulty (1-10)
    actual_difficulty = Column(Float, default=0.0)  # Based on success rate
    
    # Learning Progress
    first_attempt_correct = Column(Boolean, nullable=True)
    improvement_trend = Column(JSON, default=list)  # List of attempts over time
    mastery_level = Column(Float, default=0.0)  # 0-1 scale of mastery
    
    # Concept Mapping
    related_concepts = Column(JSON, default=list)  # Related concepts for this question
    prerequisite_concepts = Column(JSON, default=list)  # Concepts needed to understand this
    
    # Timestamps
    first_attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    last_attempted_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="question_analytics")
    question = relationship("Question", back_populates="analytics")

class LearningPath(Base):
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Path Information
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(TopicCategory), nullable=False)
    
    # Progress Tracking
    current_level = Column(Integer, default=1)
    total_levels = Column(Integer, nullable=False)
    completion_percentage = Column(Float, default=0.0)
    
    # Path Structure
    topics_sequence = Column(JSON, nullable=False)  # Ordered list of topics
    difficulty_progression = Column(JSON, nullable=False)  # Difficulty for each level
    prerequisites = Column(JSON, default=list)  # Prerequisites for this path
    
    # Performance
    average_score = Column(Float, default=0.0)
    time_spent = Column(Float, default=0.0)  # in minutes
    quizzes_completed = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="learning_paths") 