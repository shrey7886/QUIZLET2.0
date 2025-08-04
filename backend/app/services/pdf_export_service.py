from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
import base64

from app.models.quiz import Quiz, Question, UserAnswer
from app.models.user import User
from app.models.analytics import QuizHistory, UserProgress, TopicAnalytics
from app.schemas.analytics import AnalyticsDashboard

class PDFExportService:
    
    @staticmethod
    async def generate_student_report(
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> bytes:
        """Generate a comprehensive student performance report"""
        
        # Get user data
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        )
        
        # Title page
        story.append(Paragraph("Student Performance Report", title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Student: {user.username}", styles['Heading2']))
        story.append(Paragraph(f"Email: {user.email}", styles['Normal']))
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        
        if start_date and end_date:
            story.append(Paragraph(f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}", styles['Normal']))
        
        story.append(PageBreak())
        
        # Get analytics data
        analytics_data = await PDFExportService._get_student_analytics(
            db, user_id, start_date, end_date
        )
        
        # Overall Performance Summary
        story.append(Paragraph("Overall Performance Summary", heading_style))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Quizzes Taken', str(analytics_data['total_quizzes'])],
            ['Average Score', f"{analytics_data['average_score']:.1f}%"],
            ['Total Questions Answered', str(analytics_data['total_questions'])],
            ['Correct Answers', str(analytics_data['correct_answers'])],
            ['Accuracy Rate', f"{analytics_data['accuracy']:.1f}%"],
            ['Total Study Time', f"{analytics_data['total_time']:.1f} minutes"],
            ['Current Streak', str(analytics_data['current_streak'])]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Topic Performance
        story.append(Paragraph("Topic Performance Analysis", heading_style))
        
        if analytics_data['topic_performance']:
            topic_data = [['Topic', 'Quizzes', 'Average Score', 'Improvement']]
            for topic in analytics_data['topic_performance']:
                topic_data.append([
                    topic['topic'],
                    str(topic['quizzes_taken']),
                    f"{topic['average_score']:.1f}%",
                    f"{topic['improvement_rate']:.1f}%"
                ])
            
            topic_table = Table(topic_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1.5*inch])
            topic_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(topic_table)
            story.append(Spacer(1, 20))
        
        # Difficulty Performance
        story.append(Paragraph("Difficulty Level Performance", heading_style))
        
        if analytics_data['difficulty_performance']:
            diff_data = [['Difficulty', 'Quizzes', 'Average Score', 'Readiness']]
            for diff in analytics_data['difficulty_performance']:
                readiness = "Ready" if diff['readiness_score'] >= 70 else "Needs Practice"
                diff_data.append([
                    diff['difficulty'],
                    str(diff['quizzes_taken']),
                    f"{diff['average_score']:.1f}%",
                    readiness
                ])
            
            diff_table = Table(diff_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1.5*inch])
            diff_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(diff_table)
            story.append(Spacer(1, 20))
        
        # Recent Quiz History
        story.append(Paragraph("Recent Quiz History", heading_style))
        
        if analytics_data['recent_quizzes']:
            history_data = [['Date', 'Topic', 'Difficulty', 'Score', 'Time']]
            for quiz in analytics_data['recent_quizzes'][:10]:  # Last 10 quizzes
                history_data.append([
                    quiz['completed_at'].strftime('%m/%d/%Y'),
                    quiz['topic'][:20] + "..." if len(quiz['topic']) > 20 else quiz['topic'],
                    quiz['difficulty'],
                    f"{quiz['score']:.1f}%",
                    f"{quiz['time_taken']:.1f}m"
                ])
            
            history_table = Table(history_data, colWidths=[1*inch, 2*inch, 1*inch, 1*inch, 1*inch])
            history_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(history_table)
            story.append(Spacer(1, 20))
        
        # Weak Areas
        story.append(Paragraph("Areas for Improvement", heading_style))
        
        if analytics_data['weak_areas']:
            weak_areas_text = "The student should focus on improving in the following areas:\n\n"
            for area in analytics_data['weak_areas']:
                weak_areas_text += f"• {area['concept']} (Error rate: {area['error_rate']:.1%})\n"
            
            story.append(Paragraph(weak_areas_text, styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(Paragraph("Learning Recommendations", heading_style))
        
        if analytics_data['recommendations']:
            rec_text = "Based on the student's performance, we recommend:\n\n"
            for rec in analytics_data['recommendations'][:5]:  # Top 5 recommendations
                rec_text += f"• {rec['title']} (Priority: {rec['priority']}/5)\n"
                rec_text += f"  {rec['description']}\n\n"
            
            story.append(Paragraph(rec_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    async def generate_class_report(
        db: Session,
        user_ids: List[int],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> bytes:
        """Generate a class-wide performance report for educators"""
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        )
        
        # Title page
        story.append(Paragraph("Class Performance Report", title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Paragraph(f"Number of Students: {len(user_ids)}", styles['Normal']))
        
        if start_date and end_date:
            story.append(Paragraph(f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}", styles['Normal']))
        
        story.append(PageBreak())
        
        # Get class analytics
        class_data = await PDFExportService._get_class_analytics(
            db, user_ids, start_date, end_date
        )
        
        # Class Summary
        story.append(Paragraph("Class Performance Summary", heading_style))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Students', str(len(user_ids))],
            ['Average Class Score', f"{class_data['average_class_score']:.1f}%"],
            ['Total Quizzes Taken', str(class_data['total_quizzes'])],
            ['Average Quizzes per Student', f"{class_data['avg_quizzes_per_student']:.1f}"],
            ['Class Accuracy Rate', f"{class_data['class_accuracy']:.1f}%"],
            ['Total Study Time', f"{class_data['total_study_time']:.1f} hours"],
            ['Most Active Student', class_data['most_active_student']]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Individual Student Performance
        story.append(Paragraph("Individual Student Performance", heading_style))
        
        if class_data['student_performance']:
            student_data = [['Student', 'Quizzes', 'Avg Score', 'Accuracy', 'Study Time']]
            for student in class_data['student_performance']:
                student_data.append([
                    student['username'],
                    str(student['quizzes_taken']),
                    f"{student['average_score']:.1f}%",
                    f"{student['accuracy']:.1f}%",
                    f"{student['study_time']:.1f}h"
                ])
            
            student_table = Table(student_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            student_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(student_table)
            story.append(Spacer(1, 20))
        
        # Topic Performance Across Class
        story.append(Paragraph("Topic Performance Across Class", heading_style))
        
        if class_data['topic_performance']:
            topic_data = [['Topic', 'Avg Score', 'Students', 'Difficulty']]
            for topic in class_data['topic_performance']:
                difficulty = "Easy" if topic['average_score'] >= 80 else "Medium" if topic['average_score'] >= 60 else "Hard"
                topic_data.append([
                    topic['topic'],
                    f"{topic['average_score']:.1f}%",
                    str(topic['student_count']),
                    difficulty
                ])
            
            topic_table = Table(topic_data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch])
            topic_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(topic_table)
            story.append(Spacer(1, 20))
        
        # Class Insights
        story.append(Paragraph("Class Insights & Recommendations", heading_style))
        
        insights_text = ""
        
        # Performance insights
        if class_data['average_class_score'] < 70:
            insights_text += "• The class average is below 70%, indicating a need for additional support and review.\n"
        elif class_data['average_class_score'] > 85:
            insights_text += "• The class is performing excellently with an average above 85%.\n"
        else:
            insights_text += "• The class is performing well with room for improvement.\n"
        
        # Topic insights
        weak_topics = [t for t in class_data['topic_performance'] if t['average_score'] < 70]
        if weak_topics:
            insights_text += f"• Topics needing attention: {', '.join([t['topic'] for t in weak_topics])}\n"
        
        # Engagement insights
        if class_data['avg_quizzes_per_student'] < 5:
            insights_text += "• Low quiz participation - consider encouraging more practice.\n"
        elif class_data['avg_quizzes_per_student'] > 15:
            insights_text += "• High engagement levels - students are actively practicing.\n"
        
        story.append(Paragraph(insights_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    async def generate_quiz_analysis_report(
        db: Session,
        quiz_id: int
    ) -> bytes:
        """Generate detailed analysis of a specific quiz"""
        
        # Get quiz data
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            raise ValueError("Quiz not found")
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        )
        
        # Title page
        story.append(Paragraph("Quiz Analysis Report", title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Quiz Topic: {quiz.topic}", styles['Heading2']))
        story.append(Paragraph(f"Difficulty: {quiz.difficulty}", styles['Normal']))
        story.append(Paragraph(f"Questions: {quiz.num_questions}", styles['Normal']))
        story.append(Paragraph(f"Time Limit: {quiz.time_limit} minutes", styles['Normal']))
        story.append(Paragraph(f"Created: {quiz.created_at.strftime('%B %d, %Y')}", styles['Normal']))
        
        if quiz.completed_at:
            story.append(Paragraph(f"Completed: {quiz.completed_at.strftime('%B %d, %Y')}", styles['Normal']))
            story.append(Paragraph(f"Score: {quiz.score:.1f}%", styles['Normal']))
            story.append(Paragraph(f"Accuracy: {quiz.accuracy:.1f}%", styles['Normal']))
        
        story.append(PageBreak())
        
        # Get quiz analysis data
        analysis_data = await PDFExportService._get_quiz_analysis(db, quiz_id)
        
        # Quiz Performance Summary
        story.append(Paragraph("Quiz Performance Summary", heading_style))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Attempts', str(analysis_data['total_attempts'])],
            ['Average Score', f"{analysis_data['average_score']:.1f}%"],
            ['Highest Score', f"{analysis_data['highest_score']:.1f}%"],
            ['Lowest Score', f"{analysis_data['lowest_score']:.1f}%"],
            ['Average Time', f"{analysis_data['average_time']:.1f} minutes"],
            ['Completion Rate', f"{analysis_data['completion_rate']:.1f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Question Analysis
        story.append(Paragraph("Question-by-Question Analysis", heading_style))
        
        if analysis_data['question_analysis']:
            q_data = [['Question', 'Correct', 'Incorrect', 'Success Rate']]
            for q in analysis_data['question_analysis']:
                q_data.append([
                    f"Q{q['question_number']}",
                    str(q['correct_answers']),
                    str(q['incorrect_answers']),
                    f"{q['success_rate']:.1f}%"
                ])
            
            q_table = Table(q_data, colWidths=[1*inch, 1*inch, 1*inch, 1.5*inch])
            q_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(q_table)
            story.append(Spacer(1, 20))
        
        # Student Performance
        story.append(Paragraph("Student Performance", heading_style))
        
        if analysis_data['student_performance']:
            s_data = [['Student', 'Score', 'Time', 'Accuracy']]
            for s in analysis_data['student_performance']:
                s_data.append([
                    s['username'],
                    f"{s['score']:.1f}%",
                    f"{s['time_taken']:.1f}m",
                    f"{s['accuracy']:.1f}%"
                ])
            
            s_table = Table(s_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch])
            s_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(s_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    # Helper methods
    @staticmethod
    async def _get_student_analytics(db: Session, user_id: int, start_date: Optional[datetime], end_date: Optional[datetime]) -> Dict[str, Any]:
        """Get comprehensive analytics for a student"""
        
        # Base query
        query = db.query(Quiz).filter(Quiz.user_id == user_id)
        if start_date:
            query = query.filter(Quiz.created_at >= start_date)
        if end_date:
            query = query.filter(Quiz.created_at <= end_date)
        
        quizzes = query.all()
        
        # Calculate basic stats
        total_quizzes = len(quizzes)
        total_questions = sum(q.num_questions for q in quizzes)
        correct_answers = sum(int(q.score * q.num_questions / 100) for q in quizzes if q.score)
        average_score = statistics.mean([q.score for q in quizzes if q.score]) if quizzes else 0
        accuracy = correct_answers / total_questions if total_questions > 0 else 0
        total_time = sum(q.time_limit for q in quizzes)
        
        # Get user progress
        progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
        current_streak = progress.current_streak if progress else 0
        
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
        
        # Get weak areas
        weak_areas = await AnalyticsService._get_weak_areas_analysis(db, user_id)
        
        # Get recommendations
        recommendations = await AnalyticsService._get_learning_recommendations(
            progress, topic_performance, difficulty_performance, weak_areas
        )
        
        return {
            'total_quizzes': total_quizzes,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'average_score': average_score,
            'accuracy': accuracy * 100,
            'total_time': total_time,
            'current_streak': current_streak,
            'topic_performance': [
                {
                    'topic': t.topic,
                    'quizzes_taken': t.quizzes_taken,
                    'average_score': t.average_score,
                    'improvement_rate': t.improvement_rate
                }
                for t in topic_performance
            ],
            'difficulty_performance': [
                {
                    'difficulty': d.difficulty.value,
                    'quizzes_taken': d.quizzes_taken,
                    'average_score': d.average_score,
                    'readiness_score': d.readiness_score
                }
                for d in difficulty_performance
            ],
            'recent_quizzes': recent_quizzes,
            'weak_areas': weak_areas,
            'recommendations': recommendations
        }
    
    @staticmethod
    async def _get_class_analytics(db: Session, user_ids: List[int], start_date: Optional[datetime], end_date: Optional[datetime]) -> Dict[str, Any]:
        """Get analytics for a class of students"""
        
        # Get all quizzes for the class
        query = db.query(Quiz).filter(Quiz.user_id.in_(user_ids))
        if start_date:
            query = query.filter(Quiz.created_at >= start_date)
        if end_date:
            query = query.filter(Quiz.created_at <= end_date)
        
        quizzes = query.all()
        
        # Calculate class stats
        total_quizzes = len(quizzes)
        scores = [q.score for q in quizzes if q.score]
        average_class_score = statistics.mean(scores) if scores else 0
        avg_quizzes_per_student = total_quizzes / len(user_ids) if user_ids else 0
        
        # Calculate accuracy
        total_questions = sum(q.num_questions for q in quizzes)
        correct_answers = sum(int(q.score * q.num_questions / 100) for q in quizzes if q.score)
        class_accuracy = correct_answers / total_questions * 100 if total_questions > 0 else 0
        
        # Calculate study time
        total_study_time = sum(q.time_limit for q in quizzes) / 60  # Convert to hours
        
        # Get most active student
        student_activity = {}
        for quiz in quizzes:
            student_activity[quiz.user_id] = student_activity.get(quiz.user_id, 0) + 1
        
        most_active_user_id = max(student_activity.keys(), key=lambda k: student_activity[k]) if student_activity else None
        most_active_student = "N/A"
        if most_active_user_id:
            user = db.query(User).filter(User.id == most_active_user_id).first()
            most_active_student = user.username if user else "Unknown"
        
        # Get individual student performance
        student_performance = []
        for user_id in user_ids:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user_quizzes = [q for q in quizzes if q.user_id == user_id]
                user_scores = [q.score for q in user_quizzes if q.score]
                user_accuracy = statistics.mean(user_scores) if user_scores else 0
                user_study_time = sum(q.time_limit for q in user_quizzes) / 60
                
                student_performance.append({
                    'username': user.username,
                    'quizzes_taken': len(user_quizzes),
                    'average_score': user_accuracy,
                    'accuracy': user_accuracy,
                    'study_time': user_study_time
                })
        
        # Get topic performance across class
        topic_performance = []
        topics = set(q.topic for q in quizzes)
        for topic in topics:
            topic_quizzes = [q for q in quizzes if q.topic == topic]
            topic_scores = [q.score for q in topic_quizzes if q.score]
            topic_avg_score = statistics.mean(topic_scores) if topic_scores else 0
            topic_students = len(set(q.user_id for q in topic_quizzes))
            
            topic_performance.append({
                'topic': topic,
                'average_score': topic_avg_score,
                'student_count': topic_students
            })
        
        return {
            'average_class_score': average_class_score,
            'total_quizzes': total_quizzes,
            'avg_quizzes_per_student': avg_quizzes_per_student,
            'class_accuracy': class_accuracy,
            'total_study_time': total_study_time,
            'most_active_student': most_active_student,
            'student_performance': student_performance,
            'topic_performance': topic_performance
        }
    
    @staticmethod
    async def _get_quiz_analysis(db: Session, quiz_id: int) -> Dict[str, Any]:
        """Get detailed analysis of a specific quiz"""
        
        # Get quiz attempts
        attempts = db.query(Quiz).filter(Quiz.id == quiz_id).all()
        
        # Calculate basic stats
        total_attempts = len(attempts)
        scores = [a.score for a in attempts if a.score]
        average_score = statistics.mean(scores) if scores else 0
        highest_score = max(scores) if scores else 0
        lowest_score = min(scores) if scores else 0
        
        # Calculate time stats
        times = [a.time_limit for a in attempts]
        average_time = statistics.mean(times) if times else 0
        
        # Calculate completion rate
        completed = len([a for a in attempts if a.completed_at])
        completion_rate = completed / total_attempts * 100 if total_attempts > 0 else 0
        
        # Get question analysis
        questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
        question_analysis = []
        
        for question in questions:
            user_answers = db.query(UserAnswer).filter(UserAnswer.question_id == question.id).all()
            correct_answers = len([ua for ua in user_answers if ua.is_correct])
            incorrect_answers = len([ua for ua in user_answers if not ua.is_correct])
            total_answers = len(user_answers)
            success_rate = correct_answers / total_answers * 100 if total_answers > 0 else 0
            
            question_analysis.append({
                'question_number': question.question_number,
                'correct_answers': correct_answers,
                'incorrect_answers': incorrect_answers,
                'success_rate': success_rate
            })
        
        # Get student performance
        student_performance = []
        for attempt in attempts:
            user = db.query(User).filter(User.id == attempt.user_id).first()
            if user:
                student_performance.append({
                    'username': user.username,
                    'score': attempt.score or 0,
                    'time_taken': attempt.time_limit,
                    'accuracy': attempt.accuracy or 0
                })
        
        return {
            'total_attempts': total_attempts,
            'average_score': average_score,
            'highest_score': highest_score,
            'lowest_score': lowest_score,
            'average_time': average_time,
            'completion_rate': completion_rate,
            'question_analysis': question_analysis,
            'student_performance': student_performance
        } 