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

const App: React.FC = () => {
  const navigate = useNavigate()
  const [showDemo, setShowDemo] = useState(false)
  const [showLogin, setShowLogin] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [apiMessage, setApiMessage] = useState<string>("")

  useEffect(() => {
    // Check for existing authentication
    const token = localStorage.getItem('authToken')
    const savedUser = localStorage.getItem('user')
    
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser))
      } catch (error) {
        // Clear invalid data
        localStorage.removeItem('authToken')
        localStorage.removeItem('user')
      }
    }

    // Handle dashboard navigation from hash (for backward compatibility)
    const hash = window.location.hash.substring(1)
    if (hash === 'dashboard' && user) {
      navigate('/dashboard')
      window.location.hash = ''
    }

    // Check for OAuth callback
    const urlParams = new URLSearchParams(window.location.search)
    const oauthToken = urlParams.get('token')
    const oauthUserId = urlParams.get('user')
    
    if (oauthToken && oauthUserId) {
      localStorage.setItem('authToken', oauthToken)
      // In a real app, you'd fetch user data with the token
      // For now, we'll use mock data
      const mockUser = { id: oauthUserId, name: 'OAuth User', email: 'user@example.com', role: 'user' }
      localStorage.setItem('user', JSON.stringify(mockUser))
      setUser(mockUser)
      
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname)
    }

    // Fetch from Flask backend
    fetch("/docs")
      .then(res => res.json())
      .then(data => setApiMessage(data.message))
      .catch(err => console.error("API fetch error:", err))

    // No cleanup needed for event listeners
  }, [])

  const handleLogin = (userData: any) => {
    setUser(userData)
    setShowLogin(false)
    // Stay on the same page - no redirect
  }

  const handleLogout = () => {
    localStorage.removeItem('authToken')
    localStorage.removeItem('user')
    setUser(null)
    navigate('/')
  }

  // Create a HomePage component for cleaner code
  const HomePage = () => (
    <div className="relative min-h-screen bg-charcoal-950 text-white overflow-x-hidden pt-20">
      {/* Background elements (lowest z-index) */}
      <BackgroundAnimation />

      {/* Main content container */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <Navigation
          onShowLogin={() => setShowLogin(true)}
          user={user}
          onLogout={handleLogout}
        />

        <main className="flex-1">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
            {/* Show API message above hero for testing */}
            {apiMessage && (
              <div className="mb-6 p-4 bg-green-800 rounded-md">
                Backend says: {apiMessage}
              </div>
            )}
            <HeroSection
              onShowDemo={() => setShowDemo(true)}
              onShowSignup={() => setShowLogin(true)}
            />
            <FeaturesSection />
            <APISection />
            <PricingSection />
            <ContactSection />
          </div>
        </main>

        <Footer />
      </div>

      {/* Modals (highest z-index) */}
      {showDemo && (
        <DemoModal
          onClose={() => setShowDemo(false)}
        />
      )}
      {showLogin && (
        <LoginModal
          onClose={() => setShowLogin(false)}
          onLogin={handleLogin}
        />
      )}
    </div>
  )

  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route
        path="/dashboard"
        element={
          user ? (
            user.role === 'admin' ? (
              <AdminDashboard user={user} onLogout={handleLogout} />
            ) : (
              <UserDashboard user={user} onLogout={handleLogout} />
            )
          ) : (
            <HomePage />
          )
        }
      />
    </Routes>
  )
}

export default App
