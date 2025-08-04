import axios from 'axios';

// API base URL configuration
const getApiBaseUrl = () => {
  // For production deployment
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // For local development
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  
  // For Railway deployment
  if (window.location.hostname.includes('railway.app')) {
    return 'https://quizlet-production-0834.up.railway.app';
  }
  
  // For Render deployment
  if (window.location.hostname.includes('render.com')) {
    return window.location.origin;
  }
  
  // Fallback to current origin
  return window.location.origin;
};

const API_BASE_URL = getApiBaseUrl();

console.log('API Base URL:', API_BASE_URL);

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('Response error:', error);
    
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    
    if (error.response?.status === 500) {
      console.error('Server error:', error.response.data);
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data: { email: string; username: string; password: string }) =>
    api.post('/api/auth/register', data),
  
  login: (data: { email: string; password: string }) =>
    api.post('/api/auth/login', data),
  
  getCurrentUser: () => api.get('/api/auth/me'),
};

// Quiz API
export const quizAPI = {
  generateQuiz: (config: any) => api.post('/api/quiz/generate', config),
  
  submitAnswer: (quizId: number, answer: any) =>
    api.post(`/api/quiz/${quizId}/submit-answer`, answer),
  
  completeQuiz: (quizId: number) => api.post(`/api/quiz/${quizId}/complete`),
  
  getQuizHistory: () => api.get('/api/quiz/history'),
  
  getQuizQuestions: (quizId: number) => api.get(`/api/quiz/${quizId}/questions`),
  
  chatWithTutor: (message: string, context?: string) =>
    api.post('/api/quiz/chat', { message, context }),
};

// User API
export const userAPI = {
  getProfile: () => api.get('/api/user/profile'),
  
  getStats: () => api.get('/api/user/stats'),
  
  getRecentActivity: () => api.get('/api/user/recent-activity'),
};

// Analytics API
export const analyticsAPI = {
  // Dashboard
  getDashboard: () => api.get('/api/analytics/dashboard'),
  
  // Progress
  getProgress: () => api.get('/api/analytics/progress'),
  
  // History
  getHistory: (params?: {
    limit?: number;
    offset?: number;
    topic?: string;
    difficulty?: string;
    start_date?: string;
    end_date?: string;
  }) => api.get('/api/analytics/history', { params }),
  
  getQuizDetail: (quizId: number) => api.get(`/api/analytics/history/${quizId}`),
  
  // Topics
  getTopicAnalytics: () => api.get('/api/analytics/topics'),
  
  getTopicDetail: (topic: string) => api.get(`/api/analytics/topics/${topic}`),
  
  // Difficulty
  getDifficultyAnalytics: () => api.get('/api/analytics/difficulty'),
  
  // Trends
  getPerformanceTrends: (params?: {
    days?: number;
    topic?: string;
  }) => api.get('/api/analytics/trends', { params }),
  
  // Weak Areas
  getWeakAreas: () => api.get('/api/analytics/weak-areas'),
  
  // Recommendations
  getRecommendations: () => api.get('/api/analytics/recommendations'),
  
  // Stats
  getStatsSummary: () => api.get('/api/analytics/stats/summary'),
  
  getPerformanceComparison: (period: string) =>
    api.get('/api/analytics/stats/comparison', { params: { period } }),
  
  // Export
  exportHistory: (format: 'json' | 'csv') =>
    api.get('/api/analytics/export/history', { params: { format } }),
};

// Flashcard API
export const flashcardAPI = {
  // Flashcard Management
  createFlashcard: (data: any) => api.post('/api/flashcards', data),
  
  getFlashcards: (params?: {
    status?: string;
    tags?: string[];
    limit?: number;
    offset?: number;
  }) => api.get('/api/flashcards', { params }),
  
  getFlashcard: (flashcardId: number) => api.get(`/api/flashcards/${flashcardId}`),
  
  updateFlashcard: (flashcardId: number, data: any) => 
    api.put(`/api/flashcards/${flashcardId}`, data),
  
  deleteFlashcard: (flashcardId: number) => 
    api.delete(`/api/flashcards/${flashcardId}`),
  
  // Flashcard Review
  reviewFlashcard: (flashcardId: number, data: any) =>
    api.post(`/api/flashcards/${flashcardId}/review`, data),
  
  // Flashcard Decks
  createDeck: (data: any) => api.post('/api/flashcards/decks', data),
  
  getDecks: () => api.get('/api/flashcards/decks'),
  
  getDeck: (deckId: number) => api.get(`/api/flashcards/decks/${deckId}`),
  
  updateDeck: (deckId: number, data: any) => 
    api.put(`/api/flashcards/decks/${deckId}`, data),
  
  deleteDeck: (deckId: number) => 
    api.delete(`/api/flashcards/decks/${deckId}`),
  
  addQuestionsToDeck: (deckId: number, questionIds: number[]) =>
    api.post(`/api/flashcards/decks/${deckId}/add-questions`, { question_ids: questionIds }),
  
  // Study Sessions
  startStudySession: (data: any) => api.post('/api/flashcards/study/start', data),
  
  endStudySession: (sessionId: string, data: any) =>
    api.post(`/api/flashcards/study/${sessionId}/end`, data),
  
  // Statistics
  getFlashcardStats: () => api.get('/api/flashcards/stats'),
  
  getDeckStats: (deckId: number) => api.get(`/api/flashcards/decks/${deckId}/stats`),
  
  // Search
  searchFlashcards: (data: any) => api.post('/api/flashcards/search', data),
  
  // Due Cards
  getDueCards: (limit?: number) => api.get('/api/flashcards/due', { params: { limit } }),
  
  // Import/Export
  importFlashcards: (data: any[]) => api.post('/api/flashcards/import', data),
  
  exportFlashcards: (format: 'json' | 'csv') =>
    api.get('/api/flashcards/export', { params: { format } }),
};

