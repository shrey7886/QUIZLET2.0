import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const QuizDashboard: React.FC = () => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  // Sample data for demonstration
  const stats = {
    totalQuizzes: 24,
    completedQuizzes: 18,
    averageScore: 85,
    studyStreak: 7,
    totalStudyTime: 12.5,
    accuracyRate: 92
  };

  const recentActivity = [
    { id: 1, type: 'quiz', title: 'JavaScript Fundamentals', score: 88, date: '2 hours ago' },
    { id: 2, type: 'flashcard', title: 'React Hooks', score: 95, date: '1 day ago' },
    { id: 3, type: 'quiz', title: 'Python Basics', score: 76, date: '2 days ago' },
    { id: 4, type: 'flashcard', title: 'CSS Grid', score: 91, date: '3 days ago' }
  ];

  const quickActions = [
    { id: 1, title: 'Create Quiz', description: 'Generate a new quiz', icon: '📝', color: 'from-blue-500 to-cyan-500', href: '/quiz' },
    { id: 2, title: 'Study Cards', description: 'Review flashcards', icon: '🗂️', color: 'from-purple-500 to-pink-500', href: '/flashcards' },
    { id: 3, title: 'AI Chat', description: 'Ask questions', icon: '🤖', color: 'from-indigo-500 to-purple-500', href: '/chat' },
    { id: 4, title: 'Analytics', description: 'View progress', icon: '📊', color: 'from-green-500 to-emerald-500', href: '/analytics' }
  ];

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
        <div className="max-w-7xl mx-auto">
          {/* Welcome Section */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Welcome back, {user?.username || 'Learner'}! 👋
            </h1>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Ready to continue your learning journey? Let's make today productive!
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {/* Total Quizzes */}
            <div className="stat-card group">
              <div className="stat-icon bg-gradient-to-br from-blue-500 to-cyan-500">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="stat-content">
                <h3 className="stat-title">Total Quizzes</h3>
                <p className="stat-value">{stats.totalQuizzes}</p>
                <p className="stat-change text-green-400">+3 this week</p>
              </div>
            </div>

            {/* Average Score */}
            <div className="stat-card group">
              <div className="stat-icon bg-gradient-to-br from-purple-500 to-pink-500">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="stat-content">
                <h3 className="stat-title">Average Score</h3>
                <p className="stat-value">{stats.averageScore}%</p>
                <p className="stat-change text-green-400">+5% this month</p>
              </div>
            </div>

            {/* Study Streak */}
            <div className="stat-card group">
              <div className="stat-icon bg-gradient-to-br from-yellow-500 to-orange-500">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="stat-content">
                <h3 className="stat-title">Study Streak</h3>
                <p className="stat-value">{stats.studyStreak} days</p>
                <p className="stat-change text-green-400">🔥 Keep it up!</p>
              </div>
            </div>

            {/* Total Study Time */}
            <div className="stat-card group">
              <div className="stat-icon bg-gradient-to-br from-green-500 to-emerald-500">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="stat-content">
                <h3 className="stat-title">Study Time</h3>
                <p className="stat-value">{stats.totalStudyTime}h</p>
                <p className="stat-change text-green-400">+2.5h this week</p>
              </div>
            </div>

            {/* Accuracy Rate */}
            <div className="stat-card group">
              <div className="stat-icon bg-gradient-to-br from-indigo-500 to-purple-500">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="stat-content">
                <h3 className="stat-title">Accuracy Rate</h3>
                <p className="stat-value">{stats.accuracyRate}%</p>
                <p className="stat-change text-green-400">+3% improvement</p>
              </div>
            </div>

            {/* Completion Rate */}
            <div className="stat-card group">
              <div className="stat-icon bg-gradient-to-br from-pink-500 to-rose-500">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div className="stat-content">
                <h3 className="stat-title">Completion Rate</h3>
                <p className="stat-value">{Math.round((stats.completedQuizzes / stats.totalQuizzes) * 100)}%</p>
                <p className="stat-change text-green-400">{stats.completedQuizzes}/{stats.totalQuizzes} completed</p>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-white mb-6">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {quickActions.map((action) => (
                <a
                  key={action.id}
                  href={action.href}
                  className="quick-action-card group"
                >
                  <div className={`quick-action-icon bg-gradient-to-br ${action.color}`}>
                    <span className="text-2xl">{action.icon}</span>
                  </div>
                  <div className="quick-action-content">
                    <h3 className="quick-action-title">{action.title}</h3>
                    <p className="quick-action-description">{action.description}</p>
                  </div>
                  <div className="quick-action-arrow">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </a>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-white mb-6">Recent Activity</h2>
            <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 overflow-hidden">
              <div className="p-6">
                <div className="space-y-4">
                  {recentActivity.map((activity) => (
                    <div key={activity.id} className="activity-item group">
                      <div className="activity-icon">
                        {activity.type === 'quiz' ? (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        )}
                      </div>
                      <div className="activity-content">
                        <h4 className="activity-title">{activity.title}</h4>
                        <p className="activity-score">Score: {activity.score}%</p>
                      </div>
                      <div className="activity-time">
                        <span className="text-sm text-gray-400">{activity.date}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Progress Section */}
          <div>
            <h2 className="text-2xl font-bold text-white mb-6">Learning Progress</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Weekly Progress */}
              <div className="progress-card">
                <h3 className="progress-title">Weekly Progress</h3>
                <div className="progress-bar-container">
                  <div className="progress-bar" style={{ width: '75%' }}></div>
                </div>
                <p className="progress-text">75% of weekly goal completed</p>
              </div>

              {/* Monthly Streak */}
              <div className="progress-card">
                <h3 className="progress-title">Monthly Streak</h3>
                <div className="streak-display">
                  <div className="streak-number">{stats.studyStreak}</div>
                  <div className="streak-label">days</div>
                </div>
                <p className="progress-text">Keep the momentum going!</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizDashboard; 