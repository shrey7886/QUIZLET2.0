from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.analytics import UserProgress, TopicAnalytics, DifficultyAnalytics, QuizHistory, QuestionAnalytics, LearningPath
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    AnalyticsDashboard, QuizHistory as QuizHistorySchema, PerformanceTrend,
    WeakAreaAnalysis, LearningRecommendation, UserProgress as UserProgressSchema,
    TopicAnalytics as TopicAnalyticsSchema, DifficultyAnalytics as DifficultyAnalyticsSchema
)

router = APIRouter()

@router.get("/dashboard", response_model=AnalyticsDashboard)
async def get_analytics_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics dashboard for the current user"""
    try:
        dashboard = await AnalyticsService.get_analytics_dashboard(db, current_user.id)
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load analytics dashboard: {str(e)}")

@router.get("/progress", response_model=UserProgressSchema)
async def get_user_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user progress summary"""
    try:
        user_progress = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).first()
        if not user_progress:
            # Initialize progress if not found
            user_progress = UserProgress(user_id=current_user.id)
            db.add(user_progress)
            db.commit()
            db.refresh(user_progress)
        return user_progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load user progress: {str(e)}")

@router.get("/history", response_model=List[QuizHistorySchema])
async def get_quiz_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get quiz history with filtering options"""
    try:
        query = db.query(QuizHistory).filter(QuizHistory.user_id == current_user.id)
        
        if topic:
            query = query.filter(QuizHistory.topic.ilike(f"%{topic}%"))
        
        if difficulty:
            query = query.filter(QuizHistory.difficulty == difficulty)
        
        if start_date:
            query = query.filter(QuizHistory.completed_at >= start_date)
        
        if end_date:
            query = query.filter(QuizHistory.completed_at <= end_date)
        
        history = query.order_by(QuizHistory.completed_at.desc()).offset(offset).limit(limit).all()
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load quiz history: {str(e)}")

@router.get("/history/{quiz_id}", response_model=QuizHistorySchema)
async def get_quiz_detail(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific quiz"""
    try:
        quiz_history = db.query(QuizHistory).filter(
            and_(QuizHistory.id == quiz_id, QuizHistory.user_id == current_user.id)
        ).first()
        
        if not quiz_history:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        return quiz_history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load quiz details: {str(e)}")

@router.get("/topics", response_model=List[TopicAnalyticsSchema])
async def get_topic_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get topic-specific analytics"""
    try:
        topic_analytics = db.query(TopicAnalytics).filter(TopicAnalytics.user_id == current_user.id).all()
        return topic_analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load topic analytics: {str(e)}")

@router.get("/topics/{topic}", response_model=TopicAnalyticsSchema)
async def get_topic_detail(
    topic: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a specific topic"""
    try:
        topic_analytics = db.query(TopicAnalytics).filter(
            and_(TopicAnalytics.user_id == current_user.id, TopicAnalytics.topic == topic)
        ).first()
        
        if not topic_analytics:
            raise HTTPException(status_code=404, detail="Topic analytics not found")
        
        return topic_analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load topic details: {str(e)}")

@router.get("/difficulty", response_model=List[DifficultyAnalyticsSchema])
async def get_difficulty_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get difficulty-level analytics"""
    try:
        difficulty_analytics = db.query(DifficultyAnalytics).filter(DifficultyAnalytics.user_id == current_user.id).all()
        return difficulty_analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load difficulty analytics: {str(e)}")

@router.get("/trends", response_model=List[PerformanceTrend])
async def get_performance_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=7, le=365),
    topic: Optional[str] = None
):
    """Get performance trends over time"""
    try:
        trends = AnalyticsService._get_performance_trends(db, current_user.id)
        
        if topic:
            trends = [t for t in trends if t.topic == topic]
        
        # Filter by days
        cutoff_date = datetime.now() - timedelta(days=days)
        trends = [t for t in trends if t.date >= cutoff_date]
        
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load performance trends: {str(e)}")

@router.get("/weak-areas", response_model=List[WeakAreaAnalysis])
async def get_weak_areas_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weak areas analysis"""
    try:
        weak_areas = AnalyticsService._get_weak_areas_analysis(db, current_user.id)
        return weak_areas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load weak areas analysis: {str(e)}")

