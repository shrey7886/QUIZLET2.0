import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { quizAPI } from '../services/api';
import Header from './Header';

interface Question {
  id: number;
  question_text: string;
  options: string[];
  correct_answer: string;
  explanation: string;
  question_number: number;
}

interface Quiz {
  id: number;
  topic: string;
  difficulty: string;
  num_questions: number;
  time_limit: number;
  questions: Question[];
}

const QuizInterface: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<{ [key: number]: string }>({});
  const [timeLeft, setTimeLeft] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [quizStarted, setQuizStarted] = useState(false);
  const [startTime, setStartTime] = useState<Date | null>(null);
  
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Get quiz data from location state or load from API
    if (location.state?.quiz) {
      setQuiz(location.state.quiz);
      setTimeLeft(location.state.quiz.time_limit * 60);
    } else {
      // Redirect to dashboard if no quiz data
      navigate('/dashboard');
    }
  }, [location.state, navigate]);

  useEffect(() => {
    if (quizStarted && timeLeft > 0) {
      timerRef.current = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            // Time's up, auto-submit
            handleSubmitQuiz();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [quizStarted, timeLeft]);

  const startQuiz = () => {
    setQuizStarted(true);
    setStartTime(new Date());
  };

  const handleAnswerSelect = (questionId: number, answer: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleSubmitQuiz = async () => {
    if (!quiz || !startTime) return;

    try {
      setLoading(true);
      
      // Calculate time taken
      const endTime = new Date();
      const timeTaken = (endTime.getTime() - startTime.getTime()) / 60000; // in minutes
      
      // Submit answers
      for (const [questionId, answer] of Object.entries(answers)) {
        await quizAPI.submitAnswer(quiz.id, {
          question_id: parseInt(questionId),
          selected_answer: answer,
          time_taken: timeTaken
        });
      }
      
      // Complete quiz
      const result = await quizAPI.completeQuiz(quiz.id);
      
      // Navigate to results page
      navigate('/results', { 
        state: { 
          quizResult: result.data,
          quiz: quiz,
          answers: answers,
          timeTaken: timeTaken
        } 
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit quiz');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getCurrentQuestion = () => {
    if (!quiz || currentQuestionIndex >= quiz.questions.length) return null;
    return quiz.questions[currentQuestionIndex];
  };

  const goToQuestion = (index: number) => {
    if (index >= 0 && index < (quiz?.questions.length || 0)) {
      setCurrentQuestionIndex(index);
    }
  };

  const isQuestionAnswered = (questionId: number) => {
    return answers[questionId] !== undefined;
  };

  if (!quiz) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <Header />
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="spinner w-12 h-12 mx-auto mb-4"></div>
            <p className="text-slate-600">Loading quiz...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!quizStarted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <Header />
        
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="card text-center animate-fade-in">
            <h1 className="text-3xl font-bold text-slate-900 mb-6">Quiz Ready!</h1>
            
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-slate-800 mb-2">{quiz.topic}</h2>
              <div className="flex items-center justify-center space-x-4 text-slate-600">
                <span className="badge badge-secondary">{quiz.difficulty}</span>
                <span>{quiz.num_questions} questions</span>
                <span>{quiz.time_limit} minutes</span>
              </div>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
              <h3 className="text-lg font-semibold text-blue-900 mb-4">Instructions</h3>
              <ul className="text-left space-y-2 text-blue-800">
                <li>• Read each question carefully before answering</li>
                <li>• You can navigate between questions using the question numbers</li>
                <li>• The timer will automatically submit the quiz when time runs out</li>
                <li>• You can submit early if you finish before the time limit</li>
                <li>• Review your answers before final submission</li>
              </ul>
            </div>
            
            <button
              onClick={startQuiz}
              className="btn-primary px-8 py-4 text-lg"
            >
              Start Quiz
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentQuestion = getCurrentQuestion();
  if (!currentQuestion) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <Header />
      
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quiz Header */}
        <div className="card mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">{quiz.topic}</h1>
              <p className="text-slate-600">Question {currentQuestionIndex + 1} of {quiz.questions.length}</p>
            </div>
            
            <div className="text-right">
              <div className="text-2xl font-bold text-red-600 mb-1">
                {formatTime(timeLeft)}
              </div>
              <div className="text-sm text-slate-500">Time Remaining</div>
            </div>
          </div>
        </div>

        {error && (
          <div className="card mb-6 bg-red-50 border-red-200">
            <div className="flex items-center space-x-2 text-red-700">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-medium">{error}</span>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Question Area */}
          <div className="lg:col-span-3">
            <div className="card">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-slate-900 mb-4">
                  {currentQuestion.question_text}
                </h2>
              </div>
              
              <div className="space-y-3">
                {currentQuestion.options.map((option, index) => (
                  <button
                    key={index}
                    onClick={() => handleAnswerSelect(currentQuestion.id, option)}
                    className={`w-full text-left p-4 rounded-lg border-2 transition-all duration-200 ${
                      answers[currentQuestion.id] === option
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                        answers[currentQuestion.id] === option
                          ? 'border-blue-500 bg-blue-500'
                          : 'border-slate-300'
                      }`}>
                        {answers[currentQuestion.id] === option && (
                          <div className="w-2 h-2 bg-white rounded-full"></div>
                        )}
                      </div>
                      <span className="font-medium text-slate-900">{option}</span>
                    </div>
                  </button>
                ))}
              </div>
              
              <div className="flex justify-between mt-8">
                <button
                  onClick={() => goToQuestion(currentQuestionIndex - 1)}
                  disabled={currentQuestionIndex === 0}
                  className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                
                <button
                  onClick={() => goToQuestion(currentQuestionIndex + 1)}
                  disabled={currentQuestionIndex === quiz.questions.length - 1}
                  className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </div>

          {/* Question Navigator */}
          <div className="lg:col-span-1">
            <div className="card">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Question Navigator</h3>
              
              <div className="grid grid-cols-5 gap-2 mb-6">
                {quiz.questions.map((question, index) => (
                  <button
                    key={question.id}
                    onClick={() => goToQuestion(index)}
                    className={`w-10 h-10 rounded-lg text-sm font-medium transition-all duration-200 ${
                      index === currentQuestionIndex
                        ? 'bg-blue-500 text-white'
                        : isQuestionAnswered(question.id)
                        ? 'bg-green-100 text-green-700 border border-green-300'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {index + 1}
                  </button>
                ))}
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-blue-500 rounded"></div>
                  <span>Current Question</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-green-100 border border-green-300 rounded"></div>
                  <span>Answered</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-slate-100 rounded"></div>
                  <span>Unanswered</span>
                </div>
              </div>
              
              <div className="mt-6 pt-6 border-t border-slate-200">
                <div className="text-sm text-slate-600 mb-2">
                  Progress: {Object.keys(answers).length} / {quiz.questions.length} answered
                </div>
                <div className="progress-bar mb-4">
                  <div
                    className="progress-fill"
                    style={{ width: `${(Object.keys(answers).length / quiz.questions.length) * 100}%` }}
                  ></div>
                </div>
                
                <button
                  onClick={handleSubmitQuiz}
                  disabled={loading}
                  className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <div className="flex items-center justify-center">
                      <div className="spinner w-4 h-4 mr-2"></div>
                      Submitting...
                    </div>
                  ) : (
                    'Submit Quiz'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizInterface; 