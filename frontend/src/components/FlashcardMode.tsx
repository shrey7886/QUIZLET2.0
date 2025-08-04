import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { flashcardAPI } from '../services/api';
import Header from './Header';

interface Flashcard {
  id: number;
  front_content: string;
  back_content: string;
  hint?: string;
  tags: string[];
  status: string;
  difficulty_level: number;
  interval: number;
  ease_factor: number;
  next_review?: string;
}

interface StudySession {
  session_id: string;
  cards: Array<{
    flashcard: Flashcard;
    is_new: boolean;
    is_review: boolean;
    is_learning: boolean;
  }>;
  total_new: number;
  total_review: number;
  total_learning: number;
}

interface StudyProgress {
  session_id: string;
  completed_cards: number;
  total_cards: number;
  correct_answers: number;
  incorrect_answers: number;
  accuracy: number;
  average_response_time: number;
}

const FlashcardMode: React.FC = () => {
  const { user } = useAuth();
  const [studySession, setStudySession] = useState<StudySession | null>(null);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null);
  const [cardStartTime, setCardStartTime] = useState<Date | null>(null);
  const [studyProgress, setStudyProgress] = useState<StudyProgress | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [selectedDeck, setSelectedDeck] = useState<number | null>(null);
  const [decks, setDecks] = useState<any[]>([]);

  useEffect(() => {
    loadDecks();
  }, []);

  const loadDecks = async () => {
    try {
      const response = await flashcardAPI.getDecks();
      setDecks(response.data);
    } catch (err: any) {
      setError('Failed to load flashcard decks');
    }
  };

  const startStudySession = async (deckId?: number) => {
    try {
      setLoading(true);
      setError('');
      
      const sessionData = {
        session_type: 'spaced_repetition',
        deck_id: deckId || null
      };
      
      const response = await flashcardAPI.startStudySession(sessionData);
      setStudySession(response.data);
      setCurrentCardIndex(0);
      setShowAnswer(false);
      setSessionStartTime(new Date());
      setCardStartTime(new Date());
      
      // Initialize progress
      setStudyProgress({
        session_id: response.data.session_id,
        completed_cards: 0,
        total_cards: response.data.cards.length,
        correct_answers: 0,
        incorrect_answers: 0,
        accuracy: 0,
        average_response_time: 0
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start study session');
    } finally {
      setLoading(false);
    }
  };

  const reviewCard = async (difficulty: 'again' | 'hard' | 'good' | 'easy') => {
    if (!studySession || !studyProgress) return;

    const currentCard = studySession.cards[currentCardIndex];
    const responseTime = cardStartTime ? (new Date().getTime() - cardStartTime.getTime()) / 1000 : 0;
    
    try {
      const reviewData = {
        flashcard_id: currentCard.flashcard.id,
        difficulty_rating: difficulty,
        response_time: responseTime,
        was_correct: difficulty === 'good' || difficulty === 'easy',
        confidence_level: difficulty === 'easy' ? 5 : difficulty === 'good' ? 4 : difficulty === 'hard' ? 2 : 1,
        review_session_id: studySession.session_id
      };
      
      await flashcardAPI.reviewFlashcard(currentCard.flashcard.id, reviewData);
      
      // Update progress
      const isCorrect = difficulty === 'good' || difficulty === 'easy';
      const newCorrectAnswers = studyProgress.correct_answers + (isCorrect ? 1 : 0);
      const newIncorrectAnswers = studyProgress.incorrect_answers + (isCorrect ? 0 : 1);
      const newCompletedCards = studyProgress.completed_cards + 1;
      const newAccuracy = (newCorrectAnswers / newCompletedCards) * 100;
      
      setStudyProgress({
        ...studyProgress,
        completed_cards: newCompletedCards,
        correct_answers: newCorrectAnswers,
        incorrect_answers: newIncorrectAnswers,
        accuracy: newAccuracy,
        average_response_time: (studyProgress.average_response_time + responseTime) / 2
      });
      
      // Move to next card
      if (currentCardIndex < studySession.cards.length - 1) {
        setCurrentCardIndex(currentCardIndex + 1);
        setShowAnswer(false);
        setCardStartTime(new Date());
      } else {
        // Session complete
        await endStudySession();
      }
    } catch (err: any) {
      setError('Failed to review card');
    }
  };

  const endStudySession = async () => {
    if (!studySession || !studyProgress) return;

    try {
      const sessionData = {
        end_time: new Date(),
        duration: sessionStartTime ? (new Date().getTime() - sessionStartTime.getTime()) / 60000 : 0,
        total_cards: studyProgress.total_cards,
        correct_cards: studyProgress.correct_answers,
        incorrect_cards: studyProgress.incorrect_answers,
        accuracy: studyProgress.accuracy,
        average_response_time: studyProgress.average_response_time
      };
      
      await flashcardAPI.endStudySession(studySession.session_id, sessionData);
      
      // Reset session
      setStudySession(null);
      setStudyProgress(null);
      setCurrentCardIndex(0);
      setShowAnswer(false);
      setSessionStartTime(null);
      setCardStartTime(null);
    } catch (err: any) {
      setError('Failed to end study session');
    }
  };

  const getCurrentCard = () => {
    if (!studySession || currentCardIndex >= studySession.cards.length) return null;
    return studySession.cards[currentCardIndex];
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'again': return 'bg-red-500 hover:bg-red-600';
      case 'hard': return 'bg-orange-500 hover:bg-orange-600';
      case 'good': return 'bg-green-500 hover:bg-green-600';
      case 'easy': return 'bg-blue-500 hover:bg-blue-600';
      default: return 'bg-gray-500 hover:bg-gray-600';
    }
  };

  const getDifficultyLabel = (difficulty: string) => {
    switch (difficulty) {
      case 'again': return 'Again';
      case 'hard': return 'Hard';
      case 'good': return 'Good';
      case 'easy': return 'Easy';
      default: return difficulty;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <Header />
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="spinner w-12 h-12 mx-auto mb-4"></div>
            <p className="text-slate-600">Loading flashcards...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!studySession) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <Header />
        
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="text-center mb-12 animate-fade-in">
            <h1 className="text-4xl font-bold text-slate-900 mb-4">
              Flashcard Study Mode
            </h1>
            <p className="text-xl text-slate-600">
              Master concepts with spaced repetition learning
            </p>
          </div>

          {error && (
            <div className="card mb-8 bg-red-50 border-red-200">
              <div className="flex items-center space-x-2 text-red-700">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="font-medium">{error}</span>
              </div>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-8">
            {/* Study Options */}
            <div className="card animate-slide-up">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">Start Studying</h2>
              
              <div className="space-y-4">
                <button
                  onClick={() => startStudySession()}
                  className="btn-primary w-full flex items-center justify-center py-4"
                >
                  <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Study All Cards
                </button>
                
                <div className="text-center text-slate-500">or</div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Study Specific Deck
                  </label>
                  <select
                    value={selectedDeck || ''}
                    onChange={(e) => setSelectedDeck(e.target.value ? parseInt(e.target.value) : null)}
                    className="input-field w-full"
                  >
                    <option value="">Select a deck...</option>
                    {decks.map((deck) => (
                      <option key={deck.id} value={deck.id}>
                        {deck.name} ({deck.total_cards} cards)
                      </option>
                    ))}
                  </select>
                  
                  <button
                    onClick={() => selectedDeck && startStudySession(selectedDeck)}
                    disabled={!selectedDeck}
                    className="btn-secondary w-full mt-3 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Study Selected Deck
                  </button>
                </div>
              </div>
            </div>

            {/* Study Info */}
            <div className="card animate-slide-up" style={{ animationDelay: '0.2s' }}>
              <h2 className="text-2xl font-bold text-slate-900 mb-6">How It Works</h2>
              
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-blue-600 font-bold">1</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">Spaced Repetition</h3>
                    <p className="text-sm text-slate-600">Cards are shown at optimal intervals for maximum retention</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-green-600 font-bold">2</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">Rate Your Knowledge</h3>
                    <p className="text-sm text-slate-600">Tell us how well you knew each card to optimize your learning</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-purple-600 font-bold">3</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">Track Progress</h3>
                    <p className="text-sm text-slate-600">Monitor your learning progress and mastery levels</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const currentCard = getCurrentCard();
  if (!currentCard) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <Header />
      
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Bar */}
        {studyProgress && (
          <div className="card mb-8">
            <div className="flex justify-between items-center mb-4">
              <div className="text-sm text-slate-600">
                Progress: {studyProgress.completed_cards} / {studyProgress.total_cards}
              </div>
              <div className="text-sm text-slate-600">
                Accuracy: {studyProgress.accuracy.toFixed(1)}%
              </div>
            </div>
            
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${(studyProgress.completed_cards / studyProgress.total_cards) * 100}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Flashcard */}
        <div className="card mb-8 animate-slide-up">
          <div className="text-center mb-6">
            <div className="flex items-center justify-center space-x-2 text-sm text-slate-500">
              <span className={`badge ${currentCard.is_new ? 'badge-primary' : currentCard.is_learning ? 'badge-warning' : 'badge-success'}`}>
                {currentCard.is_new ? 'New' : currentCard.is_learning ? 'Learning' : 'Review'}
              </span>
              <span>•</span>
              <span>Card {currentCardIndex + 1} of {studySession.cards.length}</span>
            </div>
          </div>

          {/* Card Content */}
          <div className="min-h-[300px] flex items-center justify-center">
            <div className="text-center max-w-2xl">
              {!showAnswer ? (
                <div>
                  <h2 className="text-2xl font-bold text-slate-900 mb-6">
                    {currentCard.flashcard.front_content}
                  </h2>
                  
                  {currentCard.flashcard.hint && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                      <div className="flex items-center space-x-2 text-blue-700">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="font-medium">Hint</span>
                      </div>
                      <p className="text-blue-800 mt-2">{currentCard.flashcard.hint}</p>
                    </div>
                  )}
                  
                  <button
                    onClick={() => setShowAnswer(true)}
                    className="btn-primary px-8 py-3"
                  >
                    Show Answer
                  </button>
                </div>
              ) : (
                <div>
                  <h2 className="text-2xl font-bold text-slate-900 mb-6">
                    {currentCard.flashcard.back_content}
                  </h2>
                  
                  <div className="text-sm text-slate-500 mb-6">
                    How well did you know this?
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {['again', 'hard', 'good', 'easy'].map((difficulty) => (
                      <button
                        key={difficulty}
                        onClick={() => reviewCard(difficulty as any)}
                        className={`${getDifficultyColor(difficulty)} text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-105 active:scale-95`}
                      >
                        {getDifficultyLabel(difficulty)}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Session Controls */}
        <div className="flex justify-center space-x-4">
          <button
            onClick={endStudySession}
            className="btn-secondary px-6 py-2"
          >
            End Session
          </button>
        </div>
      </div>
    </div>
  );
};

export default FlashcardMode; 