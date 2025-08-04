from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, timedelta
import uuid
import statistics
from app.models.flashcards import (
    Flashcard, FlashcardReview, FlashcardDeck, StudySession,
    FlashcardStatus, FlashcardDifficulty
)
from app.models.quiz import Question, Quiz
from app.models.user import User
from app.schemas.flashcards import (
    FlashcardCreate, FlashcardUpdate, FlashcardReviewCreate,
    FlashcardDeckCreate, StudySessionCreate, StudySessionUpdate,
    StudySessionResponse, StudyProgress, SpacedRepetitionSettings,
    SpacedRepetitionResult, FlashcardStats, DeckStats
)

class FlashcardService:
    
    @staticmethod
    async def create_flashcard_from_question(
        db: Session, 
        user_id: int, 
        question_id: int,
        front_content: Optional[str] = None,
        back_content: Optional[str] = None,
        hint: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Flashcard:
        """Create a flashcard from an existing quiz question"""
        
        # Get the question
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise ValueError("Question not found")
        
        # Check if flashcard already exists
        existing = db.query(Flashcard).filter(
            and_(Flashcard.user_id == user_id, Flashcard.question_id == question_id)
        ).first()
        
        if existing:
            return existing
        
        # Create flashcard content
        if not front_content:
            front_content = question.question_text
        
        if not back_content:
            back_content = f"Answer: {question.correct_answer}\n\nExplanation: {question.explanation}"
        
        if not tags:
            tags = []
        
        # Create flashcard
        flashcard = Flashcard(
            user_id=user_id,
            question_id=question_id,
            front_content=front_content,
            back_content=back_content,
            hint=hint,
            tags=tags,
            status=FlashcardStatus.NEW
        )
        
        db.add(flashcard)
        db.commit()
        db.refresh(flashcard)
        
        return flashcard
    
    @staticmethod
    async def create_flashcard_deck(
        db: Session,
        user_id: int,
        deck_data: FlashcardDeckCreate
    ) -> FlashcardDeck:
        """Create a new flashcard deck"""
        
        deck = FlashcardDeck(
            user_id=user_id,
            **deck_data.dict()
        )
        
        db.add(deck)
        db.commit()
        db.refresh(deck)
        
        return deck
    
    @staticmethod
    async def add_questions_to_deck(
        db: Session,
        user_id: int,
        deck_id: int,
        question_ids: List[int]
    ) -> List[Flashcard]:
        """Add questions to a deck as flashcards"""
        
        deck = db.query(FlashcardDeck).filter(
            and_(FlashcardDeck.id == deck_id, FlashcardDeck.user_id == user_id)
        ).first()
        
        if not deck:
            raise ValueError("Deck not found")
        
        flashcards = []
        for question_id in question_ids:
            flashcard = await FlashcardService.create_flashcard_from_question(
                db, user_id, question_id
            )
            flashcards.append(flashcard)
        
        # Update deck statistics
        deck.total_cards = len(flashcards)
        deck.learning_cards = len(flashcards)
        db.commit()
        
        return flashcards
    
    @staticmethod
    async def start_study_session(
        db: Session,
        user_id: int,
        session_data: StudySessionCreate
    ) -> StudySessionResponse:
        """Start a new study session"""
        
        session_id = str(uuid.uuid4())
        
        # Create study session
        study_session = StudySession(
            user_id=user_id,
            session_type=session_data.session_type,
            deck_id=session_data.deck_id
        )
        
        db.add(study_session)
        db.commit()
        
        # Get cards for study
        if session_data.deck_id:
            # Study specific deck
            cards = await FlashcardService._get_deck_cards_for_study(
                db, user_id, session_data.deck_id
            )
        else:
            # Study all cards
            cards = await FlashcardService._get_all_cards_for_study(db, user_id)
        
        # Prepare study cards
        study_cards = []
        total_new = 0
        total_review = 0
        total_learning = 0
        
        for card in cards:
            is_new = card.status == FlashcardStatus.NEW
            is_learning = card.status == FlashcardStatus.LEARNING
            is_review = card.status == FlashcardStatus.REVIEWING
            
            if is_new:
                total_new += 1
            elif is_learning:
                total_learning += 1
            elif is_review:
                total_review += 1
            
            study_cards.append({
                "flashcard": card,
                "is_new": is_new,
                "is_review": is_review,
                "is_learning": is_learning,
                "interval": card.interval,
                "ease_factor": card.ease_factor
            })
        
        return StudySessionResponse(
            session_id=session_id,
            cards=study_cards,
            total_new=total_new,
            total_review=total_review,
            total_learning=total_learning,
            session_type=session_data.session_type
        )
    
    @staticmethod
    async def review_flashcard(
        db: Session,
        user_id: int,
        flashcard_id: int,
        review_data: FlashcardReviewCreate
    ) -> SpacedRepetitionResult:
        """Review a flashcard and update spaced repetition algorithm"""
        
        flashcard = db.query(Flashcard).filter(
            and_(Flashcard.id == flashcard_id, Flashcard.user_id == user_id)
        ).first()
        
        if not flashcard:
            raise ValueError("Flashcard not found")
        
        # Create review record
        review = FlashcardReview(
            flashcard_id=flashcard_id,
            user_id=user_id,
            **review_data.dict()
        )
        
        db.add(review)
        
        # Update flashcard statistics
        flashcard.review_count += 1
        flashcard.last_reviewed = datetime.now()
        
        if review_data.was_correct:
            flashcard.correct_count += 1
        else:
            flashcard.incorrect_count += 1
        
        # Apply spaced repetition algorithm
        result = await FlashcardService._apply_spaced_repetition(
            flashcard, review_data.difficulty_rating
        )
        
        # Update flashcard with new values
        flashcard.interval = result.new_interval
        flashcard.ease_factor = result.new_ease_factor
        flashcard.next_review = result.next_review
        flashcard.status = result.status
        
        db.commit()
        
        return result
    
    @staticmethod
    async def end_study_session(
        db: Session,
        user_id: int,
        session_id: str,
        session_data: StudySessionUpdate
    ) -> StudySession:
        """End a study session and update statistics"""
        
        study_session = db.query(StudySession).filter(
            and_(StudySession.user_id == user_id, StudySession.id == session_id)
        ).first()
        
        if not study_session:
            raise ValueError("Study session not found")
        
        # Update session data
        for field, value in session_data.dict(exclude_unset=True).items():
            setattr(study_session, field, value)
        
        study_session.end_time = datetime.now()
        
        if study_session.start_time and study_session.end_time:
            duration = (study_session.end_time - study_session.start_time).total_seconds() / 60
            study_session.duration = duration
        
        db.commit()
        db.refresh(study_session)
        
        return study_session
    
    @staticmethod
    async def get_flashcard_stats(db: Session, user_id: int) -> FlashcardStats:
        """Get comprehensive flashcard statistics"""
        
        flashcards = db.query(Flashcard).filter(Flashcard.user_id == user_id).all()
        
        total_cards = len(flashcards)
        new_cards = len([f for f in flashcards if f.status == FlashcardStatus.NEW])
        learning_cards = len([f for f in flashcards if f.status == FlashcardStatus.LEARNING])
        review_cards = len([f for f in flashcards if f.status == FlashcardStatus.REVIEWING])
        mastered_cards = len([f for f in flashcards if f.status == FlashcardStatus.MASTERED])
        
        # Get review statistics
        reviews = db.query(FlashcardReview).filter(FlashcardReview.user_id == user_id).all()
        total_reviews = len(reviews)
        correct_reviews = len([r for r in reviews if r.was_correct])
        accuracy = correct_reviews / total_reviews if total_reviews > 0 else 0
        
        # Calculate average response time
        response_times = [r.response_time for r in reviews if r.response_time]
        average_response_time = statistics.mean(response_times) if response_times else 0
        
        # Calculate cards due today and tomorrow
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        cards_due_today = len([
            f for f in flashcards 
            if f.next_review and f.next_review.date() <= today
        ])
        
        cards_due_tomorrow = len([
            f for f in flashcards 
            if f.next_review and f.next_review.date() == tomorrow
        ])
        
        return FlashcardStats(
            total_cards=total_cards,
            new_cards=new_cards,
            learning_cards=learning_cards,
            review_cards=review_cards,
            mastered_cards=mastered_cards,
            total_reviews=total_reviews,
            correct_reviews=correct_reviews,
            accuracy=accuracy,
            average_response_time=average_response_time,
            cards_due_today=cards_due_today,
            cards_due_tomorrow=cards_due_tomorrow
        )
    
    @staticmethod
    async def get_deck_stats(db: Session, user_id: int, deck_id: int) -> DeckStats:
        """Get statistics for a specific deck"""
        
        deck = db.query(FlashcardDeck).filter(
            and_(FlashcardDeck.id == deck_id, FlashcardDeck.user_id == user_id)
        ).first()
        
        if not deck:
            raise ValueError("Deck not found")
        
        # Get deck flashcards
        deck_flashcards = db.query(Flashcard).join(
            DeckFlashcard, Flashcard.id == DeckFlashcard.flashcard_id
        ).filter(DeckFlashcard.deck_id == deck_id).all()
        
        # Calculate stats
        stats = await FlashcardService._calculate_deck_stats(db, deck_flashcards)
        
        # Get recent performance
        recent_reviews = db.query(FlashcardReview).join(
            Flashcard, FlashcardReview.flashcard_id == Flashcard.id
        ).join(
            DeckFlashcard, Flashcard.id == DeckFlashcard.flashcard_id
        ).filter(
            DeckFlashcard.deck_id == deck_id
        ).order_by(desc(FlashcardReview.reviewed_at)).limit(10).all()
        
        recent_performance = []
        for review in recent_reviews:
            recent_performance.append({
                "date": review.reviewed_at,
                "was_correct": review.was_correct,
                "difficulty": review.difficulty_rating.value,
                "response_time": review.response_time
            })
        
        # Calculate learning curve
        learning_curve = await FlashcardService._calculate_learning_curve(
            db, deck_flashcards
        )
        
        return DeckStats(
            deck=deck,
            stats=stats,
            recent_performance=recent_performance,
            learning_curve=learning_curve
        )
    
    # Helper methods
    @staticmethod
    async def _get_deck_cards_for_study(db: Session, user_id: int, deck_id: int) -> List[Flashcard]:
        """Get cards from a specific deck for study"""
        
        cards = db.query(Flashcard).join(
            DeckFlashcard, Flashcard.id == DeckFlashcard.flashcard_id
        ).filter(
            and_(
                DeckFlashcard.deck_id == deck_id,
                Flashcard.user_id == user_id
            )
        ).all()
        
        # Filter cards that are due for review
        now = datetime.now()
        due_cards = [
            card for card in cards
            if card.next_review is None or card.next_review <= now
        ]
        
        return due_cards
    
    @staticmethod
    async def _get_all_cards_for_study(db: Session, user_id: int) -> List[Flashcard]:
        """Get all cards for study"""
        
        cards = db.query(Flashcard).filter(Flashcard.user_id == user_id).all()
        
        # Filter cards that are due for review
        now = datetime.now()
        due_cards = [
            card for card in cards
            if card.next_review is None or card.next_review <= now
        ]
        
        return due_cards
    
    @staticmethod
    async def _apply_spaced_repetition(
        flashcard: Flashcard,
        difficulty_rating: FlashcardDifficulty
    ) -> SpacedRepetitionResult:
        """Apply spaced repetition algorithm (SuperMemo 2)"""
        
        settings = SpacedRepetitionSettings()
        
        if difficulty_rating == FlashcardDifficulty.AGAIN:
            # Reset to learning phase
            new_interval = 0
            new_ease_factor = max(
                settings.minimum_ease_factor,
                flashcard.ease_factor - 0.2
            )
            status = FlashcardStatus.LEARNING
            
        elif difficulty_rating == FlashcardDifficulty.HARD:
            # Reduce interval and ease factor
            new_interval = max(1, int(flashcard.interval * 0.8))
            new_ease_factor = max(
                settings.minimum_ease_factor,
                flashcard.ease_factor - 0.15
            )
            status = FlashcardStatus.REVIEWING
            
        elif difficulty_rating == FlashcardDifficulty.GOOD:
            # Standard interval increase
            if flashcard.interval == 0:
                new_interval = 1
            else:
                new_interval = int(flashcard.interval * flashcard.ease_factor)
            
            new_ease_factor = flashcard.ease_factor
            status = FlashcardStatus.REVIEWING
            
        else:  # EASY
            # Larger interval increase and ease factor bonus
            if flashcard.interval == 0:
                new_interval = 4
            else:
                new_interval = int(flashcard.interval * flashcard.ease_factor * 1.3)
            
            new_ease_factor = min(
                5.0,
                flashcard.ease_factor + settings.ease_bonus
            )
            status = FlashcardStatus.REVIEWING
        
        # Cap interval at maximum
        new_interval = min(new_interval, settings.maximum_interval)
        
        # Calculate next review date
        next_review = datetime.now() + timedelta(days=new_interval)
        
        # Update status based on interval
        if new_interval >= 30:  # Consider mastered after 30 days
            status = FlashcardStatus.MASTERED
        
        return SpacedRepetitionResult(
            new_interval=new_interval,
            new_ease_factor=new_ease_factor,
            next_review=next_review,
            status=status
        )
    
    @staticmethod
    async def _calculate_deck_stats(db: Session, flashcards: List[Flashcard]) -> FlashcardStats:
        """Calculate statistics for a deck"""
        
        total_cards = len(flashcards)
        new_cards = len([f for f in flashcards if f.status == FlashcardStatus.NEW])
        learning_cards = len([f for f in flashcards if f.status == FlashcardStatus.LEARNING])
        review_cards = len([f for f in flashcards if f.status == FlashcardStatus.REVIEWING])
        mastered_cards = len([f for f in flashcards if f.status == FlashcardStatus.MASTERED])
        
        # Get reviews for these flashcards
        flashcard_ids = [f.id for f in flashcards]
        reviews = db.query(FlashcardReview).filter(
            FlashcardReview.flashcard_id.in_(flashcard_ids)
        ).all()
        
        total_reviews = len(reviews)
        correct_reviews = len([r for r in reviews if r.was_correct])
        accuracy = correct_reviews / total_reviews if total_reviews > 0 else 0
        
        response_times = [r.response_time for r in reviews if r.response_time]
        average_response_time = statistics.mean(response_times) if response_times else 0
        
        # Calculate due cards
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        cards_due_today = len([
            f for f in flashcards 
            if f.next_review and f.next_review.date() <= today
        ])
        
        cards_due_tomorrow = len([
            f for f in flashcards 
            if f.next_review and f.next_review.date() == tomorrow
        ])
        
        return FlashcardStats(
            total_cards=total_cards,
            new_cards=new_cards,
            learning_cards=learning_cards,
            review_cards=review_cards,
            mastered_cards=mastered_cards,
            total_reviews=total_reviews,
            correct_reviews=correct_reviews,
            accuracy=accuracy,
            average_response_time=average_response_time,
            cards_due_today=cards_due_today,
            cards_due_tomorrow=cards_due_tomorrow
        )
    
    @staticmethod
    async def _calculate_learning_curve(db: Session, flashcards: List[Flashcard]) -> List[Dict[str, Any]]:
        """Calculate learning curve data"""
        
        flashcard_ids = [f.id for f in flashcards]
        reviews = db.query(FlashcardReview).filter(
            FlashcardReview.flashcard_id.in_(flashcard_ids)
        ).order_by(FlashcardReview.reviewed_at).all()
        
        # Group reviews by date
        daily_performance = {}
        for review in reviews:
            date = review.reviewed_at.date()
            if date not in daily_performance:
                daily_performance[date] = {"correct": 0, "total": 0}
            
            daily_performance[date]["total"] += 1
            if review.was_correct:
                daily_performance[date]["correct"] += 1
        
        # Convert to list format
        learning_curve = []
        for date, performance in sorted(daily_performance.items()):
            accuracy = performance["correct"] / performance["total"]
            learning_curve.append({
                "date": date.isoformat(),
                "accuracy": accuracy,
                "total_reviews": performance["total"]
            })
        
        return learning_curve 