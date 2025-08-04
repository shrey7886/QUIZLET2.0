from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.flashcard_service import FlashcardService
from app.schemas.flashcards import (
    FlashcardCreate, FlashcardUpdate, Flashcard, FlashcardReviewCreate,
    FlashcardDeckCreate, FlashcardDeckUpdate, FlashcardDeck,
    StudySessionCreate, StudySessionResponse, StudyProgress,
    FlashcardStats, DeckStats, FlashcardSearch, FlashcardSearchResult,
    StudySessionUpdate
)

router = APIRouter()

# Flashcard Management
@router.post("/", response_model=Flashcard)
async def create_flashcard(
    flashcard_data: FlashcardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new flashcard"""
    try:
        flashcard = await FlashcardService.create_flashcard_from_question(
            db, current_user.id, flashcard_data.question_id,
            flashcard_data.front_content, flashcard_data.back_content,
            flashcard_data.hint, flashcard_data.tags
        )
        return flashcard
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Flashcard])
async def get_flashcards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get user's flashcards with optional filtering"""
    try:
        query = db.query(Flashcard).filter(Flashcard.user_id == current_user.id)
        
        if status:
            query = query.filter(Flashcard.status == status)
        
        if tags:
            # Filter by tags (simplified - could be improved with JSON operations)
            for tag in tags:
                query = query.filter(Flashcard.tags.contains([tag]))
        
        flashcards = query.offset(offset).limit(limit).all()
        return flashcards
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load flashcards: {str(e)}")

@router.get("/{flashcard_id}", response_model=Flashcard)
async def get_flashcard(
    flashcard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific flashcard"""
    try:
        flashcard = db.query(Flashcard).filter(
            and_(Flashcard.id == flashcard_id, Flashcard.user_id == current_user.id)
        ).first()
        
        if not flashcard:
            raise HTTPException(status_code=404, detail="Flashcard not found")
        
        return flashcard
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load flashcard: {str(e)}")

@router.put("/{flashcard_id}", response_model=Flashcard)
async def update_flashcard(
    flashcard_id: int,
    flashcard_data: FlashcardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a flashcard"""
    try:
        flashcard = db.query(Flashcard).filter(
            and_(Flashcard.id == flashcard_id, Flashcard.user_id == current_user.id)
        ).first()
        
        if not flashcard:
            raise HTTPException(status_code=404, detail="Flashcard not found")
        
        for field, value in flashcard_data.dict(exclude_unset=True).items():
            setattr(flashcard, field, value)
        
        db.commit()
        db.refresh(flashcard)
        return flashcard
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update flashcard: {str(e)}")

@router.delete("/{flashcard_id}")
async def delete_flashcard(
    flashcard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a flashcard"""
    try:
        flashcard = db.query(Flashcard).filter(
            and_(Flashcard.id == flashcard_id, Flashcard.user_id == current_user.id)
        ).first()
        
        if not flashcard:
            raise HTTPException(status_code=404, detail="Flashcard not found")
        
        db.delete(flashcard)
        db.commit()
        
        return {"message": "Flashcard deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete flashcard: {str(e)}")

# Flashcard Review
@router.post("/{flashcard_id}/review")
async def review_flashcard(
    flashcard_id: int,
    review_data: FlashcardReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Review a flashcard and update spaced repetition algorithm"""
    try:
        result = await FlashcardService.review_flashcard(
            db, current_user.id, flashcard_id, review_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Flashcard Decks
@router.post("/decks", response_model=FlashcardDeck)
async def create_deck(
    deck_data: FlashcardDeckCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new flashcard deck"""
    try:
        deck = await FlashcardService.create_flashcard_deck(db, current_user.id, deck_data)
        return deck
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/decks", response_model=List[FlashcardDeck])
async def get_decks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's flashcard decks"""
    try:
        decks = db.query(FlashcardDeck).filter(FlashcardDeck.user_id == current_user.id).all()
        return decks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load decks: {str(e)}")

@router.get("/decks/{deck_id}", response_model=FlashcardDeck)
async def get_deck(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific deck"""
    try:
        deck = db.query(FlashcardDeck).filter(
            and_(FlashcardDeck.id == deck_id, FlashcardDeck.user_id == current_user.id)
        ).first()
        
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        
        return deck
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load deck: {str(e)}")

@router.put("/decks/{deck_id}", response_model=FlashcardDeck)
async def update_deck(
    deck_id: int,
    deck_data: FlashcardDeckUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a deck"""
    try:
        deck = db.query(FlashcardDeck).filter(
            and_(FlashcardDeck.id == deck_id, FlashcardDeck.user_id == current_user.id)
        ).first()
        
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        
        for field, value in deck_data.dict(exclude_unset=True).items():
            setattr(deck, field, value)
        
        db.commit()
        db.refresh(deck)
        return deck
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update deck: {str(e)}")

@router.delete("/decks/{deck_id}")
async def delete_deck(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a deck"""
    try:
        deck = db.query(FlashcardDeck).filter(
            and_(FlashcardDeck.id == deck_id, FlashcardDeck.user_id == current_user.id)
        ).first()
        
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        
        db.delete(deck)
        db.commit()
        
        return {"message": "Deck deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete deck: {str(e)}")

@router.post("/decks/{deck_id}/add-questions")
async def add_questions_to_deck(
    deck_id: int,
    question_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add questions to a deck as flashcards"""
    try:
        flashcards = await FlashcardService.add_questions_to_deck(
            db, current_user.id, deck_id, question_ids
        )
        return {"message": f"Added {len(flashcards)} flashcards to deck", "flashcards": flashcards}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Study Sessions
@router.post("/study/start", response_model=StudySessionResponse)
async def start_study_session(
    session_data: StudySessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new study session"""
    try:
        response = await FlashcardService.start_study_session(db, current_user.id, session_data)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/study/{session_id}/end")
async def end_study_session(
    session_id: str,
    session_data: StudySessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """End a study session"""
    try:
        session = await FlashcardService.end_study_session(db, current_user.id, session_id, session_data)
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Statistics
@router.get("/stats", response_model=FlashcardStats)
async def get_flashcard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get flashcard statistics"""
    try:
        stats = await FlashcardService.get_flashcard_stats(db, current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load stats: {str(e)}")

@router.get("/decks/{deck_id}/stats", response_model=DeckStats)
async def get_deck_stats(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for a specific deck"""
    try:
        stats = await FlashcardService.get_deck_stats(db, current_user.id, deck_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load deck stats: {str(e)}")

# Search
@router.post("/search", response_model=FlashcardSearchResult)
async def search_flashcards(
    search_data: FlashcardSearch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search flashcards"""
    try:
        query = db.query(Flashcard).filter(Flashcard.user_id == current_user.id)
        
        if search_data.query:
            query = query.filter(
                or_(
                    Flashcard.front_content.ilike(f"%{search_data.query}%"),
                    Flashcard.back_content.ilike(f"%{search_data.query}%")
                )
            )
        
        if search_data.tags:
            for tag in search_data.tags:
                query = query.filter(Flashcard.tags.contains([tag]))
        
        if search_data.status:
            query = query.filter(Flashcard.status == search_data.status)
        
        if search_data.difficulty_min:
            query = query.filter(Flashcard.difficulty_level >= search_data.difficulty_min)
        
        if search_data.difficulty_max:
            query = query.filter(Flashcard.difficulty_level <= search_data.difficulty_max)
        
        if search_data.due_before:
            query = query.filter(Flashcard.next_review <= search_data.due_before)
        
        total_count = query.count()
        flashcards = query.offset(search_data.offset).limit(search_data.limit).all()
        has_more = total_count > search_data.offset + search_data.limit
        
        return FlashcardSearchResult(
            flashcards=flashcards,
            total_count=total_count,
            has_more=has_more
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Due Cards
@router.get("/due", response_model=List[Flashcard])
async def get_due_cards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100)
):
    """Get flashcards due for review"""
    try:
        now = datetime.now()
        due_cards = db.query(Flashcard).filter(
            and_(
                Flashcard.user_id == current_user.id,
                or_(
                    Flashcard.next_review.is_(None),
                    Flashcard.next_review <= now
                )
            )
        ).limit(limit).all()
        
        return due_cards
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load due cards: {str(e)}")

# Import/Export
@router.post("/import")
async def import_flashcards(
    flashcards_data: List[FlashcardCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import flashcards from external source"""
    try:
        imported_flashcards = []
        for flashcard_data in flashcards_data:
            flashcard = await FlashcardService.create_flashcard_from_question(
                db, current_user.id, flashcard_data.question_id,
                flashcard_data.front_content, flashcard_data.back_content,
                flashcard_data.hint, flashcard_data.tags
            )
            imported_flashcards.append(flashcard)
        
        return {"message": f"Imported {len(imported_flashcards)} flashcards", "flashcards": imported_flashcards}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/export")
async def export_flashcards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    format: str = Query("json", regex="^(json|csv)$")
):
    """Export flashcards"""
    try:
        flashcards = db.query(Flashcard).filter(Flashcard.user_id == current_user.id).all()
        
        if format == "csv":
            # Generate CSV format
            csv_data = "Front,Back,Hint,Tags,Status,Next Review\n"
            for flashcard in flashcards:
                csv_data += f'"{flashcard.front_content}","{flashcard.back_content}","{flashcard.hint or ""}","{",".join(flashcard.tags)}","{flashcard.status.value}","{flashcard.next_review or ""}"\n'
            
            return {
                "format": "csv",
                "data": csv_data,
                "filename": f"flashcards_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        else:
            # Return JSON format
            return {
                "format": "json",
                "data": [flashcard.__dict__ for flashcard in flashcards],
                "filename": f"flashcards_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.json"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}") 