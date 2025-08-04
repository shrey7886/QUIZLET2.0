import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

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
  time_limit: number;
}

interface ResultsData {
  score: number;
  totalQuestions: number;
  correctAnswers: number;
  answers: (number | null)[];
  questions: Question[];
  config: QuizConfig;
  timeUsed?: number;
}

const ResultsPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [showExplanations, setShowExplanations] = useState(false);
  
  const results: ResultsData = location.state;

  if (!results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl text-white mb-4">No Results Found</h1>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const { score, totalQuestions, correctAnswers, answers, questions, config, timeUsed } = results;
  const accuracy = Math.round((correctAnswers / totalQuestions) * 100);
  const timeUsedMinutes = timeUsed ? Math.floor(timeUsed / 60) : 0;
  const timeUsedSeconds = timeUsed ? timeUsed % 60 : 0;

  const getScoreColor = () => {
    if (accuracy >= 80) return 'text-green-400';
    if (accuracy >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreMessage = () => {
    if (accuracy >= 90) return 'Outstanding! You\'re a master! 🏆';
    if (accuracy >= 80) return 'Excellent work! You\'re doing great! 🌟';
    if (accuracy >= 70) return 'Good job! Keep up the good work! 👍';
    if (accuracy >= 60) return 'Not bad! Room for improvement! 📈';
    return 'Keep practicing! You\'ll get better! 💪';
  };

  const getScoreEmoji = () => {
    if (accuracy >= 90) return '🏆';
    if (accuracy >= 80) return '🌟';
    if (accuracy >= 70) return '👍';
    if (accuracy >= 60) return '📈';
    return '💪';
  };

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
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Quiz Results
            </h1>
            <p className="text-xl text-gray-300">
              {config.topic} • {config.difficulty} • {totalQuestions} questions
            </p>
          </div>

          {/* Score Summary */}
          <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-8 mb-8 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-600/5 rounded-2xl"></div>
            
            <div className="relative z-10 text-center">
              <div className="text-8xl mb-4">{getScoreEmoji()}</div>
              <h2 className="text-3xl font-bold text-white mb-2">{getScoreMessage()}</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-8">
                <div className="text-center">
                  <div className={`text-4xl font-bold ${getScoreColor()} mb-2`}>{accuracy}%</div>
                  <div className="text-gray-400">Accuracy</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-blue-400 mb-2">{correctAnswers}/{totalQuestions}</div>
                  <div className="text-gray-400">Correct Answers</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-purple-400 mb-2">{totalQuestions - correctAnswers}</div>
                  <div className="text-gray-400">Incorrect</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-green-400 mb-2">
                    {timeUsedMinutes}:{timeUsedSeconds.toString().padStart(2, '0')}
                  </div>
                  <div className="text-gray-400">Time Used</div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mt-8">
                <div className="flex justify-between text-sm text-gray-400 mb-2">
                  <span>Progress</span>
                  <span>{accuracy}%</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-3">
                  <div 
                    className={`h-3 rounded-full transition-all duration-1000 ease-out ${
                      accuracy >= 80 ? 'bg-gradient-to-r from-green-500 to-emerald-500' :
                      accuracy >= 60 ? 'bg-gradient-to-r from-yellow-500 to-orange-500' :
                      'bg-gradient-to-r from-red-500 to-pink-500'
                    }`}
                    style={{ width: `${accuracy}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* Quiz Statistics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Quiz Info */}
            <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-xl font-bold text-white mb-4">📊 Quiz Information</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Topic:</span>
                  <span className="text-white font-medium">{config.topic}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Difficulty:</span>
                  <span className="text-white font-medium capitalize">{config.difficulty}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Questions:</span>
                  <span className="text-white font-medium">{config.num_questions}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Time Limit:</span>
                  <span className="text-white font-medium">{Math.floor(config.time_limit / 60)} minutes</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Time Used:</span>
                  <span className="text-white font-medium">
                    {timeUsedMinutes}:{timeUsedSeconds.toString().padStart(2, '0')}
                  </span>
                </div>
              </div>
            </div>

            {/* Performance Analysis */}
            <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-xl font-bold text-white mb-4">📈 Performance Analysis</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">Correct Answers</span>
                    <span className="text-green-400">{correctAnswers}</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all duration-1000"
                      style={{ width: `${(correctAnswers / totalQuestions) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">Incorrect Answers</span>
                    <span className="text-red-400">{totalQuestions - correctAnswers}</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <div 
                      className="bg-red-500 h-2 rounded-full transition-all duration-1000"
                      style={{ width: `${((totalQuestions - correctAnswers) / totalQuestions) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">Accuracy Rate</span>
                    <span className="text-blue-400">{accuracy}%</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all duration-1000"
                      style={{ width: `${accuracy}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Question Review */}
          <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-8 mb-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-white">📝 Question Review</h3>
              <button
                onClick={() => setShowExplanations(!showExplanations)}
                className="px-4 py-2 bg-blue-500/20 border border-blue-500/30 text-blue-400 rounded-lg hover:bg-blue-500/30 transition-colors"
              >
                {showExplanations ? 'Hide' : 'Show'} Explanations
              </button>
            </div>

            <div className="space-y-6">
              {questions.map((question, index) => {
                const userAnswer = answers[index];
                const isCorrect = userAnswer === question.correct_answer;
                
                return (
                  <div key={question.id} className="border border-white/10 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-lg font-semibold text-white">
                        Question {index + 1}
                      </h4>
                      <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                        isCorrect 
                          ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                          : 'bg-red-500/20 text-red-400 border border-red-500/30'
                      }`}>
                        {isCorrect ? '✓ Correct' : '✗ Incorrect'}
                      </div>
                    </div>

                    <p className="text-white mb-4 leading-relaxed">{question.question}</p>

                    <div className="space-y-2 mb-4">
                      {question.options.map((option, optionIndex) => (
                        <div
                          key={optionIndex}
                          className={`p-3 rounded-lg border-2 ${
                            optionIndex === question.correct_answer
                              ? 'border-green-500 bg-green-500/20 text-green-100'
                              : optionIndex === userAnswer && !isCorrect
                              ? 'border-red-500 bg-red-500/20 text-red-100'
                              : 'border-white/20 bg-white/5 text-white'
                          }`}
                        >
                          <div className="flex items-center">
                            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center mr-3 text-sm font-semibold ${
                              optionIndex === question.correct_answer
                                ? 'border-green-400 bg-green-400 text-white'
                                : optionIndex === userAnswer && !isCorrect
                                ? 'border-red-400 bg-red-400 text-white'
                                : 'border-white/30 text-white/50'
                            }`}>
                              {String.fromCharCode(65 + optionIndex)}
                            </div>
                            <span className="flex-1">{option}</span>
                            {optionIndex === question.correct_answer && (
                              <svg className="w-5 h-5 text-green-400 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            )}
                            {optionIndex === userAnswer && !isCorrect && (
                              <svg className="w-5 h-5 text-red-400 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>

                    {showExplanations && question.explanation && (
                      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                        <h5 className="text-blue-400 font-semibold mb-2 flex items-center">
                          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Explanation
                        </h5>
                        <p className="text-blue-100 text-sm leading-relaxed">{question.explanation}</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/quiz-generator')}
              className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200 flex items-center justify-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Take Another Quiz
            </button>
            
            <button
              onClick={() => navigate('/dashboard')}
              className="px-8 py-4 bg-white/10 border border-white/20 text-white rounded-xl hover:bg-white/20 transition-all duration-200 flex items-center justify-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
              </svg>
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage; 