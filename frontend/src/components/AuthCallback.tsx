import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const AuthCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (token) {
      // Store the token and redirect to dashboard
      localStorage.setItem('token', token);
      
      // You can also decode the token to get user info
      try {
        // For now, just redirect to dashboard
        // In a real app, you might want to decode the JWT and set user info
        navigate('/dashboard');
      } catch (err) {
        setError('Failed to process authentication');
        setTimeout(() => navigate('/login'), 3000);
      }
    } else {
      setError('No authentication token received');
      setTimeout(() => navigate('/login'), 3000);
    }
  }, [searchParams, navigate, login]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <div className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mb-6">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          
          {error ? (
            <>
              <h2 className="text-2xl font-bold text-red-600 mb-4">Authentication Failed</h2>
              <p className="text-slate-600 mb-4">{error}</p>
              <p className="text-sm text-slate-500">Redirecting to login...</p>
            </>
          ) : (
            <>
              <h2 className="text-2xl font-bold text-slate-900 mb-4">Authenticating...</h2>
              <div className="flex justify-center">
                <div className="spinner w-8 h-8"></div>
              </div>
              <p className="text-slate-600 mt-4">Please wait while we complete your sign-in.</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthCallback; 