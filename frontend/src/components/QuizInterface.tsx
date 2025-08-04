import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

interface Question {
  id: number;
  question: string;
  options: string[];
  correct_answer: number;
  explanation?: string;
}

interface QuizConfig {
  topic: string;
  difficulty: string;
  num_questions: number;
  time_limit?: number;
}

const QuizInterface: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { questions, config } = location.state || { questions: [], config: {} };

  // Redirect if no quiz data
  useEffect(() => {
    if (!questions || questions.length === 0) {
      navigate('/quiz-generator');
    }
  }, [questions, navigate]);

  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const [timeLeft, setTimeLeft] = useState(config.time_limit || 300); // 5 minutes default
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [answers, setAnswers] = useState<(number | null)[]>(new Array(questions.length).fill(null));
  const [score, setScore] = useState(0);
  const [startTime] = useState(Date.now());

  const currentQuestion = questions[currentQuestionIndex];

  useEffect(() => {
    if (timeLeft > 0 && !isAnswered) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && !isAnswered) {
      handleNextQuestion();
    }
  }, [timeLeft, isAnswered]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerSelect = (answerIndex: number) => {
    if (isAnswered) return;
    setSelectedAnswer(answerIndex);
  };

  const handleSubmitAnswer = () => {
    if (selectedAnswer === null) return;
    
    setIsAnswered(true);
    setShowExplanation(true);
    
    const newAnswers = [...answers];
    newAnswers[currentQuestionIndex] = selectedAnswer;
    setAnswers(newAnswers);
    
    if (selectedAnswer === currentQuestion.correct_answer) {
      setScore(score + 1);
    }
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setSelectedAnswer(null);
      setIsAnswered(false);
      setShowExplanation(false);
    } else {
      // Quiz completed
      const timeUsed = Math.floor((Date.now() - startTime) / 1000);
      navigate('/results', { 
        state: { 
          score: Math.round((score / questions.length) * 100), 
          totalQuestions: questions.length,
          correctAnswers: score,
          answers,
          questions,
          config,
          timeUsed
        } 
      });
    }
  };

  const getProgressPercentage = () => {
    return ((currentQuestionIndex + 1) / questions.length) * 100;
  };

  const getTimeColor = () => {
    if (timeLeft > 120) return 'text-green-400';
    if (timeLeft > 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  // Show loading if no questions
  if (!questions || questions.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white">Loading quiz...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Floating Elements */}
        <div className="absolute top-20 left-20 w-2 h-2 bg-blue-400 rounded-full animate-pulse opacity-60"></div>
        <div className="absolute top-40 right-32 w-1 h-1 bg-purple-400 rounded-full animate-bounce opacity-80"></div>
        <div className="absolute bottom-32 left-40 w-3 h-3 bg-pink-400 rounded-full animate-ping opacity-40"></div>
        <div className="absolute bottom-20 right-20 w-2 h-2 bg-cyan-400 rounded-full animate-pulse opacity-70"></div>
        <div className="absolute top-1/2 left-1/4 w-1 h-1 bg-yellow-400 rounded-full animate-bounce opacity-90"></div>
        
        {/* Geometric Shapes */}
        <div className="absolute top-10 right-10 w-20 h-20 border border-white/10 rounded-full animate-spin-slow"></div>
        <div className="absolute bottom-10 left-10 w-16 h-16 border border-purple-400/20 rounded-lg animate-pulse"></div>
        <div className="absolute top-1/3 right-1/4 w-12 h-12 border border-blue-400/30 rotate-45 animate-pulse"></div>
        
        {/* Gradient Orbs */}
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-500/10 to-purple-600/10 rounded-full mix-blend-multiply filter blur-xl animate-float"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-purple-500/10 to-pink-600/10 rounded-full mix-blend-multiply filter blur-xl animate-float" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-40 left-40 w-60 h-60 bg-gradient-to-br from-indigo-500/10 to-blue-600/10 rounded-full mix-blend-multiply filter blur-xl animate-float" style={{ animationDelay: '4s' }}></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 pt-20 pb-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  {config.topic}
                </h1>
                <p className="text-gray-300">
                  Question {currentQuestionIndex + 1} of {questions.length} • {config.difficulty}
                </p>
              </div>
              
              {/* Timer */}
              <div className="text-right">
                <div className={`text-2xl font-bold ${getTimeColor()} mb-1`}>
                  {formatTime(timeLeft)}
                </div>
                <div className="text-sm text-gray-400">Time Remaining</div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-white/10 rounded-full h-2 mb-4">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${getProgressPercentage()}%` }}
              ></div>
            </div>
            
            <div className="flex justify-between text-sm text-gray-400">
              <span>Progress: {currentQuestionIndex + 1}/{questions.length}</span>
              <span>Score: {score}/{questions.length}</span>
            </div>
          </div>

          {/* Question Card */}
          <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-8 mb-8 relative overflow-hidden">
            {/* Question Background Glow */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-600/5 rounded-2xl"></div>
            
            <div className="relative z-10">
              {/* Question Number */}
              <div className="flex items-center mb-6">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm mr-3">
                  {currentQuestionIndex + 1}
                </div>
                <h2 className="text-xl font-semibold text-white">Question</h2>
              </div>

              {/* Question Text */}
              <div className="mb-8">
                <p className="text-lg text-white leading-relaxed">
                  {currentQuestion.question}
                </p>
              </div>

              {/* Answer Options */}
              <div className="space-y-4">
                {currentQuestion.options.map((option, index) => (
                  <button
                    key={index}
                    onClick={() => handleAnswerSelect(index)}
                    disabled={isAnswered}
                    className={`w-full p-4 rounded-xl border-2 transition-all duration-200 text-left group ${
                      selectedAnswer === index
                        ? isAnswered
                          ? index === currentQuestion.correct_answer
                            ? 'border-green-500 bg-green-500/20 text-green-100'
                            : 'border-red-500 bg-red-500/20 text-red-100'
                          : 'border-blue-500 bg-blue-500/20 text-blue-100'
                        : isAnswered && index === currentQuestion.correct_answer
                        ? 'border-green-500 bg-green-500/20 text-green-100'
                        : 'border-white/20 bg-white/5 text-white hover:border-white/40 hover:bg-white/10'
                    } ${isAnswered ? 'cursor-default' : 'cursor-pointer'}`}
                  >
                    <div className="flex items-center">
                      <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center mr-4 text-sm font-semibold ${
                        selectedAnswer === index
                          ? isAnswered
                            ? index === currentQuestion.correct_answer
                              ? 'border-green-400 bg-green-400 text-white'
                              : 'border-red-400 bg-red-400 text-white'
                            : 'border-blue-400 bg-blue-400 text-white'
                          : isAnswered && index === currentQuestion.correct_answer
                          ? 'border-green-400 bg-green-400 text-white'
                          : 'border-white/30 text-white/50'
                      }`}>
                        {String.fromCharCode(65 + index)}
                      </div>
                      <span className="flex-1">{option}</span>
                      {isAnswered && index === currentQuestion.correct_answer && (
                        <svg className="w-5 h-5 text-green-400 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                      {isAnswered && selectedAnswer === index && index !== currentQuestion.correct_answer && (
                        <svg className="w-5 h-5 text-red-400 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      )}
                    </div>
                  </button>
                ))}
              </div>

              {/* Explanation */}
              {showExplanation && currentQuestion.explanation && (
                <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl">
                  <h3 className="text-blue-400 font-semibold mb-2 flex items-center">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Explanation
                  </h3>
                  <p className="text-blue-100 text-sm leading-relaxed">
                    {currentQuestion.explanation}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between items-center">
            <button
              onClick={() => navigate('/dashboard')}
              className="px-6 py-3 bg-white/10 border border-white/20 rounded-xl text-white hover:bg-white/20 transition-all duration-200 flex items-center"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Exit Quiz
            </button>

            <div className="flex space-x-4">
              {!isAnswered ? (
                <button
                  onClick={handleSubmitAnswer}
                  disabled={selectedAnswer === null}
                  className="px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Submit Answer
                </button>
              ) : (
                <button
                  onClick={handleNextQuestion}
                  className="px-8 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all duration-200 flex items-center"
                >
                  {currentQuestionIndex < questions.length - 1 ? (
                    <>
                      <span>Next Question</span>
                      <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </>
                  ) : (
                    <>
                      <span>Finish Quiz</span>
                      <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </>
                  )}
                </button>
              )}
            </div>
          </div>

          {/* Question Navigation */}
          <div className="mt-8">
            <h3 className="text-white font-semibold mb-4">Question Navigation</h3>
            <div className="grid grid-cols-5 md:grid-cols-10 gap-2">
              {questions.map((_, index) => (
                <button
                  key={index}
                  onClick={() => {
                    if (index !== currentQuestionIndex) {
                      setCurrentQuestionIndex(index);
                      setSelectedAnswer(answers[index]);
                      setIsAnswered(answers[index] !== null);
                      setShowExplanation(answers[index] !== null);
                    }
                  }}
                  className={`w-10 h-10 rounded-lg border-2 text-sm font-semibold transition-all duration-200 ${
                    index === currentQuestionIndex
                      ? 'border-blue-500 bg-blue-500 text-white'
                      : answers[index] !== null
                      ? 'border-green-500 bg-green-500/20 text-green-400'
                      : 'border-white/20 bg-white/5 text-white/50 hover:border-white/40 hover:bg-white/10'
                  }`}
                >
                  {index + 1}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizInterface; 