@router.get("/recommendations", response_model=List[LearningRecommendation])
async def get_learning_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized learning recommendations"""
    try:
        user_progress = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).first()
        topic_performance = db.query(TopicAnalytics).filter(TopicAnalytics.user_id == current_user.id).all()
        difficulty_performance = db.query(DifficultyAnalytics).filter(DifficultyAnalytics.user_id == current_user.id).all()
        weak_areas = AnalyticsService._get_weak_areas_analysis(db, current_user.id)
        
        recommendations = AnalyticsService._get_learning_recommendations(
            user_progress, topic_performance, difficulty_performance, weak_areas
        )
        
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load recommendations: {str(e)}")

@router.get("/stats/summary")
async def get_stats_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive statistics summary"""
    try:
        user_progress = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).first()
        if not user_progress:
            raise HTTPException(status_code=404, detail="User progress not found")
        
        # Get recent quiz performance
        recent_quizzes = db.query(QuizHistory).filter(
            QuizHistory.user_id == current_user.id
        ).order_by(QuizHistory.completed_at.desc()).limit(10).all()
        
        # Calculate improvement trends
        if len(recent_quizzes) >= 2:
            recent_avg = sum(q.score for q in recent_quizzes[:5]) / min(5, len(recent_quizzes))
            older_avg = sum(q.score for q in recent_quizzes[5:10]) / min(5, len(recent_quizzes[5:]))
            improvement = recent_avg - older_avg if len(recent_quizzes) >= 10 else 0
        else:
            improvement = 0
        
        return {
            "overall_stats": {
                "total_quizzes": user_progress.total_quizzes_taken,
                "average_score": user_progress.average_score,
                "accuracy": user_progress.average_accuracy,
                "streak": user_progress.current_streak,
                "longest_streak": user_progress.longest_streak,
                "time_spent": user_progress.total_time_spent
            },
            "recent_performance": {
                "recent_quizzes": len(recent_quizzes),
                "average_recent_score": sum(q.score for q in recent_quizzes) / len(recent_quizzes) if recent_quizzes else 0,
                "improvement_trend": improvement
            },
            "topics_covered": user_progress.topics_covered,
            "difficulty_progress": user_progress.difficulty_progress
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load stats summary: {str(e)}")

@router.get("/stats/comparison")
async def get_performance_comparison(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    period: str = Query("month", regex="^(week|month|quarter|year)$")
):
    """Get performance comparison for different periods"""
    try:
        now = datetime.now()
        
        if period == "week":
            current_start = now - timedelta(days=7)
            previous_start = current_start - timedelta(days=7)
        elif period == "month":
            current_start = now - timedelta(days=30)
            previous_start = current_start - timedelta(days=30)
        elif period == "quarter":
            current_start = now - timedelta(days=90)
            previous_start = current_start - timedelta(days=90)
        else:  # year
            current_start = now - timedelta(days=365)
            previous_start = current_start - timedelta(days=365)
        
        # Get current period quizzes
        current_quizzes = db.query(QuizHistory).filter(
            and_(
                QuizHistory.user_id == current_user.id,
                QuizHistory.completed_at >= current_start,
                QuizHistory.completed_at <= now
            )
        ).all()
        
        # Get previous period quizzes
        previous_quizzes = db.query(QuizHistory).filter(
            and_(
                QuizHistory.user_id == current_user.id,
                QuizHistory.completed_at >= previous_start,
                QuizHistory.completed_at < current_start
            )
        ).all()
        
        # Calculate metrics
        current_avg_score = sum(q.score for q in current_quizzes) / len(current_quizzes) if current_quizzes else 0
        previous_avg_score = sum(q.score for q in previous_quizzes) / len(previous_quizzes) if previous_quizzes else 0
        
        current_avg_accuracy = sum(q.accuracy for q in current_quizzes) / len(current_quizzes) if current_quizzes else 0
        previous_avg_accuracy = sum(q.accuracy for q in previous_quizzes) / len(previous_quizzes) if previous_quizzes else 0
        
        return {
            "period": period,
            "current_period": {
                "quizzes_taken": len(current_quizzes),
                "average_score": current_avg_score,
                "average_accuracy": current_avg_accuracy,
                "total_time": sum(q.time_taken for q in current_quizzes)
            },
            "previous_period": {
                "quizzes_taken": len(previous_quizzes),
                "average_score": previous_avg_score,
                "average_accuracy": previous_avg_accuracy,
                "total_time": sum(q.time_taken for q in previous_quizzes)
            },
            "improvement": {
                "score_change": current_avg_score - previous_avg_score,
                "accuracy_change": current_avg_accuracy - previous_avg_accuracy,
                "score_percentage_change": ((current_avg_score - previous_avg_score) / previous_avg_score * 100) if previous_avg_score > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load performance comparison: {str(e)}")

@router.get("/export/history")
async def export_quiz_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    format: str = Query("json", regex="^(json|csv)$")
):
    """Export quiz history in specified format"""
    try:
        history = db.query(QuizHistory).filter(
            QuizHistory.user_id == current_user.id
        ).order_by(QuizHistory.completed_at.desc()).all()
        
        if format == "json":
            return {
                "user_id": current_user.id,
                "export_date": datetime.now().isoformat(),
                "total_quizzes": len(history),
                "history": [
                    {
                        "id": q.id,
                        "topic": q.topic,
                        "difficulty": q.difficulty,
                        "score": q.score,
                        "accuracy": q.accuracy,
                        "time_taken": q.time_taken,
                        "completed_at": q.completed_at.isoformat()
                    }
                    for q in history
                ]
            }
        else:  # CSV format
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Topic', 'Difficulty', 'Score', 'Accuracy', 'Time Taken', 'Completed At'])
            
            for quiz in history:
                writer.writerow([
                    quiz.id,
                    quiz.topic,
                    quiz.difficulty,
                    quiz.score,
                    quiz.accuracy,
                    quiz.time_taken,
                    quiz.completed_at.isoformat()
                ])
            
            return {
                "csv_data": output.getvalue(),
                "filename": f"quiz_history_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.csv"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export history: {str(e)}") 