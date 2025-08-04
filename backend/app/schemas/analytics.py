from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

class TopicCategory(str, Enum):
    PROGRAMMING = "Programming"
    MATHEMATICS = "Mathematics"
    SCIENCE = "Science"
    HISTORY = "History"
    LITERATURE = "Literature"
    LANGUAGES = "Languages"
    BUSINESS = "Business"
    TECHNOLOGY = "Technology"
    OTHER = "Other"

# User Progress Schemas
class UserProgressBase(BaseModel):
    total_quizzes_taken: int = 0
    total_questions_answered: int = 0
    total_correct_answers: int = 0
    total_time_spent: float = 0.0
    average_score: float = 0.0
    average_accuracy: float = 0.0
    current_streak: int = 0
    longest_streak: int = 0
    topics_covered: List[str] = []
    difficulty_progress: Dict[str, float] = {}

class UserProgress(UserProgressBase):
    id: int
    user_id: int
    last_quiz_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Topic Analytics Schemas
class TopicAnalyticsBase(BaseModel):
    topic: str
    category: TopicCategory
    quizzes_taken: int = 0
    questions_answered: int = 0
    correct_answers: int = 0
    total_time_spent: float = 0.0
    easy_score: float = 0.0
    medium_score: float = 0.0
    hard_score: float = 0.0
    improvement_rate: float = 0.0
    best_score: float = 0.0
    average_score: float = 0.0
    weak_areas: List[str] = []
    recommended_topics: List[str] = []

class TopicAnalytics(TopicAnalyticsBase):
    id: int
    user_id: int
    user_progress_id: int
    last_quiz_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Difficulty Analytics Schemas
class DifficultyAnalyticsBase(BaseModel):
    difficulty: DifficultyLevel
    quizzes_taken: int = 0
    questions_answered: int = 0
    correct_answers: int = 0
    total_time_spent: float = 0.0
    average_score: float = 0.0
    best_score: float = 0.0
    worst_score: float = 0.0
    average_time_per_question: float = 0.0
    fastest_completion: float = 0.0
    slowest_completion: float = 0.0
    improvement_trend: List[float] = []
    readiness_score: float = 0.0

class DifficultyAnalytics(DifficultyAnalyticsBase):
    id: int
    user_id: int
    user_progress_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Quiz History Schemas
class QuestionBreakdown(BaseModel):
    question_id: int
    question_text: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    time_taken: float
    difficulty_perceived: Optional[float] = None

class QuizHistoryBase(BaseModel):
    topic: str
    difficulty: DifficultyLevel
    num_questions: int
    time_limit: int
    score: float
    accuracy: float
    correct_answers: int
    total_questions: int
    time_taken: float
    question_breakdown: List[QuestionBreakdown]
    weak_areas_identified: List[str] = []
    strengths_identified: List[str] = []
    average_time_per_question: float
    questions_answered_quickly: int = 0
    questions_answered_slowly: int = 0
    difficulty_level: str
    next_recommended_difficulty: Optional[str] = None
    concepts_mastered: List[str] = []
    concepts_to_review: List[str] = []
    recommended_next_topics: List[str] = []

class QuizHistory(QuizHistoryBase):
    id: int
    user_id: int
    quiz_id: int
    completed_at: datetime
    
    class Config:
        from_attributes = True

# Question Analytics Schemas
class QuestionAnalyticsBase(BaseModel):
    times_answered: int = 0
    times_correct: int = 0
    average_time_taken: float = 0.0
    perceived_difficulty: float = 0.0
    actual_difficulty: float = 0.0
    first_attempt_correct: Optional[bool] = None
    improvement_trend: List[Dict[str, Any]] = []
    mastery_level: float = 0.0
    related_concepts: List[str] = []
    prerequisite_concepts: List[str] = []

class QuestionAnalytics(QuestionAnalyticsBase):
    id: int
    user_id: int
    question_id: int
    first_attempted_at: datetime
    last_attempted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Learning Path Schemas
class LearningPathBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: TopicCategory
    current_level: int = 1
    total_levels: int
    completion_percentage: float = 0.0
    topics_sequence: List[str]
    difficulty_progression: List[str]
    prerequisites: List[str] = []
    average_score: float = 0.0
    time_spent: float = 0.0
    quizzes_completed: int = 0
    is_active: bool = True

class LearningPath(LearningPathBase):
    id: int
    user_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Analytics Summary Schemas
class AnalyticsSummary(BaseModel):
    overall_progress: UserProgress
    topic_performance: List[TopicAnalytics]
    difficulty_performance: List[DifficultyAnalytics]
    recent_quizzes: List[QuizHistory]
    weak_areas: List[str]
    strengths: List[str]
    recommended_actions: List[str]
    learning_insights: Dict[str, Any]

# Performance Trends
class PerformanceTrend(BaseModel):
    date: datetime
    score: float
    accuracy: float
    time_taken: float
    topic: str
    difficulty: str

# Weak Areas Analysis
class WeakAreaAnalysis(BaseModel):
    topic: str
    concept: str
    error_rate: float
    total_attempts: int
    recommended_resources: List[str]
    practice_questions_needed: int

# Learning Recommendations
class LearningRecommendation(BaseModel):
    type: str  # "topic", "difficulty", "concept"
    title: str
    description: str
    priority: int  # 1-5, where 5 is highest
    estimated_time: int  # in minutes
    prerequisites: List[str]
    resources: List[str]

# Analytics Dashboard Response
class AnalyticsDashboard(BaseModel):
    summary: AnalyticsSummary
    performance_trends: List[PerformanceTrend]
    weak_areas: List[WeakAreaAnalysis]
    recommendations: List[LearningRecommendation]
    quiz_history: List[QuizHistory]
    learning_paths: List[LearningPath] 