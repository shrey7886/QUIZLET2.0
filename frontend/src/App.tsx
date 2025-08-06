import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Header from './components/Header';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import QuizDashboard from './components/QuizDashboard';
import QuizGenerator from './components/QuizGenerator';
import QuizInterface from './components/QuizInterface';
import ResultsPage from './components/ResultsPage';
import ChatbotInterface from './components/ChatbotInterface';
import FlashcardMode from './components/FlashcardMode';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Header />
          <Routes>
            <Route path="/login" element={<LoginForm />} />
            <Route path="/register" element={<RegisterForm />} />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <QuizDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/quiz-generator" 
              element={
                <ProtectedRoute>
                  <QuizGenerator />
                </ProtectedRoute>
              }
            />
            <Route 
              path="/quiz" 
              element={
                <ProtectedRoute>
                  <QuizInterface />
                </ProtectedRoute>
              }
            />
            <Route 
              path="/results" 
              element={
                <ProtectedRoute>
                  <ResultsPage />
                </ProtectedRoute>
              }
            />
            <Route 
              path="/chat" 
              element={
                <ProtectedRoute>
                  <ChatbotInterface />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/flashcards" 
              element={
                <ProtectedRoute>
                  <FlashcardMode />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/analytics" 
              element={
                <ProtectedRoute>
                  <AnalyticsDashboard />
                </ProtectedRoute>
              } 
            />
            <Route path="/" element={<LoginForm />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App; 