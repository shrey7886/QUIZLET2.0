from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.quiz import Quiz, Question, UserAnswer, QuizHistory
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
    Generate a new quiz using LLM service with history tracking.
    """
    
    try:
        # Check user's quiz history to avoid repetition
        recent_quizzes = db.query(QuizHistory).filter(
            QuizHistory.user_id == current_user.id,
            QuizHistory.topic == config.topic
        ).order_by(QuizHistory.created_at.desc()).limit(5).all()
        
        # Create context for LLM to avoid repetition
        history_context = ""
        if recent_quizzes:
            history_context = f"\n\nAvoid these recent questions from user's history:\n"
            for quiz in recent_quizzes:
                history_context += f"- {quiz.questions_summary}\n"
        
        # Generate quiz using LLM service
        questions = await llm_service.generate_quiz(config, history_context)
        
        # Create quiz history record
        quiz_history = QuizHistory(
            user_id=current_user.id,
            topic=config.topic,
            difficulty=config.difficulty,
            num_questions=config.num_questions,
            time_limit=config.time_limit,
            questions_summary=", ".join([q.question[:50] + "..." for q in questions]),
            created_at=datetime.utcnow()
        )
        db.add(quiz_history)
        db.commit()
        
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
    
    # Get quiz and all answers
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Get all questions for this quiz
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    
    # Get all user answers
    user_answers = db.query(UserAnswer).filter(
        UserAnswer.quiz_id == quiz_id,
        UserAnswer.user_id == current_user.id
    ).all()
    
    # Calculate results
    total_questions = len(questions)
    correct_answers = sum(1 for answer in user_answers if answer.is_correct)
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Calculate time taken
    total_time = sum(answer.time_taken for answer in user_answers if answer.time_taken)
    
    # Create quiz result
    result = QuizResult(
        quiz_id=quiz_id,
        user_id=current_user.id,
        total_questions=total_questions,
        correct_answers=correct_answers,
        score=score,
        time_taken=total_time,
        completed_at=datetime.utcnow()
    )
    
    # Update quiz completion status
    quiz.is_completed = True
    quiz.completed_at = datetime.utcnow()
    quiz.score = score
    
    db.commit()
    
    return result

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
    
    # Get questions
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    
    return {
        "quiz_id": quiz_id,
        "questions": questions
    }

@router.post("/chat")
async def chat_with_tutor(
    message: ChatMessage,
    current_user: User = Depends(get_current_active_user)
):
    """
    Chat with AI tutor for quiz-related help.
    """
    
    try:
        # Get response from LLM service
        response = await llm_service.get_chat_response(
            message=message.content,
            context=message.context
        )
        
        return {
            "message": response,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat response: {str(e)}"
        )

@router.get("/stats")
async def get_quiz_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's quiz statistics.
    """
    
    # Get total quizzes
    total_quizzes = db.query(Quiz).filter(Quiz.user_id == current_user.id).count()
    
    # Get completed quizzes
    completed_quizzes = db.query(Quiz).filter(
        Quiz.user_id == current_user.id,
        Quiz.is_completed == True
    ).count()
    
    # Get average score
    avg_score = db.query(Quiz.score).filter(
        Quiz.user_id == current_user.id,
        Quiz.is_completed == True
    ).all()
    
    avg_score = sum(score[0] for score in avg_score) / len(avg_score) if avg_score else 0
    
    # Get total questions answered
    total_questions = db.query(UserAnswer).filter(
        UserAnswer.user_id == current_user.id
    ).count()
    
    # Get correct answers
    correct_answers = db.query(UserAnswer).filter(
        UserAnswer.user_id == current_user.id,
        UserAnswer.is_correct == True
    ).count()
    
    return {
        "total_quizzes": total_quizzes,
        "completed_quizzes": completed_quizzes,
        "average_score": round(avg_score, 2),
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "accuracy": round((correct_answers / total_questions) * 100, 2) if total_questions > 0 else 0
    } 