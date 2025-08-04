from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
# Conditional import for PDF export service
try:
    from app.services.pdf_export_service import PDFExportService
    PDF_EXPORT_AVAILABLE = True
except ImportError:
    PDF_EXPORT_AVAILABLE = False
    PDFExportService = None

router = APIRouter()

@router.get("/student/{user_id}")
async def export_student_report(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Export a comprehensive student performance report as PDF"""
    if not PDF_EXPORT_AVAILABLE:
        raise HTTPException(status_code=503, detail="PDF export service is not available")
    
    try:
        # Check if current user is educator or the student themselves
        if current_user.id != user_id:
            # TODO: Add educator role check here
            # For now, allow any authenticated user to export reports
            pass
        
        pdf_data = await PDFExportService.generate_student_report(
            db, user_id, start_date, end_date
        )
        
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=student_report_{user_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate student report: {str(e)}")

@router.post("/class")
async def export_class_report(
    user_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Export a class-wide performance report as PDF"""
    if not PDF_EXPORT_AVAILABLE:
        raise HTTPException(status_code=503, detail="PDF export service is not available")
    
    try:
        # TODO: Add educator role check here
        # For now, allow any authenticated user to export class reports
        
        pdf_data = await PDFExportService.generate_class_report(
            db, user_ids, start_date, end_date
        )
        
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=class_report_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate class report: {str(e)}")

@router.get("/quiz/{quiz_id}")
async def export_quiz_analysis(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export detailed analysis of a specific quiz as PDF"""
    try:
        # TODO: Add educator role check here
        # For now, allow any authenticated user to export quiz reports
        
        pdf_data = await PDFExportService.generate_quiz_analysis_report(db, quiz_id)
        
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=quiz_analysis_{quiz_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz analysis: {str(e)}")

@router.get("/analytics/summary")
async def export_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Export analytics summary as PDF"""
    try:
        # Generate analytics summary for current user
        pdf_data = await PDFExportService.generate_student_report(
            db, current_user.id, start_date, end_date
        )
        
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=analytics_summary_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics summary: {str(e)}")

@router.get("/flashcards/{deck_id}")
async def export_flashcard_deck(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export flashcard deck as PDF"""
    try:
        # TODO: Implement flashcard deck PDF export
        # This would generate a PDF with all cards in the deck
        
        # Placeholder response
        return {"message": "Flashcard deck export not yet implemented"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export flashcard deck: {str(e)}")

@router.get("/progress/timeline")
async def export_progress_timeline(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=7, le=365)
):
    """Export progress timeline as PDF"""
    try:
        # TODO: Implement progress timeline PDF export
        # This would show learning progress over time with charts
        
        # Placeholder response
        return {"message": "Progress timeline export not yet implemented"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export progress timeline: {str(e)}")

@router.get("/certificate/{achievement_id}")
async def export_achievement_certificate(
    achievement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export achievement certificate as PDF"""
    try:
        # TODO: Implement achievement certificate PDF export
        # This would generate a certificate for completing milestones
        
        # Placeholder response
        return {"message": "Achievement certificate export not yet implemented"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export certificate: {str(e)}") 