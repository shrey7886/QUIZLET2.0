# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .quiz import Quiz, Question, UserAnswer, QuizHistory
from .analytics import UserProgress, TopicAnalytics, DifficultyAnalytics, QuestionAnalytics, LearningPath
from .chat import ChatRoom, ChatParticipant, ChatMessage, StudyGroup, StudyGroupMember, ChatNotification
from .flashcards import Flashcard, FlashcardReview, FlashcardDeck, DeckFlashcard, StudySession

# Export all models
__all__ = [
    # User models
    "User",
    
    # Quiz models
    "Quiz", "Question", "UserAnswer", "QuizHistory",
    
    # Analytics models
    "UserProgress", "TopicAnalytics", 
    "DifficultyAnalytics", "QuestionAnalytics", "LearningPath",
    
    # Chat models
    "ChatRoom", "ChatParticipant", "ChatMessage", 
    "StudyGroup", "StudyGroupMember", "ChatNotification",
    
    # Flashcard models
    "Flashcard", "FlashcardReview", "FlashcardDeck", "DeckFlashcard", "StudySession"
] 