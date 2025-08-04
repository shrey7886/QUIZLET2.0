import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import ReactSlider from 'react-slider';
import { useNavigate } from 'react-router-dom';
import { quizAPI } from '../services/api';
import { QuizConfig } from '../types';
import Header from './Header';

interface QuizFormData {
  topic: string;
  difficulty: string;
  num_questions: number;
  time_limit: number;
}

const QuizDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string>('');

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<QuizFormData>({
    defaultValues: {
      topic: '',
      difficulty: 'Medium',
      num_questions: 5,
      time_limit: 10,
    },
  });

  const watchedNumQuestions = watch('num_questions');
  const watchedTimeLimit = watch('time_limit');

  const onSubmit = async (data: QuizFormData) => {
    setIsGenerating(true);
    setError('');

    try {
      const quizResponse = await quizAPI.generateQuiz(data);
      navigate('/quiz', { 
        state: { 
          questions: quizResponse.data?.quiz || quizResponse.data || [],
          config: data 
        } 
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate quiz. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const difficultyOptions = [
    { value: 'Easy', label: 'Easy', color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-200' },
    { value: 'Medium', label: 'Medium', color: 'text-yellow-600', bgColor: 'bg-yellow-50', borderColor: 'border-yellow-200' },
    { value: 'Hard', label: 'Hard', color: 'text-red-600', bgColor: 'bg-red-50', borderColor: 'border-red-200' },
  ];

  const quickStartTopics = [
    { 
      topic: 'Python Basics', 
      difficulty: 'Easy', 
      questions: 5, 
      time: 10,
      icon: '🐍',
      description: 'Learn fundamental Python concepts'
    },
    { 
      topic: 'JavaScript Fundamentals', 
      difficulty: 'Medium', 
      questions: 8, 
      time: 15,
      icon: '⚡',
      description: 'Master JavaScript essentials'
    },
    { 
      topic: 'Data Structures & Algorithms', 
      difficulty: 'Hard', 
      questions: 10, 
      time: 20,
      icon: '🧮',
      description: 'Advanced programming concepts'
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-5xl font-bold text-slate-900 mb-4">
            Create Your Perfect
            <span className="gradient-text block">Quiz Experience</span>
          </h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Choose your topic, difficulty, and settings to generate a personalized quiz powered by advanced AI
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Quiz Configuration */}
          <div className="lg:col-span-2">
            <div className="card animate-slide-up">
              <div className="flex items-center mb-6">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center mr-3">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold text-slate-900">Quiz Configuration</h2>
              </div>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center space-x-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-sm font-medium">{error}</span>
                  </div>
                )}

                {/* Topic Selection */}
                <div>
                  <label htmlFor="topic" className="block text-lg font-semibold text-slate-900 mb-3">
                    What would you like to learn about?
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                    <input
                      id="topic"
                      type="text"
                      {...register('topic', {
                        required: 'Topic is required',
                        minLength: {
                          value: 3,
                          message: 'Topic must be at least 3 characters',
                        },
                      })}
                      className="input-field pl-12 text-lg"
                      placeholder="e.g., Python Programming, World History, Mathematics..."
                    />
                  </div>
                  {errors.topic && (
                    <p className="mt-2 text-sm text-red-600 flex items-center">
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {errors.topic.message}
                    </p>
                  )}
                </div>

                {/* Difficulty Selection */}
                <div>
                  <label className="block text-lg font-semibold text-slate-900 mb-3">
                    Choose Difficulty Level
                  </label>
                  <div className="grid grid-cols-3 gap-4">
                    {difficultyOptions.map((option) => (
                      <label
                        key={option.value}
                        className={`relative flex cursor-pointer rounded-xl border-2 p-4 transition-all duration-300 hover:shadow-md ${
                          watch('difficulty') === option.value
                            ? `${option.borderColor} ${option.bgColor} shadow-md scale-105`
                            : 'border-slate-200 bg-white hover:border-slate-300'
                        }`}
                      >
                        <input
                          type="radio"
                          value={option.value}
                          {...register('difficulty')}
                          className="sr-only"
                        />
                        <div className="flex flex-col items-center text-center">
                          <span className={`text-lg font-semibold ${option.color} mb-1`}>
                            {option.label}
                          </span>
                          <span className="text-xs text-slate-500">
                            {option.value === 'Easy' && 'Beginner friendly'}
                            {option.value === 'Medium' && 'Balanced challenge'}
                            {option.value === 'Hard' && 'Advanced concepts'}
                          </span>
                        </div>
                        <div className="absolute top-2 right-2 w-4 h-4 border-2 border-slate-300 rounded-full">
                          {watch('difficulty') === option.value && (
                            <div className="w-2 h-2 bg-blue-600 rounded-full m-0.5"></div>
                          )}
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Number of Questions Slider */}
                <div>
                  <label className="block text-lg font-semibold text-slate-900 mb-3">
                    Number of Questions: <span className="text-blue-600">{watchedNumQuestions}</span>
                  </label>
                  <div className="px-2">
                    <ReactSlider
                      className="w-full h-3 bg-slate-200 rounded-full appearance-none cursor-pointer"
                      thumbClassName="w-6 h-6 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full cursor-pointer focus:outline-none focus:ring-4 focus:ring-blue-500/30 shadow-lg"
                      trackClassName="h-3 bg-gradient-to-r from-blue-200 to-indigo-200 rounded-full"
                      value={watchedNumQuestions}
                      onChange={(value) => setValue('num_questions', value)}
                      min={1}
                      max={15}
                      step={1}
                    />
                  </div>
                  <div className="flex justify-between text-sm text-slate-500 mt-2">
                    <span>1 question</span>
                    <span>15 questions</span>
                  </div>
                </div>

                {/* Time Limit Slider */}
                <div>
                  <label className="block text-lg font-semibold text-slate-900 mb-3">
                    Time Limit: <span className="text-blue-600">{watchedTimeLimit} minutes</span>
                  </label>
                  <div className="px-2">
                    <ReactSlider
                      className="w-full h-3 bg-slate-200 rounded-full appearance-none cursor-pointer"
                      thumbClassName="w-6 h-6 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full cursor-pointer focus:outline-none focus:ring-4 focus:ring-blue-500/30 shadow-lg"
                      trackClassName="h-3 bg-gradient-to-r from-blue-200 to-indigo-200 rounded-full"
                      value={watchedTimeLimit}
                      onChange={(value) => setValue('time_limit', value)}
                      min={1}
                      max={120}
                      step={1}
                    />
                  </div>
                  <div className="flex justify-between text-sm text-slate-500 mt-2">
                    <span>1 minute</span>
                    <span>120 minutes</span>
                  </div>
                </div>

                {/* Generate Button */}
                <button
                  type="submit"
                  disabled={isGenerating}
                  className="btn-primary w-full flex justify-center items-center py-4 px-6 text-xl font-bold"
                >
                  {isGenerating ? (
                    <div className="flex items-center">
                      <div className="spinner w-6 h-6 mr-3"></div>
                      <span>Generating Your Quiz...</span>
                    </div>
                  ) : (
                    <div className="flex items-center">
                      <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Generate Quiz
                    </div>
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Quick Start Sidebar */}
          <div className="lg:col-span-1">
            <div className="card animate-slide-up" style={{ animationDelay: '0.2s' }}>
              <div className="flex items-center mb-6">
                <div className="w-10 h-10 bg-gradient-to-r from-green-600 to-emerald-600 rounded-xl flex items-center justify-center mr-3">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-slate-900">Quick Start</h3>
              </div>

              <div className="space-y-4">
                {quickStartTopics.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setValue('topic', suggestion.topic);
                      setValue('difficulty', suggestion.difficulty);
                      setValue('num_questions', suggestion.questions);
                      setValue('time_limit', suggestion.time);
                    }}
                    className="w-full p-4 border border-slate-200 rounded-xl hover:border-blue-300 hover:bg-blue-50/50 hover:shadow-md transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] text-left"
                  >
                    <div className="flex items-start space-x-3">
                      <span className="text-2xl">{suggestion.icon}</span>
                      <div className="flex-1">
                        <h4 className="font-semibold text-slate-900 mb-1">{suggestion.topic}</h4>
                        <p className="text-sm text-slate-600 mb-2">{suggestion.description}</p>
                        <div className="flex items-center space-x-2 text-xs">
                          <span className={`badge ${
                            suggestion.difficulty === 'Easy' ? 'badge-success' :
                            suggestion.difficulty === 'Medium' ? 'badge-warning' : 'badge-error'
                          }`}>
                            {suggestion.difficulty}
                          </span>
                          <span className="text-slate-500">•</span>
                          <span className="text-slate-500">{suggestion.questions} questions</span>
                          <span className="text-slate-500">•</span>
                          <span className="text-slate-500">{suggestion.time} min</span>
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>

              <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                <h4 className="font-semibold text-slate-900 mb-2">💡 Pro Tip</h4>
                <p className="text-sm text-slate-600">
                  Start with easier topics and gradually increase difficulty as you improve. Our AI adapts to your learning pace!
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizDashboard; 