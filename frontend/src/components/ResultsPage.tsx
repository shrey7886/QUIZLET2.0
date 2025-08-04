import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { QuizResult, Question } from '../types';
import Header from './Header';

const ResultsPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { result, questions, answers } = location.state || {};
  
  const [selectedQuestion, setSelectedQuestion] = useState<number | null>(null);

  if (!result || !questions) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-slate-900 mb-4">No Results Found</h2>
          <p className="text-slate-600 mb-6">Please complete a quiz first.</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-primary"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreEmoji = (score: number) => {
    if (score >= 90) return '🎉';
    if (score >= 80) return '🎊';
    if (score >= 70) return '👍';
    if (score >= 60) return '😊';
    if (score >= 50) return '😐';
    return '😔';
  };

  const getScoreMessage = (score: number) => {
    if (score >= 90) return 'Excellent! You\'re a master of this topic!';
    if (score >= 80) return 'Great job! You have a solid understanding.';
    if (score >= 70) return 'Good work! Keep learning and improving.';
    if (score >= 60) return 'Not bad! Review the topics you missed.';
    if (score >= 50) return 'Keep practicing! You\'ll get better.';
    return 'Don\'t worry! Learning is a journey.';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <Header />
      
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Results Header */}
        <div className="text-center mb-12 animate-fade-in">
          <div className="text-6xl mb-4">{getScoreEmoji(result.score)}</div>
          <h1 className="text-4xl font-bold text-slate-900 mb-4">
            Quiz Complete!
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            {getScoreMessage(result.score)}
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Results Card */}
          <div className="lg:col-span-2">
            {/* Score Overview */}
            <div className="card mb-8 animate-slide-up">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className={`text-4xl font-bold ${getScoreColor(result.score)} mb-2`}>
                    {result.score.toFixed(1)}%
                  </div>
                  <div className="text-sm text-slate-600">Overall Score</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-blue-600 mb-2">
                    {result.correct_answers}/{result.total_questions}
                  </div>
                  <div className="text-sm text-slate-600">Correct Answers</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-indigo-600 mb-2">
                    {result.accuracy.toFixed(1)}%
                  </div>
                  <div className="text-sm text-slate-600">Accuracy</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-green-600 mb-2">
                    {Math.round(result.time_taken / 60)}m
                  </div>
                  <div className="text-sm text-slate-600">Time Taken</div>
                </div>
              </div>
            </div>

            {/* Question Review */}
            <div className="card animate-slide-up" style={{ animationDelay: '0.2s' }}>
              <h2 className="text-2xl font-bold text-slate-900 mb-6">Question Review</h2>
              
              <div className="space-y-6">
                {questions.map((question: Question, index: number) => {
                  const userAnswer = answers[index];
                  const isCorrect = userAnswer === question.correct_answer;
                  
                  return (
                    <div
                      key={index}
                      className={`p-6 rounded-xl border-2 transition-all duration-300 cursor-pointer hover:shadow-md ${
                        isCorrect ? 'border-green-200 bg-green-50/50' : 'border-red-200 bg-red-50/50'
                      }`}
                      onClick={() => setSelectedQuestion(selectedQuestion === index ? null : index)}
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${
                            isCorrect ? 'bg-green-500' : 'bg-red-500'
                          }`}>
                            {isCorrect ? (
                              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            ) : (
                              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            )}
                          </div>
                          <h3 className="text-lg font-semibold text-slate-900">
                            Question {index + 1}
                          </h3>
                        </div>
                        <button className="text-slate-400 hover:text-slate-600">
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </button>
                      </div>
                      
                      <p className="text-slate-900 mb-4">{question.question}</p>
                      
                      <div className="space-y-2 mb-4">
                        {question.options.map((option, optionIndex) => (
                          <div
                            key={optionIndex}
                            className={`p-3 rounded-lg border-2 ${
                              option === question.correct_answer
                                ? 'border-green-500 bg-green-100'
                                : option === userAnswer && !isCorrect
                                ? 'border-red-500 bg-red-100'
                                : 'border-slate-200 bg-white'
                            }`}
                          >
                            <div className="flex items-center">
                              <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                                option === question.correct_answer
                                  ? 'border-green-500 bg-green-500'
                                  : option === userAnswer && !isCorrect
                                  ? 'border-red-500 bg-red-500'
                                  : 'border-slate-300'
                              }`}>
                                {option === question.correct_answer && (
                                  <div className="w-1 h-1 bg-white rounded-full m-0.5"></div>
                                )}
                                {option === userAnswer && !isCorrect && (
                                  <div className="w-1 h-1 bg-white rounded-full m-0.5"></div>
                                )}
                              </div>
                              <span className="text-slate-900">{option}</span>
                              {option === question.correct_answer && (
                                <span className="ml-auto text-green-600 font-semibold">Correct</span>
                              )}
                              {option === userAnswer && !isCorrect && (
                                <span className="ml-auto text-red-600 font-semibold">Your Answer</span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      {selectedQuestion === index && (
                        <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                          <h4 className="font-semibold text-blue-900 mb-2">Explanation</h4>
                          <p className="text-blue-800">{question.explanation}</p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            {/* Performance Summary */}
            <div className="card mb-6 animate-slide-up" style={{ animationDelay: '0.4s' }}>
              <h3 className="text-xl font-bold text-slate-900 mb-4">Performance Summary</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-slate-600">Correct Answers</span>
                  <span className="font-semibold text-green-600">{result.correct_answers}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-600">Incorrect Answers</span>
                  <span className="font-semibold text-red-600">{result.total_questions - result.correct_answers}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-600">Accuracy</span>
                  <span className="font-semibold text-blue-600">{result.accuracy.toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-600">Time Per Question</span>
                  <span className="font-semibold text-indigo-600">
                    {Math.round(result.time_taken / result.total_questions)}s
                  </span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="card animate-slide-up" style={{ animationDelay: '0.6s' }}>
              <h3 className="text-xl font-bold text-slate-900 mb-4">What's Next?</h3>
              
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/dashboard')}
                  className="btn-primary w-full"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Take Another Quiz
                </button>
                
                <button
                  onClick={() => navigate('/history')}
                  className="btn-secondary w-full"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  View History
                </button>
                
                <button
                  onClick={() => navigate('/stats')}
                  className="btn-secondary w-full"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  View Analytics
                </button>
              </div>
            </div>

            {/* Tips */}
            <div className="card animate-slide-up" style={{ animationDelay: '0.8s' }}>
              <h3 className="text-xl font-bold text-slate-900 mb-4">💡 Learning Tips</h3>
              
              <div className="space-y-3 text-sm text-slate-600">
                <p>• Review questions you got wrong to understand the concepts better</p>
                <p>• Take quizzes on the same topic to reinforce your learning</p>
                <p>• Use the AI tutor to get explanations for difficult concepts</p>
                <p>• Practice regularly to improve your knowledge retention</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage; 