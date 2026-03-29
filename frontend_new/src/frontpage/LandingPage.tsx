import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Hero } from './Hero'
import { Stats } from './Stats'
import { HowItWorks } from './HowItWorks'
import { Features } from './Features'
import { Bento } from './Bento'
import { CTA } from './CTA'
import { Footer } from './Footer'

function Navbar() {
  const navigate = useNavigate()
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const handleGetStarted = () => {
    const token = localStorage.getItem('token')
    navigate(token ? '/app' : '/login')
  }

  return (
    <motion.nav
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className={`fixed top-0 left-0 right-0 z-50 px-8 py-4 transition-all duration-300 ${
        scrolled
          ? 'bg-[#C8C8BF]/90 backdrop-blur-xl border-b border-black/10'
          : 'bg-transparent border-b border-transparent'
      }`}
    >
      <div className="max-w-[1280px] mx-auto flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-[#6f8f88] flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <span className="text-[15px] font-bold text-[#1a1a1a] tracking-[-0.02em]">Authentia</span>
        </div>

        {/* Nav links */}
        <div className="hidden md:flex items-center gap-1">
          {['Features', 'Pricing', 'Enterprise', 'Docs'].map((item) => (
            <button
              key={item}
              className="px-4 py-2 text-[13px] text-[#52525b] hover:text-[#1a1a1a] transition-colors rounded-lg hover:bg-black/5"
            >
              {item}
            </button>
          ))}
        </div>

        {/* Right CTAs */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleGetStarted}
            className="hidden md:block px-4 py-2 text-[13px] text-[#52525b] hover:text-[#1a1a1a] transition-colors"
          >
            Sign in
          </button>
          <motion.button
            onClick={handleGetStarted}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            className="px-4 py-2 bg-[#1a1a1a] text-white rounded-lg text-[13px] font-semibold hover:bg-[#2a2a2a] transition-colors"
          >
            Get Started
          </motion.button>
        </div>
      </div>
    </motion.nav>
  )
}

export function LandingPage() {
  return (
    <div className="min-h-screen bg-[#C8C8BF] text-[#1a1a1a]">
      <Navbar />
      <Hero />
      <Stats />
      <HowItWorks />
      <Features />
      <Bento />
      <CTA />
      <Footer />
    </div>
  )
}
