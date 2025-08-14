import React, { useState } from 'react'

const Navigation: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen)
  }

  return (
    <>
      <nav className="fixed top-0 w-full z-50 glass-minimal">
        <div className="max-w-6xl mx-auto px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center space-x-3">
              <div className="w-7 h-7 bg-white rounded-lg flex items-center justify-center">
                <span className="text-black font-semibold text-sm">A</span>
              </div>
              <span className="text-xl font-semibold text-white">Authentia</span>
            </div>
            <div className="hidden md:flex items-center space-x-12">
                <a href="#features" className="text-charcoal-300 hover:text-white transition-colors duration-300 font-medium">Features</a>
                <a href="#api" className="text-charcoal-300 hover:text-white transition-colors duration-300 font-medium">API</a>
                <a href="#pricing" className="text-charcoal-300 hover:text-white transition-colors duration-300 font-medium">Pricing</a>
                <a href="#documents" className="text-charcoal-300 hover:text-white transition-colors duration-300 font-medium">Documents</a>
              <button className="bg-white text-black px-6 py-2.5 rounded-lg hover:bg-charcoal-100 transition-all duration-300 font-medium hover-lift">
                Sign In
              </button>
            </div>
            <button 
              className="md:hidden text-white" 
              onClick={toggleMobileMenu}
              aria-label="Toggle mobile menu"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path>
              </svg>
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Menu */}
      <div 
        id="mobileMenu" 
        className={`fixed inset-0 z-40 bg-charcoal-950 bg-opacity-98 ${mobileMenuOpen ? 'flex' : 'hidden'} flex-col items-center justify-center`}
      >
        <div className="flex flex-col items-center justify-center h-full space-y-12">
          <a 
            href="#features" 
            className="text-xl text-charcoal-300 hover:text-white transition-colors duration-300 font-medium"
            onClick={toggleMobileMenu}
          >
            Features
          </a>
          <a 
            href="#api" 
            className="text-xl text-charcoal-300 hover:text-white transition-colors duration-300 font-medium"
            onClick={toggleMobileMenu}
          >
            API
          </a>
          <a 
            href="#pricing" 
            className="text-xl text-charcoal-300 hover:text-white transition-colors duration-300 font-medium"
            onClick={toggleMobileMenu}
          >
            Pricing
          </a>
          <a 
            href="#documents" 
            className="text-xl text-charcoal-300 hover:text-white transition-colors duration-300 font-medium"
            onClick={toggleMobileMenu}
          >
            Documents
          </a>
          <button className="bg-white text-black px-8 py-3 rounded-lg hover:bg-charcoal-100 transition-all duration-300 font-medium hover-lift">
            Sign In
          </button>
        </div>
      </div>
    </>
  )
}

export default Navigation