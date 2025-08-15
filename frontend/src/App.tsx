import React, { useState, useEffect } from 'react'
import BackgroundAnimation from './components/BackgroundAnimation'
import Navigation from './components/Navigation'
import HeroSection from './components/HeroSection'
import FeaturesSection from './components/FeaturesSection'
import APISection from './components/APISection'
import PricingSection from './components/PricingSection'
import ContactSection from './components/ContactSection'
import Footer from './components/Footer'
import DemoModal from './components/DemoModal'
import LoginModal from './components/LoginModal'
import UserDashboard from './components/UserDashboard'
import AdminDashboard from './components/AdminDashboard'

const App: React.FC = () => {
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
  }, [])

  const handleLogin = (userData: any) => {
    setUser(userData)
    setShowLogin(false)
  }

  const handleLogout = () => {
    localStorage.removeItem('authToken')
    localStorage.removeItem('user')
    setUser(null)
  }

  // If user is logged in, show appropriate dashboard
  if (user) {
    if (user.role === 'admin') {
      return <AdminDashboard user={user} onLogout={handleLogout} />
    } else {
      return <UserDashboard user={user} onLogout={handleLogout} />
    }
  }

  return (
    <div className="relative min-h-screen bg-charcoal-950 text-white overflow-x-hidden">
      {/* Background elements (lowest z-index) */}
      <BackgroundAnimation />
      
      {/* Main content container */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <Navigation onShowLogin={() => setShowLogin(true)} />
        
        <main className="flex-1">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
            {/* Show API message above hero for testing */}
            {apiMessage && (
              <div className="mb-6 p-4 bg-green-800 rounded-md">
                Backend says: {apiMessage}
              </div>
            )}
            <HeroSection onShowDemo={() => setShowDemo(true)} />
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
}

export default App
