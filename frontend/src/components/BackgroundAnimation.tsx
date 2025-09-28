import React from 'react';

const BackgroundAnimation: React.FC = () => {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
      {/* Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-charcoal-950 via-charcoal-900 to-charcoal-950" />
      
      {/* Floating Elements */}
      <div className="absolute inset-0">
        {/* Dots */}
        <div className="absolute w-2 h-2 rounded-full bg-white/20 animate-float-dot-1 left-[20%] top-[30%]" />
        <div className="absolute w-2 h-2 rounded-full bg-white/20 animate-float-dot-2 left-[35%] top-[50%]" />
        <div className="absolute w-2 h-2 rounded-full bg-white/20 animate-float-dot-3 left-[50%] top-[70%]" />
        <div className="absolute w-2 h-2 rounded-full bg-white/20 animate-float-dot-1 animation-delay-2000 left-[65%] top-[30%]" />
        <div className="absolute w-2 h-2 rounded-full bg-white/20 animate-float-dot-2 animation-delay-2000 left-[80%] top-[50%]" />
        <div className="absolute w-2 h-2 rounded-full bg-white/20 animate-float-dot-3 animation-delay-2000 left-[95%] top-[70%]" />

        {/* Shapes */}
        <div className="absolute w-16 h-16 rounded-full border-2 border-white/10 animate-float-circle-1 left-[15%] top-[20%]" />
        <div className="absolute w-20 h-20 rounded-full border-2 border-white/10 animate-float-circle-2 left-[65%] top-[25%]" />
        
        {/* Square with rotation */}
        <div className="absolute w-12 h-12 border-2 border-white/10 animate-float-square-1 left-[75%] top-[60%] origin-center rotate-45" />
      </div>

      {/* Gradient Orbs */}
      <div className="absolute inset-0">
        <div className="absolute w-[500px] h-[500px] rounded-full bg-gradient-to-br from-blue-500/20 via-purple-500/20 to-emerald-500/20 opacity-30 blur-3xl -left-[10%] -top-[10%] animate-pulse-orb" />
        <div className="absolute w-[600px] h-[600px] rounded-full bg-gradient-to-br from-emerald-500/20 via-blue-500/20 to-purple-500/20 opacity-20 blur-3xl -right-[15%] -bottom-[20%] animate-pulse-orb animation-delay-2000" />
      </div>
    </div>
  );
};

export default BackgroundAnimation;