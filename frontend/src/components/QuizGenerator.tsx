import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface QuizConfig {
  topic: string;
  difficulty: string;
  num_questions: number;
  time_limit: number;
}

const QuizGenerator: React.FC = () => {
  const navigate = useNavigate();
  const [isGenerating, setIsGenerating] = useState(false);
  const [customTopic, setCustomTopic] = useState('');
  const [useCustomTopic, setUseCustomTopic] = useState(false);
  const [config, setConfig] = useState<QuizConfig>({
    topic: '',
    difficulty: 'medium',
    num_questions: 10,
    time_limit: 300
  });

  const topics = [
    'JavaScript Fundamentals',
    'React Hooks',
    'Python Basics',
    'Data Structures',
    'Algorithms',
    'Web Development',
    'Database Design',
    'Machine Learning',
    'Computer Science',
    'Software Engineering'
  ];

  const difficulties = [
    { value: 'easy', label: 'Easy', color: 'text-green-400' },
    { value: 'medium', label: 'Medium', color: 'text-yellow-400' },
    { value: 'hard', label: 'Hard', color: 'text-red-400' }
  ];

  const questionCounts = [5, 10, 15, 20, 25, 30];
  const timeLimits = [
    { value: 180, label: '3 minutes' },
    { value: 300, label: '5 minutes' },
    { value: 600, label: '10 minutes' },
    { value: 900, label: '15 minutes' },
    { value: 1200, label: '20 minutes' }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const finalTopic = useCustomTopic ? customTopic.trim() : config.topic;
    if (!finalTopic) {
      alert('Please select or enter a topic');
      return;
    }

    setIsGenerating(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/quiz/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ ...config, topic: finalTopic })
      });

      if (response.ok) {
        const data = await response.json();
        navigate('/quiz', { 
          state: { 
            questions: data.questions, 
            config: config 
          } 
        });
      } else {
        throw new Error('Failed to generate quiz');
      }
    } catch (error) {
      console.error('Error generating quiz:', error);
      alert('Failed to generate quiz. Please try again.');
    } finally {
      setIsGenerating(false);
    }
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
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Create Your Quiz
            </h1>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Customize your learning experience with AI-generated questions tailored to your preferences
            </p>
          </div>

          {/* Quiz Configuration Form */}
          <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-8 relative overflow-hidden">
            {/* Form Background Glow */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-600/5 rounded-2xl"></div>
            
            <form onSubmit={handleSubmit} className="relative z-10 space-y-8">
              {/* Topic Selection */}
              <div>
                <label className="block text-white font-semibold mb-4 text-lg">
                  📚 Select Topic
                </label>
                
                {/* Toggle between predefined and custom topics */}
                <div className="flex mb-6 bg-white/5 rounded-xl p-1 border border-white/10">
                  <button
                    type="button"
                    onClick={() => {
                      setUseCustomTopic(false);
                      setCustomTopic('');
                    }}
                    className={`flex-1 py-3 px-4 rounded-lg transition-all duration-200 font-medium ${
                      !useCustomTopic
                        ? 'bg-blue-500 text-white'
                        : 'text-gray-300 hover:text-white'
                    }`}
                  >
                    📋 Predefined Topics
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setUseCustomTopic(true);
                      setConfig({ ...config, topic: '' });
                    }}
                    className={`flex-1 py-3 px-4 rounded-lg transition-all duration-200 font-medium ${
                      useCustomTopic
                        ? 'bg-blue-500 text-white'
                        : 'text-gray-300 hover:text-white'
                    }`}
                  >
                    ✏️ Custom Topic
                  </button>
                </div>

                {/* Predefined Topics */}
                {!useCustomTopic && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {topics.map((topic) => (
                      <button
                        key={topic}
                        type="button"
                        onClick={() => setConfig({ ...config, topic })}
                        className={`p-4 rounded-xl border-2 transition-all duration-200 text-left group ${
                          config.topic === topic
                            ? 'border-blue-500 bg-blue-500/20 text-blue-100'
                            : 'border-white/20 bg-white/5 text-white hover:border-white/40 hover:bg-white/10'
                        }`}
                      >
                        <div className="flex items-center">
                          <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                            config.topic === topic
                              ? 'border-blue-400 bg-blue-400'
                              : 'border-white/30'
                          }`}>
                            {config.topic === topic && (
                              <div className="w-2 h-2 bg-white rounded-full mx-auto mt-0.5"></div>
                            )}
                          </div>
                          <span className="font-medium">{topic}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {/* Custom Topic Input */}
                {useCustomTopic && (
                  <div className="space-y-4">
                    <div className="relative">
                      <input
                        type="text"
                        value={customTopic}
                        onChange={(e) => setCustomTopic(e.target.value)}
                        placeholder="Enter any topic you want to learn about..."
                        className="w-full px-6 py-4 bg-white/10 border-2 border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:bg-white/15 transition-all duration-200"
                        maxLength={100}
                      />
                      <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                      </div>
                    </div>
                    
                    {/* Example topics for inspiration */}
                    <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                      <div className="text-sm text-gray-300 mb-2">💡 Examples:</div>
                      <div className="flex flex-wrap gap-2">
                        {['Quantum Physics', 'Ancient History', 'Cooking Techniques', 'Photography', 'Space Exploration', 'Cryptocurrency'].map((example) => (
                          <button
                            key={example}
                            type="button"
                            onClick={() => setCustomTopic(example)}
                            className="px-3 py-1 bg-white/10 rounded-full text-xs text-gray-300 hover:bg-white/20 hover:text-white transition-all duration-200"
                          >
                            {example}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Difficulty Selection */}
              <div>
                <label className="block text-white font-semibold mb-4 text-lg">
                  🎯 Difficulty Level
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {difficulties.map((difficulty) => (
                    <button
                      key={difficulty.value}
                      type="button"
                      onClick={() => setConfig({ ...config, difficulty: difficulty.value })}
                      className={`p-4 rounded-xl border-2 transition-all duration-200 text-center group ${
                        config.difficulty === difficulty.value
                          ? 'border-blue-500 bg-blue-500/20 text-blue-100'
                          : 'border-white/20 bg-white/5 text-white hover:border-white/40 hover:bg-white/10'
                      }`}
                    >
                      <div className={`text-2xl mb-2 ${difficulty.color}`}>
                        {difficulty.value === 'easy' && '😊'}
                        {difficulty.value === 'medium' && '😐'}
                        {difficulty.value === 'hard' && '😰'}
                      </div>
                      <div className="font-semibold">{difficulty.label}</div>
                      <div className="text-sm opacity-70 mt-1">
                        {difficulty.value === 'easy' && 'Beginner friendly'}
                        {difficulty.value === 'medium' && 'Balanced challenge'}
                        {difficulty.value === 'hard' && 'Expert level'}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Number of Questions */}
              <div>
                <label className="block text-white font-semibold mb-4 text-lg">
                  ❓ Number of Questions
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                  {questionCounts.map((count) => (
                    <button
                      key={count}
                      type="button"
                      onClick={() => setConfig({ ...config, num_questions: count })}
                      className={`p-4 rounded-xl border-2 transition-all duration-200 text-center ${
                        config.num_questions === count
                          ? 'border-blue-500 bg-blue-500/20 text-blue-100'
                          : 'border-white/20 bg-white/5 text-white hover:border-white/40 hover:bg-white/10'
                      }`}
                    >
                      <div className="text-2xl font-bold">{count}</div>
                      <div className="text-sm opacity-70">questions</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Time Limit */}
              <div>
                <label className="block text-white font-semibold mb-4 text-lg">
                  ⏱️ Time Limit
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                  {timeLimits.map((time) => (
                    <button
                      key={time.value}
                      type="button"
                      onClick={() => setConfig({ ...config, time_limit: time.value })}
                      className={`p-4 rounded-xl border-2 transition-all duration-200 text-center ${
                        config.time_limit === time.value
                          ? 'border-blue-500 bg-blue-500/20 text-blue-100'
                          : 'border-white/20 bg-white/5 text-white hover:border-white/40 hover:bg-white/10'
                      }`}
                    >
                      <div className="text-2xl mb-1">⏰</div>
                      <div className="font-semibold">{time.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Summary */}
              <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                <h3 className="text-white font-semibold mb-4 text-lg">📋 Quiz Summary</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400">
                      {useCustomTopic ? (customTopic || 'Enter custom topic') : (config.topic || 'Not selected')}
                    </div>
                    <div className="text-sm text-gray-400">Topic</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-400 capitalize">{config.difficulty}</div>
                    <div className="text-sm text-gray-400">Difficulty</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-400">{config.num_questions}</div>
                    <div className="text-sm text-gray-400">Questions</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-400">{Math.floor(config.time_limit / 60)}m</div>
                    <div className="text-sm text-gray-400">Time Limit</div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 pt-6">
                <button
                  type="button"
                  onClick={() => navigate('/dashboard')}
                  className="flex-1 px-8 py-4 bg-white/10 border border-white/20 rounded-xl text-white hover:bg-white/20 transition-all duration-200 flex items-center justify-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                  Back to Dashboard
                </button>
                
                <button
                  type="submit"
                  disabled={(useCustomTopic ? !customTopic.trim() : !config.topic) || isGenerating}
                  className="flex-1 px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {isGenerating ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Generating Quiz...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Start Quiz
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizGenerator; 