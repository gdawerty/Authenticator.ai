import { useState, useEffect } from 'react';
import Homepage from './components/Homepage';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import DemoRequestForm from './components/DemoRequestForm';
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
  const [showLogin, setShowLogin] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false);
  const [showDemoRequest, setShowDemoRequest] = useState(false);

  useEffect(() => {
    // Check for existing auth token
    const token = localStorage.getItem('access_token');
    if (token) {
      // Try to get user info from token or localStorage
      const userData = localStorage.getItem('user_data');
      if (userData) {
        try {
          setUser(JSON.parse(userData));
          setShowDashboard(true);
        } catch (error) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user_data');
        }
      }
    }
    setIsLoading(false);
  }, []);

  const handleLogin = (userData: any) => {
    // Store user data and tokens
    setUser({
      id: userData.id.toString(),
      name: userData.name,
      email: userData.email,
      avatar: userData.avatar_url
    });

    // Store user data for persistence
    localStorage.setItem('user_data', JSON.stringify(userData));
    setShowLogin(false);
    setShowDashboard(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    setUser(null);
    setShowDashboard(false);
  };

  const handleRequestDemo = () => {
    setShowDemoRequest(true);
  };

  const handleShowLogin = () => {
    setShowLogin(true);
  };

  const handleBackToHome = () => {
    setShowLogin(false);
    setShowDemoRequest(false);
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

  if (showDashboard && user) {
    return (
      <div className="App">
        <Dashboard user={user} onLogout={handleLogout} />
      </div>
    );
  }

  if (showDemoRequest) {
    return <DemoRequestForm onBack={handleBackToHome} />;
  }

  if (showLogin) {
    return (
      <div className="App">
        <LoginPage onLogin={handleLogin} onBack={handleBackToHome} />
      </div>
    );
  }

  return (
    <Homepage onRequestDemo={handleRequestDemo} onLogin={handleShowLogin} />
  );
}

export default App;
