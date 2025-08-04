from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Analytics Relationships
    progress = relationship("UserProgress", back_populates="user", uselist=False)
    topic_analytics = relationship("TopicAnalytics", back_populates="user")
    difficulty_analytics = relationship("DifficultyAnalytics", back_populates="user")
    quiz_history = relationship("QuizHistory", back_populates="user")
    question_analytics = relationship("QuestionAnalytics", back_populates="user")
    learning_paths = relationship("LearningPath", back_populates="user")
    
    # Quiz Relationships
    quizzes = relationship("Quiz", back_populates="user")
    user_answers = relationship("UserAnswer", back_populates="user")
    
    # Chat Relationships
    chat_messages = relationship("ChatMessage", back_populates="user")
    chat_participations = relationship("ChatParticipant", back_populates="user")
    chat_notifications = relationship("ChatNotification", back_populates="user")
    created_rooms = relationship("ChatRoom", back_populates="creator")
    # topic_suggestions = relationship("TopicSuggestion", foreign_keys="[TopicSuggestion.user_id]", back_populates="user")  # Temporarily disabled
    created_study_groups = relationship("StudyGroup", back_populates="creator")
    study_group_memberships = relationship("StudyGroupMember", back_populates="user") 