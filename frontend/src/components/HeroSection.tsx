import React from 'react'

interface HeroSectionProps {
  onShowDemo: () => void
}

const HeroSection: React.FC<HeroSectionProps> = ({ onShowDemo }) => {
  const showSignup = () => {
    alert('Sign up functionality would redirect to registration page')
  }

  const contentTypes = [
    {
      name: 'Text',
      icon: (
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
      )
    },
    {
      name: 'Image',
      icon: (
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
      )
    },
    {
      name: 'Audio',
      icon: (
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"></path>
        </svg>
      )
    },
    {
      name: 'Video',
      icon: (
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
        </svg>
      )
    }
  ]

  return (
    <section className="min-h-screen flex items-center justify-center relative pt-20 z-10">
      <div className="max-w-4xl mx-auto px-8 text-center relative z-10">
        <div className="space-y-16">
          <div className="space-y-8">
            <h1 className="text-5xl md:text-7xl font-bold text-white leading-tight tracking-tight">
              Detect AI-Generated<br />Content
            </h1>
            <p className="text-xl md:text-2xl text-charcoal-300 max-w-2xl mx-auto leading-relaxed font-light">
              Enterprise-grade detection platform for text, images, audio, and video content with precise confidence scoring.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
            <button 
              onClick={onShowDemo}
              className="bg-white text-black px-8 py-4 rounded-lg hover:bg-charcoal-100 transition-all duration-300 font-semibold hover-lift"
            >
              Try Demo
            </button>
            <button 
              onClick={showSignup}
              className="border border-charcoal-600 text-white px-8 py-4 rounded-lg hover:border-white hover:bg-white hover:text-black transition-all duration-300 font-semibold hover-lift"
            >
              Sign Up Free
            </button>
          </div>
          
          {/* Content Type Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl mx-auto pt-8">
            {contentTypes.map((type, index) => (
              <div 
                key={index}
                className="glass-minimal rounded-xl p-6 hover:bg-white/5 transition-all duration-300 cursor-pointer hover-lift group"
              >
                <div className="text-center space-y-3">
                  <div className="w-12 h-12 mx-auto bg-white/10 rounded-lg flex items-center justify-center group-hover:bg-white/20 transition-colors duration-300">
                    {type.icon}
                  </div>
                  <p className="text-sm font-medium text-white">{type.name}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

export default HeroSection