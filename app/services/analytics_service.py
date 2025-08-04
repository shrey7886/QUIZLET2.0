from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
import json
import statistics
from app.models.analytics import (
    UserProgress, TopicAnalytics, DifficultyAnalytics, QuizHistory,
    QuestionAnalytics, LearningPath, DifficultyLevel, TopicCategory
)
from app.models.quiz import Quiz, Question, UserAnswer
from app.models.user import User
from app.schemas.analytics import (
    AnalyticsDashboard, AnalyticsSummary, PerformanceTrend,
    WeakAreaAnalysis, LearningRecommendation, QuizHistory as QuizHistorySchema
)

class AnalyticsService:
    
    @staticmethod
    async def update_user_progress(db: Session, user_id: int, quiz_result: Dict[str, Any]):
        """Update user progress after quiz completion"""
        
        # Get or create user progress
        user_progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
        if not user_progress:
            user_progress = UserProgress(user_id=user_id)
            db.add(user_progress)
        
        # Update overall statistics
        user_progress.total_quizzes_taken += 1
        user_progress.total_questions_answered += quiz_result['total_questions']
        user_progress.total_correct_answers += quiz_result['correct_answers']
        user_progress.total_time_spent += quiz_result['time_taken']
        
        # Calculate new averages
        user_progress.average_score = (
            (user_progress.average_score * (user_progress.total_quizzes_taken - 1) + quiz_result['score']) 
            / user_progress.total_quizzes_taken
        )
        user_progress.average_accuracy = (
            (user_progress.average_accuracy * (user_progress.total_quizzes_taken - 1) + quiz_result['accuracy']) 
            / user_progress.total_quizzes_taken
        )
        
        # Update streak
        today = datetime.now().date()
        if user_progress.last_quiz_date:
            last_quiz_date = user_progress.last_quiz_date.date()
            if today - last_quiz_date == timedelta(days=1):
                user_progress.current_streak += 1
            elif today - last_quiz_date > timedelta(days=1):
                user_progress.current_streak = 1
        else:
            user_progress.current_streak = 1
        
        user_progress.longest_streak = max(user_progress.longest_streak, user_progress.current_streak)
        user_progress.last_quiz_date = datetime.now()
        
        # Update topics covered
        if quiz_result['topic'] not in user_progress.topics_covered:
            user_progress.topics_covered.append(quiz_result['topic'])
        
        # Update difficulty progress
        difficulty = quiz_result['difficulty']
        if difficulty not in user_progress.difficulty_progress:
            user_progress.difficulty_progress[difficulty] = 0.0
        
        # Calculate difficulty progress (average score for this difficulty)
        difficulty_quizzes = db.query(Quiz).filter(
            and_(Quiz.user_id == user_id, Quiz.difficulty == difficulty)
        ).all()
        
        if difficulty_quizzes:
            avg_difficulty_score = sum(q.score or 0 for q in difficulty_quizzes) / len(difficulty_quizzes)
            user_progress.difficulty_progress[difficulty] = avg_difficulty_score
        
        db.commit()
        return user_progress
    
    @staticmethod
    async def update_topic_analytics(db: Session, user_id: int, quiz_result: Dict[str, Any]):
        """Update topic-specific analytics"""
        
        topic = quiz_result['topic']
        category = AnalyticsService._categorize_topic(topic)
        
        # Get or create topic analytics
        topic_analytics = db.query(TopicAnalytics).filter(
            and_(TopicAnalytics.user_id == user_id, TopicAnalytics.topic == topic)
        ).first()
        
        if not topic_analytics:
            user_progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
            topic_analytics = TopicAnalytics(
                user_id=user_id,
                user_progress_id=user_progress.id,
                topic=topic,
                category=category
            )
            db.add(topic_analytics)
        
        # Update metrics
        topic_analytics.quizzes_taken += 1
        topic_analytics.questions_answered += quiz_result['total_questions']
        topic_analytics.correct_answers += quiz_result['correct_answers']
        topic_analytics.total_time_spent += quiz_result['time_taken']
        
        # Update scores by difficulty
        difficulty = quiz_result['difficulty']
        if difficulty == 'Easy':
            topic_analytics.easy_score = quiz_result['score']
        elif difficulty == 'Medium':
            topic_analytics.medium_score = quiz_result['score']
        elif difficulty == 'Hard':
            topic_analytics.hard_score = quiz_result['score']
        
        # Calculate improvement rate
        topic_analytics.improvement_rate = AnalyticsService._calculate_improvement_rate(
            db, user_id, topic
        )
        
        topic_analytics.last_quiz_date = datetime.now()
        topic_analytics.best_score = max(topic_analytics.best_score, quiz_result['score'])
        
        # Update average score
        topic_analytics.average_score = (
            (topic_analytics.average_score * (topic_analytics.quizzes_taken - 1) + quiz_result['score']) 
            / topic_analytics.quizzes_taken
        )
        
        # Update weak areas and recommendations
        weak_areas = AnalyticsService._identify_weak_areas(db, user_id, topic)
        topic_analytics.weak_areas = weak_areas
        topic_analytics.recommended_topics = AnalyticsService._get_recommended_topics(weak_areas)
        
        db.commit()
        return topic_analytics
    
    @staticmethod
    async def update_difficulty_analytics(db: Session, user_id: int, quiz_result: Dict[str, Any]):
        """Update difficulty-specific analytics"""
        
        difficulty = DifficultyLevel(quiz_result['difficulty'])
        
        # Get or create difficulty analytics
        difficulty_analytics = db.query(DifficultyAnalytics).filter(
            and_(DifficultyAnalytics.user_id == user_id, DifficultyAnalytics.difficulty == difficulty)
        ).first()
        
        if not difficulty_analytics:
            user_progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
            difficulty_analytics = DifficultyAnalytics(
                user_id=user_id,
                user_progress_id=user_progress.id,
                difficulty=difficulty
            )
            db.add(difficulty_analytics)
        
        # Update metrics
        difficulty_analytics.quizzes_taken += 1
        difficulty_analytics.questions_answered += quiz_result['total_questions']
        difficulty_analytics.correct_answers += quiz_result['correct_answers']
        difficulty_analytics.total_time_spent += quiz_result['time_taken']
        
        # Update scores
        difficulty_analytics.best_score = max(difficulty_analytics.best_score, quiz_result['score'])
        difficulty_analytics.worst_score = min(difficulty_analytics.worst_score, quiz_result['score'])
        
        # Update average score
        difficulty_analytics.average_score = (
            (difficulty_analytics.average_score * (difficulty_analytics.quizzes_taken - 1) + quiz_result['score']) 
            / difficulty_analytics.quizzes_taken
        )
        
        # Update time analysis
        avg_time_per_question = quiz_result['time_taken'] * 60 / quiz_result['total_questions']  # Convert to seconds
        difficulty_analytics.average_time_per_question = (
            (difficulty_analytics.average_time_per_question * (difficulty_analytics.quizzes_taken - 1) + avg_time_per_question) 
            / difficulty_analytics.quizzes_taken
        )
        
        # Update completion times
        if difficulty_analytics.fastest_completion == 0 or quiz_result['time_taken'] < difficulty_analytics.fastest_completion:
            difficulty_analytics.fastest_completion = quiz_result['time_taken']
        
        if quiz_result['time_taken'] > difficulty_analytics.slowest_completion:
            difficulty_analytics.slowest_completion = quiz_result['time_taken']
        
        # Update improvement trend
        trend_data = {
            'date': datetime.now().isoformat(),
            'score': quiz_result['score'],
            'time_taken': quiz_result['time_taken']
        }
        difficulty_analytics.improvement_trend.append(trend_data)
        
        # Calculate readiness score for next difficulty
        difficulty_analytics.readiness_score = AnalyticsService._calculate_readiness_score(
            difficulty_analytics.average_score,
            difficulty_analytics.average_time_per_question,
            difficulty_analytics.quizzes_taken
        )
        
        db.commit()
        return difficulty_analytics
    
    @staticmethod
    async def create_quiz_history(db: Session, user_id: int, quiz_id: int, quiz_result: Dict[str, Any]):
        """Create detailed quiz history entry"""
        
        # Get quiz details
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        
        # Create question breakdown
        question_breakdown = []
        user_answers = db.query(UserAnswer).filter(
            and_(UserAnswer.user_id == user_id, UserAnswer.quiz_id == quiz_id)
        ).all()
        
        for user_answer in user_answers:
            question = db.query(Question).filter(Question.id == user_answer.question_id).first()
            question_breakdown.append({
                'question_id': question.id,
                'question_text': question.question_text,
                'user_answer': user_answer.selected_answer,
                'correct_answer': question.correct_answer,
                'is_correct': user_answer.is_correct,
                'time_taken': user_answer.time_taken or 0
            })
        
        # Analyze performance
        weak_areas = AnalyticsService._identify_weak_areas_from_breakdown(question_breakdown)
        strengths = AnalyticsService._identify_strengths_from_breakdown(question_breakdown)
        
        # Calculate time metrics
        times = [q['time_taken'] for q in question_breakdown]
        avg_time_per_question = statistics.mean(times) if times else 0
        questions_answered_quickly = len([t for t in times if t < 30])
        questions_answered_slowly = len([t for t in times if t > 120])
        
        # Determine next recommended difficulty
        next_difficulty = AnalyticsService._recommend_next_difficulty(
            quiz_result['difficulty'], quiz_result['score'], quiz_result['accuracy']
        )
        
        # Create quiz history entry
        quiz_history = QuizHistory(
            user_id=user_id,
            quiz_id=quiz_id,
            topic=quiz_result['topic'],
            difficulty=DifficultyLevel(quiz_result['difficulty']),
            num_questions=quiz_result['total_questions'],
            time_limit=quiz_result['time_limit'],
            score=quiz_result['score'],
            accuracy=quiz_result['accuracy'],
            correct_answers=quiz_result['correct_answers'],
            total_questions=quiz_result['total_questions'],
            time_taken=quiz_result['time_taken'],
            question_breakdown=question_breakdown,
            weak_areas_identified=weak_areas,
            strengths_identified=strengths,
            average_time_per_question=avg_time_per_question,
            questions_answered_quickly=questions_answered_quickly,
            questions_answered_slowly=questions_answered_slowly,
            difficulty_level=quiz_result['difficulty'],
            next_recommended_difficulty=next_difficulty,
            concepts_mastered=strengths,
            concepts_to_review=weak_areas,
            recommended_next_topics=AnalyticsService._get_recommended_topics(weak_areas)
        )
        
        db.add(quiz_history)
        db.commit()
        return quiz_history
    
    @staticmethod
    async def get_analytics_dashboard(db: Session, user_id: int) -> AnalyticsDashboard:
        """Get comprehensive analytics dashboard for user"""
        
        # Get user progress
        user_progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
        if not user_progress:
            return AnalyticsDashboard(
                summary=AnalyticsSummary(
                    overall_progress=UserProgress(user_id=user_id),
                    topic_performance=[],
                    difficulty_performance=[],
                    recent_quizzes=[],
                    weak_areas=[],
                    strengths=[],
                    recommended_actions=[],
                    learning_insights={}
                ),
                performance_trends=[],
                weak_areas=[],
                recommendations=[],
                quiz_history=[],
                learning_paths=[]
            )
        
        # Get topic performance
        topic_performance = db.query(TopicAnalytics).filter(
            TopicAnalytics.user_id == user_id
        ).all()
        
        # Get difficulty performance
        difficulty_performance = db.query(DifficultyAnalytics).filter(
            DifficultyAnalytics.user_id == user_id
        ).all()
        
        # Get recent quizzes
        recent_quizzes = db.query(QuizHistory).filter(
            QuizHistory.user_id == user_id
        ).order_by(desc(QuizHistory.completed_at)).limit(10).all()
        
        # Get performance trends
        performance_trends = AnalyticsService._get_performance_trends(db, user_id)
        
        # Get weak areas analysis
        weak_areas = AnalyticsService._get_weak_areas_analysis(db, user_id)
        
        # Get learning recommendations
        recommendations = AnalyticsService._get_learning_recommendations(
            user_progress, topic_performance, difficulty_performance, weak_areas
        )
        
        # Get quiz history
        quiz_history = db.query(QuizHistory).filter(
            QuizHistory.user_id == user_id
        ).order_by(desc(QuizHistory.completed_at)).all()
        
        # Get learning paths
        learning_paths = db.query(LearningPath).filter(
            and_(LearningPath.user_id == user_id, LearningPath.is_active == True)
        ).all()
        
        # Generate insights
        learning_insights = AnalyticsService._generate_learning_insights(
            user_progress, topic_performance, difficulty_performance, recent_quizzes
        )
        
        # Create summary
        summary = AnalyticsSummary(
            overall_progress=user_progress,
            topic_performance=topic_performance,
            difficulty_performance=difficulty_performance,
            recent_quizzes=recent_quizzes,
            weak_areas=[wa.concept for wa in weak_areas],
            strengths=learning_insights.get('strengths', []),
            recommended_actions=learning_insights.get('recommended_actions', []),
            learning_insights=learning_insights
        )
        
        return AnalyticsDashboard(
            summary=summary,
            performance_trends=performance_trends,
            weak_areas=weak_areas,
            recommendations=recommendations,
            quiz_history=quiz_history,
            learning_paths=learning_paths
        )
    
    # Helper methods
    @staticmethod
    def _categorize_topic(topic: str) -> TopicCategory:
        """Categorize topic into predefined categories"""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ['python', 'javascript', 'java', 'programming', 'coding', 'algorithm']):
            return TopicCategory.PROGRAMMING
        elif any(word in topic_lower for word in ['math', 'algebra', 'calculus', 'geometry', 'statistics']):
            return TopicCategory.MATHEMATICS
        elif any(word in topic_lower for word in ['physics', 'chemistry', 'biology', 'science']):
            return TopicCategory.SCIENCE
        elif any(word in topic_lower for word in ['history', 'historical', 'ancient', 'medieval']):
            return TopicCategory.HISTORY
        elif any(word in topic_lower for word in ['literature', 'poetry', 'novel', 'writing']):
            return TopicCategory.LITERATURE
        elif any(word in topic_lower for word in ['language', 'english', 'spanish', 'french', 'grammar']):
            return TopicCategory.LANGUAGES
        elif any(word in topic_lower for word in ['business', 'economics', 'finance', 'management']):
            return TopicCategory.BUSINESS
        elif any(word in topic_lower for word in ['technology', 'ai', 'machine learning', 'data science']):
            return TopicCategory.TECHNOLOGY
        else:
            return TopicCategory.OTHER
    
    @staticmethod
    def _calculate_improvement_rate(db: Session, user_id: int, topic: str) -> float:
        """Calculate improvement rate for a topic"""
        topic_quizzes = db.query(QuizHistory).filter(
            and_(QuizHistory.user_id == user_id, QuizHistory.topic == topic)
        ).order_by(QuizHistory.completed_at).all()
        
        if len(topic_quizzes) < 2:
            return 0.0
        
        scores = [q.score for q in topic_quizzes]
        if len(scores) >= 2:
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            
            if first_half and second_half:
                avg_first = statistics.mean(first_half)
                avg_second = statistics.mean(second_half)
                if avg_first > 0:
                    return ((avg_second - avg_first) / avg_first) * 100
        
        return 0.0
    
    @staticmethod
    def _identify_weak_areas(db: Session, user_id: int, topic: str) -> List[str]:
        """Identify weak areas for a topic"""
        # This would analyze question patterns and identify concepts user struggles with
        # For now, return a simple list based on low-scoring questions
        weak_areas = []
        
        # Get recent quiz history for this topic
        recent_quizzes = db.query(QuizHistory).filter(
            and_(QuizHistory.user_id == user_id, QuizHistory.topic == topic)
        ).order_by(desc(QuizHistory.completed_at)).limit(5).all()
        
        for quiz in recent_quizzes:
            if quiz.score < 70:  # Low score threshold
                weak_areas.extend(quiz.weak_areas_identified)
        
        return list(set(weak_areas))  # Remove duplicates
    
    @staticmethod
    def _get_recommended_topics(weak_areas: List[str]) -> List[str]:
        """Get recommended topics based on weak areas"""
        # This would use a more sophisticated algorithm to recommend related topics
        # For now, return some basic recommendations
        recommendations = []
        
        for area in weak_areas:
            if 'variable' in area.lower():
                recommendations.extend(['Data Types', 'Scope', 'Memory Management'])
            elif 'function' in area.lower():
                recommendations.extend(['Parameters', 'Return Values', 'Recursion'])
            elif 'loop' in area.lower():
                recommendations.extend(['Control Flow', 'Iteration', 'Nested Loops'])
        
        return list(set(recommendations))
    
    @staticmethod
    def _calculate_readiness_score(avg_score: float, avg_time: float, quizzes_taken: int) -> float:
        """Calculate readiness score for next difficulty level"""
        if quizzes_taken < 3:
            return 0.0
        
        # Score component (0-50 points)
        score_component = min(avg_score / 2, 50)
        
        # Time component (0-30 points) - faster is better
        time_component = max(0, 30 - (avg_time / 10))
        
        # Consistency component (0-20 points)
        consistency_component = min(quizzes_taken * 2, 20)
        
        return score_component + time_component + consistency_component
    
    @staticmethod
    def _identify_weak_areas_from_breakdown(question_breakdown: List[Dict]) -> List[str]:
        """Identify weak areas from question breakdown"""
        weak_areas = []
        
        for question in question_breakdown:
            if not question['is_correct']:
                # Extract concept from question text (simplified)
                question_text = question['question_text'].lower()
                if 'variable' in question_text:
                    weak_areas.append('Variables')
                elif 'function' in question_text:
                    weak_areas.append('Functions')
                elif 'loop' in question_text:
                    weak_areas.append('Loops')
                elif 'array' in question_text:
                    weak_areas.append('Arrays')
                else:
                    weak_areas.append('General Concepts')
        
        return list(set(weak_areas))
    
    @staticmethod
    def _identify_strengths_from_breakdown(question_breakdown: List[Dict]) -> List[str]:
        """Identify strengths from question breakdown"""
        strengths = []
        
        for question in question_breakdown:
            if question['is_correct']:
                question_text = question['question_text'].lower()
                if 'variable' in question_text:
                    strengths.append('Variables')
                elif 'function' in question_text:
                    strengths.append('Functions')
                elif 'loop' in question_text:
                    strengths.append('Loops')
                elif 'array' in question_text:
                    strengths.append('Arrays')
                else:
                    strengths.append('General Concepts')
        
        return list(set(strengths))
    
    @staticmethod
    def _recommend_next_difficulty(current_difficulty: str, score: float, accuracy: float) -> Optional[str]:
        """Recommend next difficulty level"""
        if current_difficulty == 'Easy' and score >= 80 and accuracy >= 0.8:
            return 'Medium'
        elif current_difficulty == 'Medium' and score >= 85 and accuracy >= 0.85:
            return 'Hard'
        elif current_difficulty == 'Hard' and score < 60:
            return 'Medium'
        
        return None
    
    @staticmethod
    def _get_performance_trends(db: Session, user_id: int) -> List[PerformanceTrend]:
        """Get performance trends over time"""
        recent_quizzes = db.query(QuizHistory).filter(
            QuizHistory.user_id == user_id
        ).order_by(QuizHistory.completed_at).limit(30).all()
        
        trends = []
        for quiz in recent_quizzes:
            trends.append(PerformanceTrend(
                date=quiz.completed_at,
                score=quiz.score,
                accuracy=quiz.accuracy,
                time_taken=quiz.time_taken,
                topic=quiz.topic,
                difficulty=quiz.difficulty.value
            ))
        
        return trends
    
    @staticmethod
    def _get_weak_areas_analysis(db: Session, user_id: int) -> List[WeakAreaAnalysis]:
        """Get detailed weak areas analysis"""
        weak_areas = []
        
        # Get all quiz history for analysis
        quiz_history = db.query(QuizHistory).filter(
            QuizHistory.user_id == user_id
        ).all()
        
        # Analyze weak areas across all quizzes
        concept_errors = {}
        concept_attempts = {}
        
        for quiz in quiz_history:
            for area in quiz.weak_areas_identified:
                if area not in concept_errors:
                    concept_errors[area] = 0
                    concept_attempts[area] = 0
                
                concept_errors[area] += 1
                concept_attempts[area] += 1
        
        # Create weak area analysis
        for concept, errors in concept_errors.items():
            attempts = concept_attempts[concept]
            error_rate = errors / attempts if attempts > 0 else 0
            
            if error_rate > 0.3:  # Only include areas with >30% error rate
                weak_areas.append(WeakAreaAnalysis(
                    topic='General',  # Could be made more specific
                    concept=concept,
                    error_rate=error_rate,
                    total_attempts=attempts,
                    recommended_resources=AnalyticsService._get_resources_for_concept(concept),
                    practice_questions_needed=max(5, int(attempts * 2))
                ))
        
        return weak_areas
    
    @staticmethod
    def _get_learning_recommendations(
        user_progress: UserProgress,
        topic_performance: List[TopicAnalytics],
        difficulty_performance: List[DifficultyAnalytics],
        weak_areas: List[WeakAreaAnalysis]
    ) -> List[LearningRecommendation]:
        """Get personalized learning recommendations"""
        recommendations = []
        
        # Recommend based on weak areas
        for weak_area in weak_areas[:3]:  # Top 3 weak areas
            recommendations.append(LearningRecommendation(
                type='concept',
                title=f'Improve {weak_area.concept}',
                description=f'Focus on {weak_area.concept} with {weak_area.practice_questions_needed} practice questions',
                priority=5,
                estimated_time=weak_area.practice_questions_needed * 2,  # 2 minutes per question
                prerequisites=[],
                resources=weak_area.recommended_resources
            ))
        
        # Recommend next difficulty level
        for diff_analytics in difficulty_performance:
            if diff_analytics.readiness_score >= 70:
                next_difficulty = AnalyticsService._get_next_difficulty(diff_analytics.difficulty.value)
                if next_difficulty:
                    recommendations.append(LearningRecommendation(
                        type='difficulty',
                        title=f'Try {next_difficulty} Difficulty',
                        description=f'You\'re ready for {next_difficulty} level questions',
                        priority=4,
                        estimated_time=30,
                        prerequisites=[],
                        resources=[]
                    ))
        
        # Recommend new topics
        if len(user_progress.topics_covered) < 5:
            new_topics = ['Data Structures', 'Algorithms', 'Object-Oriented Programming', 'Database Design']
            for topic in new_topics:
                if topic not in user_progress.topics_covered:
                    recommendations.append(LearningRecommendation(
                        type='topic',
                        title=f'Explore {topic}',
                        description=f'Start learning about {topic}',
                        priority=3,
                        estimated_time=60,
                        prerequisites=[],
                        resources=[]
                    ))
                    break
        
        return recommendations
    
    @staticmethod
    def _generate_learning_insights(
        user_progress: UserProgress,
        topic_performance: List[TopicAnalytics],
        difficulty_performance: List[DifficultyAnalytics],
        recent_quizzes: List[QuizHistory]
    ) -> Dict[str, Any]:
        """Generate learning insights"""
        insights = {
            'strengths': [],
            'recommended_actions': [],
            'learning_style': 'balanced',
            'consistency_score': 0.0,
            'improvement_rate': 0.0
        }
        
        # Identify strengths
        for topic in topic_performance:
            if topic.average_score >= 80:
                insights['strengths'].append(topic.topic)
        
        # Calculate consistency score
        if recent_quizzes:
            scores = [q.score for q in recent_quizzes]
            insights['consistency_score'] = 100 - statistics.stdev(scores) if len(scores) > 1 else 100
        
        # Calculate improvement rate
        if len(recent_quizzes) >= 2:
            first_half = recent_quizzes[:len(recent_quizzes)//2]
            second_half = recent_quizzes[len(recent_quizzes)//2:]
            
            if first_half and second_half:
                avg_first = statistics.mean([q.score for q in first_half])
                avg_second = statistics.mean([q.score for q in second_half])
                if avg_first > 0:
                    insights['improvement_rate'] = ((avg_second - avg_first) / avg_first) * 100
        
        # Determine learning style
        if user_progress.average_time_spent > 20:  # More than 20 minutes average
            insights['learning_style'] = 'thorough'
        elif user_progress.average_time_spent < 10:  # Less than 10 minutes average
            insights['learning_style'] = 'quick'
        
        # Generate recommended actions
        if insights['consistency_score'] < 70:
            insights['recommended_actions'].append('Focus on consistency - try to maintain steady performance')
        
        if insights['improvement_rate'] < 5:
            insights['recommended_actions'].append('Review weak areas and practice more challenging questions')
        
        if user_progress.current_streak < 3:
            insights['recommended_actions'].append('Build a daily study habit - aim for 3+ day streaks')
        
        return insights
    
    @staticmethod
    def _get_next_difficulty(current: str) -> Optional[str]:
        """Get next difficulty level"""
        difficulties = ['Easy', 'Medium', 'Hard']
        try:
            current_index = difficulties.index(current)
            if current_index < len(difficulties) - 1:
                return difficulties[current_index + 1]
        except ValueError:
            pass
        return None
    
    @staticmethod
    def _get_resources_for_concept(concept: str) -> List[str]:
        """Get recommended resources for a concept"""
        resources = {
            'Variables': ['Variable Declaration Guide', 'Data Types Tutorial', 'Scope Rules'],
            'Functions': ['Function Basics', 'Parameters and Arguments', 'Return Values'],
            'Loops': ['Loop Control Structures', 'Nested Loops', 'Loop Optimization'],
            'Arrays': ['Array Fundamentals', 'Array Methods', 'Multi-dimensional Arrays'],
            'General Concepts': ['Programming Fundamentals', 'Problem Solving', 'Code Review']
        }
        
        return resources.get(concept, ['General Programming Resources']) 