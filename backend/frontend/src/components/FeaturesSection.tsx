import React from 'react'

const FeaturesSection: React.FC = () => {
  const features = [
    {
      title: "Text Analysis",
      description: "Advanced authenticity verification for written content using perplexity analysis and watermarking detection.",
      icon: (
        <svg className="w-8 h-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
      )
    },
    {
      title: "Document Verification",
      description: "Comprehensive document authenticity analysis with pattern recognition and metadata verification.",
      icon: (
        <svg className="w-8 h-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 12H8m8 4H8m4-8H8"></path>
        </svg>
      )
    },
    {
      title: "Image Verification",
      description: "Sophisticated deepfake and manipulation detection with pixel-level authenticity analysis.",
      icon: (
        <svg className="w-8 h-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
      )
    },
    {
      title: "Audio Verification",
      description: "Voice authenticity verification and synthetic audio detection with spectral analysis.",
      icon: (
        <svg className="w-8 h-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"></path>
        </svg>
      )
    },
    {
      title: "Video Verification",
      description: "Comprehensive video authenticity analysis and synthetic content identification.",
      icon: (
        <svg className="w-8 h-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
        </svg>
      )
    }
  ]

  return (
    <section id="features" className="py-32 relative z-10" style={{ background: 'linear-gradient(180deg, #1a1a1a 0%, #222222 100%)' }}>
      <div className="max-w-6xl mx-auto px-8">
        <div className="text-center mb-24">
          <h2 className="text-4xl md:text-5xl font-bold mb-8 text-white">Authenticity Verification</h2>
          <p className="text-xl text-charcoal-300 max-w-2xl mx-auto font-light">
            Comprehensive AI-powered authenticity verification for any type of content across all media formats and platforms.
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="space-y-6 hover-lift">
              <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center">
                {feature.icon}
              </div>
              <div className="space-y-3">
                <h3 className="text-xl font-semibold text-white">{feature.title}</h3>
                <p className="text-charcoal-300 leading-relaxed">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default FeaturesSection