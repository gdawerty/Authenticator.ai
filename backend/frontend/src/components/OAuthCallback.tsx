import React, { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

interface OAuthCallbackProps {
  onLogin: (user: any) => void;
}

const OAuthCallback = ({ onLogin }: OAuthCallbackProps) => {
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const access_token = searchParams.get('access_token');
    const refresh_token = searchParams.get('refresh_token');
    const error = searchParams.get('error');

    if (error) {
      console.error('OAuth error:', error);
      // Redirect to login page with error
      window.location.href = '/';
      return;
    }

    if (access_token && refresh_token) {
      // Store tokens
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      // Get user info
      fetch('http://localhost:5001/auth/me', {
        headers: {
          'Authorization': `Bearer ${access_token}`,
        },
      })
      .then(response => response.json())
      .then(data => {
        if (data.user) {
          onLogin(data.user);
        } else {
          window.location.href = '/';
        }
      })
      .catch(error => {
        console.error('Error fetching user:', error);
        window.location.href = '/';
      });
    } else {
      // No tokens, redirect to login
      window.location.href = '/';
    }
  }, [searchParams, onLogin]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-orange-900">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold text-white mb-2">Completing authentication...</h2>
        <p className="text-gray-400">Please wait while we sign you in.</p>
      </div>
    </div>
  );
};

export default OAuthCallback;
