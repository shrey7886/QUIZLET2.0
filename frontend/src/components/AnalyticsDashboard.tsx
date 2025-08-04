import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { analyticsAPI } from '../services/api';
import Header from './Header';

interface AnalyticsData {
  summary: {
    overall_progress: {
      total_quizzes_taken: number;
      total_questions_answered: number;
      total_correct_answers: number;
      total_time_spent: number;
      average_score: number;
      average_accuracy: number;
      current_streak: number;
      longest_streak: number;
      topics_covered: string[];
      difficulty_progress: Record<string, number>;
    };
    topic_performance: Array<{
      topic: string;
      category: string;
      quizzes_taken: number;
      average_score: number;
      improvement_rate: number;
      weak_areas: string[];
    }>;
    difficulty_performance: Array<{
      difficulty: string;
      quizzes_taken: number;
      average_score: number;
      readiness_score: number;
    }>;
    recent_quizzes: Array<{
      id: number;
      topic: string;
      difficulty: string;
      score: number;
      accuracy: number;
      time_taken: number;
      completed_at: string;
    }>;
    weak_areas: string[];
    strengths: string[];
    recommended_actions: string[];
    learning_insights: Record<string, any>;
  };
  performance_trends: Array<{
    date: string;
    score: number;
    accuracy: number;
    time_taken: number;
    topic: string;
    difficulty: string;
  }>;
  weak_areas: Array<{
    topic: string;
    concept: string;
    error_rate: number;
    total_attempts: number;
    recommended_resources: string[];
    practice_questions_needed: number;
  }>;
  recommendations: Array<{
    type: string;
    title: string;
    description: string;
    priority: number;
    estimated_time: number;
    prerequisites: string[];
    resources: string[];
  }>;
  quiz_history: Array<{
    id: number;
    topic: string;
    difficulty: string;
    score: number;
    accuracy: number;
    time_taken: number;
    completed_at: string;
  }>;
  learning_paths: Array<{
    id: number;
    name: string;
    description: string;
    category: string;
    current_level: number;
    total_levels: number;
    completion_percentage: number;
    average_score: number;
  }>;
}

const AnalyticsDashboard: React.FC = () => {
  const { user } = useAuth();
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await analyticsAPI.getDashboard();
      setAnalyticsData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <Header />
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="spinner w-12 h-12 mx-auto mb-4"></div>
            <p className="text-slate-600">Loading your analytics...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !analyticsData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <Header />
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-red-500 mb-4">
              <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-slate-600 mb-4">{error || 'Failed to load analytics data'}</p>
            <button onClick={loadAnalyticsData} className="btn-primary">
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  const { summary, performance_trends, weak_areas, recommendations, quiz_history, learning_paths } = analyticsData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            Your Learning Analytics
          </h1>
          <p className="text-xl text-slate-600">
            Track your progress, identify areas for improvement, and optimize your learning journey
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-8">
          <nav className="flex space-x-1 bg-white rounded-xl p-1 shadow-sm">
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'progress', label: 'Progress', icon: '📈' },
              { id: 'topics', label: 'Topics', icon: '📚' },
              { id: 'weak-areas', label: 'Weak Areas', icon: '🎯' },
              { id: 'history', label: 'History', icon: '📋' },
              { id: 'recommendations', label: 'Recommendations', icon: '💡' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-blue-100 text-blue-700 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="animate-slide-up">
          {activeTab === 'overview' && (
            <OverviewTab summary={summary} performance_trends={performance_trends} />
          )}
          {activeTab === 'progress' && (
            <ProgressTab summary={summary} performance_trends={performance_trends} />
          )}
          {activeTab === 'topics' && (
            <TopicsTab summary={summary} />
          )}
          {activeTab === 'weak-areas' && (
            <WeakAreasTab weak_areas={weak_areas} />
          )}
          {activeTab === 'history' && (
            <HistoryTab quiz_history={quiz_history} />
          )}
          {activeTab === 'recommendations' && (
            <RecommendationsTab recommendations={recommendations} />
          )}
        </div>
      </div>
    </div>
  );
};

