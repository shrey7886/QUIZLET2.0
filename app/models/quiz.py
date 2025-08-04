from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    num_questions = Column(Integer, nullable=False)
    time_limit = Column(Integer, nullable=False)  # in minutes
    score = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz")
    user_answers = relationship("UserAnswer", back_populates="quiz")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # ["A", "B", "C", "D"]
    correct_answer = Column(Integer, nullable=False)  # Index of correct answer (0-3)
    explanation = Column(Text, nullable=True)
    question_number = Column(Integer, nullable=False)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    user_answers = relationship("UserAnswer", back_populates="question")

class UserAnswer(Base):
    __tablename__ = "user_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_answer = Column(Integer, nullable=False)  # Index of selected answer (0-3)
    is_correct = Column(Boolean, nullable=False)
    time_taken = Column(Float, nullable=True)  # in seconds
    answered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_answers")
    quiz = relationship("Quiz", back_populates="user_answers")
    question = relationship("Question", back_populates="user_answers")

class QuizHistory(Base):
    __tablename__ = "quiz_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    num_questions = Column(Integer, nullable=False)
    time_limit = Column(Integer, nullable=False)
    questions_summary = Column(Text, nullable=True)  # Summary of questions for repetition avoidance
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="quiz_history") 