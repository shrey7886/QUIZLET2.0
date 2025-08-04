from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.core.redis_client import get_redis
from app.models.user import User
from app.models.quiz import Quiz, Question, UserAnswer
from app.schemas.quiz import (
    QuizConfig, QuizResponse, QuizCreate, Quiz as QuizSchema,
    UserAnswerCreate, QuizResult, ChatMessage
)
from app.services.openai_service import OpenAIService

router = APIRouter()

@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    config: QuizConfig,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Generate a new quiz using OpenAI with caching for performance.
    """
    
    # Create cache key for this quiz configuration
    cache_key = f"quiz:{current_user.id}:{config.topic}:{config.difficulty}:{config.num_questions}"
    
    # Check cache first
    cached_quiz = await redis.get(cache_key)
    if cached_quiz:
        return json.loads(cached_quiz)
    
    try:
        # Generate quiz using OpenAI
        questions = await OpenAIService.generate_quiz(config)
        
        # Create quiz in database
        db_quiz = Quiz(
            user_id=current_user.id,
            topic=config.topic,
            difficulty=config.difficulty,
            num_questions=config.num_questions,
            time_limit=config.time_limit
        )
        db.add(db_quiz)
        db.commit()
        db.refresh(db_quiz)
        
        # Store questions in database
        for i, question_data in enumerate(questions, 1):
            db_question = Question(
                quiz_id=db_quiz.id,
                question_text=question_data.question,
                options=question_data.options,
                correct_answer=question_data.correct_answer,
                explanation=question_data.explanation,
                question_number=i
            )
            db.add(db_question)
        
        db.commit()
        
        # Cache the quiz for 1 hour
        quiz_response = QuizResponse(quiz=questions)
        await redis.setex(cache_key, 3600, json.dumps(quiz_response.dict()))
        
        return quiz_response
        
    except Exception as e:
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
        response = await OpenAIService.get_chat_response(message.message, message.context)
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat response: {str(e)}"
        ) 