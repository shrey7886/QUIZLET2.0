from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.quiz import Quiz, Question, UserAnswer
from app.schemas.quiz import (
    QuizConfig, QuizResponse, QuizCreate, Quiz as QuizSchema,
    UserAnswerCreate, QuizResult, ChatMessage
)
from app.services.llm_service import llm_service

router = APIRouter()

@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    config: QuizConfig,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new quiz using LLM service.
    """
    
    try:
        # Generate quiz using LLM service
        questions = await llm_service.generate_quiz(config)
        
        # Return the quiz response
        quiz_response = QuizResponse(quiz=questions)
        return quiz_response
        
    except Exception as e:
        print(f"Quiz generation error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quiz: {str(e)}"
        )

@router.post("/{quiz_id}/submit-answer")
async def submit_answer(
    quiz_id: int,
    answer: UserAnswerCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Submit an answer for a specific question in a quiz.
    """
    
    # Verify quiz exists and belongs to user
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Get the question
    question = db.query(Question).filter(Question.id == answer.question_id, Question.quiz_id == quiz_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if answer already exists
    existing_answer = db.query(UserAnswer).filter(
        UserAnswer.user_id == current_user.id,
        UserAnswer.question_id == answer.question_id,
        UserAnswer.quiz_id == quiz_id
    ).first()
    
    if existing_answer:
        # Update existing answer
        existing_answer.selected_answer = answer.selected_answer
        existing_answer.is_correct = answer.selected_answer == question.correct_answer
        existing_answer.time_taken = answer.time_taken
    else:
        # Create new answer
        user_answer = UserAnswer(
            user_id=current_user.id,
            quiz_id=quiz_id,
            question_id=answer.question_id,
            selected_answer=answer.selected_answer,
            is_correct=answer.selected_answer == question.correct_answer,
            time_taken=answer.time_taken
        )
        db.add(user_answer)
    
    db.commit()
    
    return {"message": "Answer submitted successfully"}

@router.post("/{quiz_id}/complete", response_model=QuizResult)
async def complete_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Complete a quiz and calculate results.
    """
    
    # Get quiz
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Get all user answers for this quiz
    user_answers = db.query(UserAnswer).filter(
        UserAnswer.quiz_id == quiz_id,
        UserAnswer.user_id == current_user.id
    ).all()
    
    # Calculate results
    total_questions = len(user_answers)
    correct_answers = sum(1 for answer in user_answers if answer.is_correct)
    accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    score = accuracy  # Simple scoring - can be modified for different scoring systems
    
    # Update quiz with results
    quiz.score = score
    quiz.accuracy = accuracy
    quiz.completed_at = datetime.utcnow()
    
    db.commit()
    
    return QuizResult(
        quiz_id=quiz_id,
        score=score,
        accuracy=accuracy,
        total_questions=total_questions,
        correct_answers=correct_answers,
        time_taken=0,  # Calculate from start time if needed
        completed_at=quiz.completed_at
    )

@router.get("/history", response_model=List[QuizSchema])
async def get_quiz_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's quiz history.
    """
    quizzes = db.query(Quiz).filter(
        Quiz.user_id == current_user.id
    ).order_by(Quiz.created_at.desc()).all()
    
    return quizzes

@router.get("/{quiz_id}/questions")
async def get_quiz_questions(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get questions for a specific quiz.
    """
    # Verify quiz belongs to user
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).order_by(Question.question_number).all()
    
    return questions

@router.post("/chat")
async def chat_with_tutor(
    message: ChatMessage,
    current_user: User = Depends(get_current_active_user)
):
    """
    Chat with the AI tutor for help with questions.
    """
    try:
        response = await llm_service.get_chat_response(message.message, message.context)
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat response: {str(e)}"
        ) 