// Overview Tab Component
const OverviewTab: React.FC<{ summary: any; performance_trends: any[] }> = ({ summary, performance_trends }) => {
  const { overall_progress, learning_insights } = summary;

  return (
    <div className="space-y-8">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card text-center">
          <div className="text-3xl font-bold text-blue-600 mb-2">
            {overall_progress.total_quizzes_taken}
          </div>
          <div className="text-sm text-slate-600">Total Quizzes</div>
        </div>
        
        <div className="card text-center">
          <div className="text-3xl font-bold text-green-600 mb-2">
            {overall_progress.average_score.toFixed(1)}%
          </div>
          <div className="text-sm text-slate-600">Average Score</div>
        </div>
        
        <div className="card text-center">
          <div className="text-3xl font-bold text-purple-600 mb-2">
            {overall_progress.current_streak}
          </div>
          <div className="text-sm text-slate-600">Current Streak</div>
        </div>
        
        <div className="card text-center">
          <div className="text-3xl font-bold text-orange-600 mb-2">
            {overall_progress.topics_covered.length}
          </div>
          <div className="text-sm text-slate-600">Topics Covered</div>
        </div>
      </div>

      {/* Performance Chart */}
      <div className="card">
        <h3 className="text-xl font-bold text-slate-900 mb-6">Performance Trends</h3>
        <div className="h-64 flex items-end justify-center space-x-2">
          {performance_trends.slice(-10).map((trend, index) => (
            <div key={index} className="flex flex-col items-center">
              <div
                className="w-8 bg-gradient-to-t from-blue-500 to-blue-300 rounded-t"
                style={{ height: `${(trend.score / 100) * 200}px` }}
              ></div>
              <div className="text-xs text-slate-500 mt-2">
                {new Date(trend.date).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Learning Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-xl font-bold text-slate-900 mb-4">Your Strengths</h3>
          <div className="space-y-2">
            {summary.strengths.map((strength: string, index: number) => (
              <div key={index} className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                <span className="text-slate-700">{strength}</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="card">
          <h3 className="text-xl font-bold text-slate-900 mb-4">Recommended Actions</h3>
          <div className="space-y-2">
            {summary.recommended_actions.map((action: string, index: number) => (
              <div key={index} className="flex items-center">
                <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                <span className="text-slate-700">{action}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Progress Tab Component
const ProgressTab: React.FC<{ summary: any; performance_trends: any[] }> = ({ summary, performance_trends }) => {
  const { overall_progress, difficulty_performance } = summary;

  return (
    <div className="space-y-8">
      {/* Progress Overview */}
      <div className="card">
        <h3 className="text-xl font-bold text-slate-900 mb-6">Overall Progress</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-slate-700">Accuracy</span>
              <span className="text-sm font-medium text-slate-700">
                {(overall_progress.average_accuracy * 100).toFixed(1)}%
              </span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${overall_progress.average_accuracy * 100}%` }}
              ></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-slate-700">Questions Answered</span>
              <span className="text-sm font-medium text-slate-700">
                {overall_progress.total_questions_answered}
              </span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${Math.min((overall_progress.total_questions_answered / 1000) * 100, 100)}%` }}
              ></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-slate-700">Time Spent</span>
              <span className="text-sm font-medium text-slate-700">
                {Math.round(overall_progress.total_time_spent)}m
              </span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${Math.min((overall_progress.total_time_spent / 100) * 100, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Difficulty Progress */}
      <div className="card">
        <h3 className="text-xl font-bold text-slate-900 mb-6">Difficulty Progress</h3>
        <div className="space-y-4">
          {difficulty_performance.map((diff: any) => (
            <div key={diff.difficulty} className="border border-slate-200 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium text-slate-900">{diff.difficulty}</span>
                <span className="text-sm text-slate-600">
                  {diff.quizzes_taken} quizzes • {diff.average_score.toFixed(1)}% avg
                </span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${diff.average_score}%` }}
                ></div>
              </div>
              {diff.readiness_score > 70 && (
                <div className="mt-2 text-sm text-green-600">
                  ✅ Ready for next difficulty level!
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Topics Tab Component
const TopicsTab: React.FC<{ summary: any }> = ({ summary }) => {
  const { topic_performance } = summary;

  return (
    <div className="space-y-8">
      <div className="card">
        <h3 className="text-xl font-bold text-slate-900 mb-6">Topic Performance</h3>
        <div className="space-y-4">
          {topic_performance.map((topic: any) => (
            <div key={topic.topic} className="border border-slate-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h4 className="font-semibold text-slate-900">{topic.topic}</h4>
                  <p className="text-sm text-slate-600">{topic.category}</p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-blue-600">
                    {topic.average_score.toFixed(1)}%
                  </div>
                  <div className="text-sm text-slate-600">
                    {topic.quizzes_taken} quizzes
                  </div>
                </div>
              </div>
              
              <div className="progress-bar mb-3">
                <div
                  className="progress-fill"
                  style={{ width: `${topic.average_score}%` }}
                ></div>
              </div>
              
              {topic.improvement_rate > 0 && (
                <div className="text-sm text-green-600">
                  📈 {topic.improvement_rate.toFixed(1)}% improvement
                </div>
              )}
              
              {topic.weak_areas.length > 0 && (
                <div className="mt-3">
                  <div className="text-sm font-medium text-slate-700 mb-1">Areas to improve:</div>
                  <div className="flex flex-wrap gap-1">
                    {topic.weak_areas.slice(0, 3).map((area: string, index: number) => (
                      <span key={index} className="badge badge-warning text-xs">
                        {area}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Weak Areas Tab Component
const WeakAreasTab: React.FC<{ weak_areas: any[] }> = ({ weak_areas }) => {
  return (
    <div className="space-y-8">
      <div className="card">
        <h3 className="text-xl font-bold text-slate-900 mb-6">Areas for Improvement</h3>
        <div className="space-y-4">
          {weak_areas.map((area, index) => (
            <div key={index} className="border border-red-200 rounded-lg p-4 bg-red-50">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h4 className="font-semibold text-slate-900">{area.concept}</h4>
                  <p className="text-sm text-slate-600">{area.topic}</p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-red-600">
                    {(area.error_rate * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-slate-600">
                    {area.total_attempts} attempts
                  </div>
                </div>
              </div>
              
              <div className="progress-bar mb-3">
                <div
                  className="progress-fill bg-red-500"
                  style={{ width: `${area.error_rate * 100}%` }}
                ></div>
              </div>
              
              <div className="text-sm text-slate-700 mb-3">
                Need {area.practice_questions_needed} more practice questions
              </div>
              
              <div>
                <div className="text-sm font-medium text-slate-700 mb-1">Recommended resources:</div>
                <div className="flex flex-wrap gap-1">
                  {area.recommended_resources.map((resource: string, idx: number) => (
                    <span key={idx} className="badge badge-primary text-xs">
                      {resource}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// History Tab Component
const HistoryTab: React.FC<{ quiz_history: any[] }> = ({ quiz_history }) => {
  return (
    <div className="space-y-8">
      <div className="card">
        <h3 className="text-xl font-bold text-slate-900 mb-6">Quiz History</h3>
        <div className="space-y-4">
          {quiz_history.map((quiz) => (
            <div key={quiz.id} className="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-semibold text-slate-900">{quiz.topic}</h4>
                  <p className="text-sm text-slate-600">
                    {new Date(quiz.completed_at).toLocaleDateString()} • {quiz.difficulty}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-blue-600">
                    {quiz.score.toFixed(1)}%
                  </div>
                  <div className="text-sm text-slate-600">
                    {quiz.time_taken.toFixed(1)}m
                  </div>
                </div>
              </div>
              
              <div className="mt-3 flex items-center justify-between">
                <div className="flex items-center space-x-4 text-sm text-slate-600">
                  <span>Accuracy: {(quiz.accuracy * 100).toFixed(1)}%</span>
                </div>
                <div className="flex space-x-2">
                  <span className={`badge ${
                    quiz.score >= 80 ? 'badge-success' :
                    quiz.score >= 60 ? 'badge-warning' : 'badge-error'
                  }`}>
                    {quiz.score >= 80 ? 'Excellent' :
                     quiz.score >= 60 ? 'Good' : 'Needs Work'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Recommendations Tab Component
const RecommendationsTab: React.FC<{ recommendations: any[] }> = ({ recommendations }) => {
  return (
    <div className="space-y-8">
      <div className="card">
        <h3 className="text-xl font-bold text-slate-900 mb-6">Learning Recommendations</h3>
        <div className="space-y-4">
          {recommendations.map((rec, index) => (
            <div key={index} className="border border-blue-200 rounded-lg p-4 bg-blue-50">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h4 className="font-semibold text-slate-900">{rec.title}</h4>
                  <p className="text-sm text-slate-600">{rec.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-blue-600">
                    Priority {rec.priority}/5
                  </div>
                  <div className="text-sm text-slate-600">
                    {rec.estimated_time}m
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2 mb-3">
                <span className="badge badge-primary">{rec.type}</span>
                <span className="text-sm text-slate-600">
                  ⏱️ {rec.estimated_time} minutes
                </span>
              </div>
              
              {rec.resources.length > 0 && (
                <div>
                  <div className="text-sm font-medium text-slate-700 mb-1">Resources:</div>
                  <div className="flex flex-wrap gap-1">
                    {rec.resources.map((resource: string, idx: number) => (
                      <span key={idx} className="badge badge-secondary text-xs">
                        {resource}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard; 