// Chat API
export const chatAPI = {
  // Chat Rooms
  createChatRoom: (data: any) => api.post('/api/chat/rooms', data),
  
  getUserRooms: () => api.get('/api/chat/rooms'),
  
  searchRooms: (data: any) => api.post('/api/chat/rooms/search', data),
  
  getRoom: (roomId: number) => api.get(`/api/chat/rooms/${roomId}`),
  
  updateRoom: (roomId: number, data: any) => api.put(`/api/chat/rooms/${roomId}`, data),
  
  joinRoom: (roomId: number) => api.post(`/api/chat/rooms/${roomId}/join`),
  
  leaveRoom: (roomId: number) => api.post(`/api/chat/rooms/${roomId}/leave`),
  
  // Chat Messages
  sendMessage: (data: any) => api.post('/api/chat/messages', data),
  
  getRoomMessages: (roomId: number, params?: {
    limit?: number;
    offset?: number;
  }) => api.get(`/api/chat/rooms/${roomId}/messages`, { params }),
  
  editMessage: (messageId: number, data: any) => api.put(`/api/chat/messages/${messageId}`, data),
  
  deleteMessage: (messageId: number) => api.delete(`/api/chat/messages/${messageId}`),
  
  searchMessages: (data: any) => api.post('/api/chat/messages/search', data),
  
  // Topic Suggestions
  createTopicSuggestion: (data: any) => api.post('/api/chat/suggestions', data),
  
  getTopicSuggestions: (params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }) => api.get('/api/chat/suggestions', { params }),
  
  voteOnSuggestion: (suggestionId: number, voteType: string) =>
    api.post(`/api/chat/suggestions/${suggestionId}/vote`, { vote_type: voteType }),
  
  // Study Groups
  createStudyGroup: (data: any) => api.post('/api/chat/study-groups', data),
  
  getStudyGroups: (params?: {
    topic?: string;
    difficulty?: string;
    limit?: number;
    offset?: number;
  }) => api.get('/api/chat/study-groups', { params }),
  
  joinStudyGroup: (groupId: number) => api.post(`/api/chat/study-groups/${groupId}/join`),
  
  // Notifications
  getNotifications: (params?: {
    limit?: number;
    offset?: number;
  }) => api.get('/api/chat/notifications', { params }),
  
  markNotificationRead: (notificationId: number) =>
    api.post(`/api/chat/notifications/${notificationId}/read`),
  
  // Statistics
  getChatStats: () => api.get('/api/chat/stats'),
  
  getRoomStats: (roomId: number) => api.get(`/api/chat/rooms/${roomId}/stats`),
};

// PDF Export API
export const exportAPI = {
  // Student Reports
  exportStudentReport: (userId: number, params?: {
    start_date?: string;
    end_date?: string;
  }) => api.get(`/api/export/student/${userId}`, { params }),
  
  // Class Reports
  exportClassReport: (userIds: number[], params?: {
    start_date?: string;
    end_date?: string;
  }) => api.post('/api/export/class', { user_ids: userIds, ...params }),
  
  // Quiz Analysis
  exportQuizAnalysis: (quizId: number) => api.get(`/api/export/quiz/${quizId}`),
  
  // Analytics Summary
  exportAnalyticsSummary: (params?: {
    start_date?: string;
    end_date?: string;
  }) => api.get('/api/export/analytics/summary', { params }),
  
  // Flashcard Deck
  exportFlashcardDeck: (deckId: number) => api.get(`/api/export/flashcards/${deckId}`),
  
  // Progress Timeline
  exportProgressTimeline: (days: number) => api.get('/api/export/progress/timeline', { params: { days } }),
  
  // Achievement Certificate
  exportCertificate: (achievementId: number) => api.get(`/api/export/certificate/${achievementId}`),
};

export default api; 