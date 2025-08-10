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

const App: React.FC = () => {
  const [showDemo, setShowDemo] = useState(false)
  const [apiMessage, setApiMessage] = useState<string>("")

  useEffect(() => {
    // Fetch from Flask backend
    fetch("/api/hello")
      .then(res => res.json())
      .then(data => setApiMessage(data.message))
      .catch(err => console.error("API fetch error:", err))
  }, [])

  return (
    <div className="relative min-h-screen bg-charcoal-950 text-white overflow-x-hidden">
      {/* Background elements (lowest z-index) */}
      <BackgroundAnimation />
      
      {/* Main content container */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <Navigation />
        
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
      
      {/* Modal (highest z-index) */}
      {showDemo && (
        <DemoModal 
          onClose={() => setShowDemo(false)} 
          className="fixed z-50"
        />
      )}
    </div>
  )
}

export default App
