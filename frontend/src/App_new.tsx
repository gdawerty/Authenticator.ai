import React, { useState, useEffect } from 'react';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import './App.css';

interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing auth token
    const token = localStorage.getItem('auth_token');
    if (token) {
      // Simulate token validation
      setTimeout(() => {
        setUser({
          id: '1',
          name: 'Pratham Saurabh',
          email: 'pratham@authenticator.ai'
        });
        setIsLoading(false);
      }, 1000);
    } else {
      setIsLoading(false);
    }
  }, []);

  const handleLogin = async (email: string, password: string) => {
    // Simulate login API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // For demo purposes, accept any credentials
    const mockUser: User = {
      id: '1',
      name: email.split('@')[0].replace(/[^a-zA-Z]/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      email: email
    };
    
    localStorage.setItem('auth_token', 'mock-jwt-token');
    setUser(mockUser);
  };

  const handleSignup = () => {
    // For now, just switch to login with a message
    alert('Sign up functionality coming soon! For demo, use any email/password to login.');
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-amber-500 rounded-xl flex items-center justify-center mx-auto mb-4">
            <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          </div>
          <p className="text-gray-400">Loading Authenticator.ai...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      {user ? (
        <Dashboard user={user} onLogout={handleLogout} />
      ) : (
        <LoginPage onLogin={handleLogin} onSignup={handleSignup} />
      )}
    </div>
  );
}

export default App;
