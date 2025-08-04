from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.quiz import Quiz, UserAnswer
from app.schemas.user import User as UserSchema

router = APIRouter()

@router.get("/profile", response_model=UserSchema)
async def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get current user's profile information.
    """
    return current_user

@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's quiz statistics.
    """
    # Get completed quizzes
    completed_quizzes = db.query(Quiz).filter(
        Quiz.user_id == current_user.id,
        Quiz.completed_at.isnot(None)
    ).all()
    
    # Calculate statistics
    total_quizzes = len(completed_quizzes)
    total_questions = sum(quiz.num_questions for quiz in completed_quizzes)
    
    # Get all user answers
    user_answers = db.query(UserAnswer).filter(
        UserAnswer.user_id == current_user.id
    ).all()
    
    correct_answers = sum(1 for answer in user_answers if answer.is_correct)
    total_answers = len(user_answers)
    overall_accuracy = (correct_answers / total_answers * 100) if total_answers > 0 else 0
    
    # Average score
    avg_score = sum(quiz.score for quiz in completed_quizzes) / total_quizzes if total_quizzes > 0 else 0
    
    return {
        "total_quizzes": total_quizzes,
        "total_questions": total_questions,
        "total_answers": total_answers,
        "correct_answers": correct_answers,
        "overall_accuracy": round(overall_accuracy, 2),
        "average_score": round(avg_score, 2)
    }

@router.get("/recent-activity")
async def get_recent_activity(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's recent quiz activity.
    """
    recent_quizzes = db.query(Quiz).filter(
        Quiz.user_id == current_user.id
    ).order_by(Quiz.created_at.desc()).limit(5).all()
    
    return recent_quizzes 