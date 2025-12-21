import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface HomepageProps {
  onRequestDemo?: () => void;
  onLogin?: () => void;
}

const Homepage: React.FC<HomepageProps> = ({ onRequestDemo, onLogin }) => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      // Trigger when scrolled past 70% of viewport height
      const scrollY = window.scrollY;
      const viewportHeight = window.innerHeight;
      const threshold = viewportHeight * 0.7;
      const isScrolled = scrollY > threshold;

      console.log('Scroll Y:', scrollY, 'Threshold:', threshold, 'Scrolled:', isScrolled);
      setScrolled(isScrolled);
    };

    // Check scroll position on mount
    handleScroll();

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = (e: React.MouseEvent) => {
    e.preventDefault();
    console.log('Scrolling to top');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#C8C8BF]">
      {/* Animated Navigation Bar */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-[#C8C8BF]/98 backdrop-blur-xl border-b border-[#6F8F88]/30 py-4 shadow-sm'
          : 'bg-[#C8C8BF]/95 backdrop-blur-md py-6'
      }`}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center">
            {/* Animated Logo */}
            <div
              className="flex items-center space-x-3 cursor-pointer"
              onClick={scrollToTop}
            >
              <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-amber-500 rounded-lg flex items-center justify-center shadow-lg">
                <span className="text-xl">🛡️</span>
              </div>
              <span className="text-2xl font-bold text-[#2a2a2a]">Authentia AI</span>
            </div>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-8">
              <a
                href="#product"
                className="text-[#2a2a2a]/70 hover:text-[#2a2a2a] transition-colors duration-200 font-medium"
              >
                Product
              </a>
              <a
                href="#about"
                className="text-[#2a2a2a]/70 hover:text-[#2a2a2a] transition-colors duration-200 font-medium"
              >
                About us
              </a>
              <a
                href="#faq"
                className="text-[#2a2a2a]/70 hover:text-[#2a2a2a] transition-colors duration-200 font-medium"
              >
                FAQ
              </a>
              <button
                onClick={onLogin}
                className="text-[#2a2a2a]/70 hover:text-[#2a2a2a] transition-colors duration-200 font-medium flex items-center space-x-1"
              >
                <span>Login</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path>
                </svg>
              </button>
              <button
                onClick={onRequestDemo}
                className="bg-[#6F8F88] text-white px-6 py-2.5 rounded-lg font-medium hover:shadow-lg hover:shadow-[#6F8F88]/50 transition-all duration-300 hover:-translate-y-0.5 flex items-center space-x-2"
              >
                <span>Request a demo</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path>
                </svg>
              </button>
            </div>

            {/* Mobile Menu Button */}
            <button className="md:hidden text-[#2a2a2a]">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path>
              </svg>
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="min-h-screen flex items-center justify-center px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-6xl font-bold text-[#2a2a2a] mb-6">
            Welcome to Authentia AI
          </h1>
          <p className="text-xl text-[#2a2a2a]/70">
            AI-powered document authenticity verification
          </p>
        </div>
      </div>

      {/* Product Section */}
      <div id="product" className="min-h-screen flex items-center justify-center px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl font-bold text-[#2a2a2a] mb-6">Product</h2>
          <p className="text-xl text-[#2a2a2a]/70">Product section coming soon...</p>
        </div>
      </div>

      {/* About Us Section */}
      <div id="about" className="min-h-screen flex items-center justify-center px-6 bg-[#b8b8af]">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl font-bold text-[#2a2a2a] mb-6">About Us</h2>
          <p className="text-xl text-[#2a2a2a]/70">About us section coming soon...</p>
        </div>
      </div>

      {/* FAQ Section */}
      <div id="faq" className="min-h-screen flex items-center justify-center px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl font-bold text-[#2a2a2a] mb-6">FAQ</h2>
          <p className="text-xl text-[#2a2a2a]/70">FAQ section coming soon...</p>
        </div>
      </div>
    </div>
  );
};

export default Homepage;
