import React from 'react'

const BackgroundAnimation: React.FC = () => (
  <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
    {/* Gradient Background */}
    <div className="absolute inset-0 bg-gradient-to-br from-charcoal-950 to-charcoal-900" />
    
    {/* Floating Dots */}
    <div className="absolute inset-0">
      <div className="floating-dot dot-1 animate-float-dot-1"></div>
      <div className="floating-dot dot-2 animate-float-dot-2"></div>
      <div className="floating-dot dot-3 animate-float-dot-3"></div>
      <div className="floating-dot dot-4 animate-float-dot-1 animation-delay-2000"></div>
      <div className="floating-dot dot-5 animate-float-dot-2"></div>
      <div className="floating-dot dot-6 animate-float-dot-3"></div>
    </div>
    
    {/* Geometric Shapes */}
    <div className="floating-shape shape-circle-1 animate-float-circle-1"></div>
    <div className="floating-shape shape-square-1 animate-float-square-1"></div>
    <div className="floating-shape shape-circle-2 animate-float-circle-1"></div>
    <div className="floating-shape shape-square-2 animate-float-square-1"></div>
    
    {/* Gradient Orbs */}
    <div className="gradient-orb orb-1 animate-pulse-orb"></div>
    <div className="gradient-orb orb-2 animate-pulse-orb animation-delay-2000"></div>
  </div>
)

export default BackgroundAnimation