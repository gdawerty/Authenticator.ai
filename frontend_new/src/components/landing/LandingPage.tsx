import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Hero } from './Hero'
import { ProductPreview } from './ProductPreview'
import { Features } from './Features'
import { HowItWorks } from './HowItWorks'
import { Footer } from './Footer'
import { ThemeToggle } from '../ThemeToggle'

export function LandingPage() {
  return (
    <div className="min-h-screen bg-[#C8C8BF] dark:bg-[#1a1a1a] text-[#1A1A1A] dark:text-[#e5e5e5] transition-colors duration-300">
      <Navbar />
      <Hero />
      <ProductPreview />
      <HowItWorks />
      <Features />
      <CTA />
      <Footer />
    </div>
  )
}

function Navbar() {
  const navigate = useNavigate()

  const handleGetStarted = () => {
    const token = localStorage.getItem('token')
    navigate(token ? '/app' : '/login')
  }

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="fixed top-0 left-0 right-0 z-50 py-4 px-6 bg-[#C8C8BF]/80 dark:bg-[#1a1a1a]/80 backdrop-blur-lg border-b border-black/10 dark:border-white/10 transition-colors duration-300"
    >
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <a href="/" className="flex items-center gap-2 group">
          <div className="w-10 h-10 rounded-xl bg-[#6f8f88] flex items-center justify-center group-hover:scale-105 transition-transform">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <span className="font-semibold text-lg dark:text-white">Authentia</span>
        </a>

        {/* Nav Links */}
        <div className="hidden md:flex items-center gap-8">
          <a href="#product-preview" className="text-sm text-[#2a2a2a]/70 dark:text-white/70 hover:text-[#1A1A1A] dark:hover:text-white transition-colors">Product</a>
          <a href="#how-it-works" className="text-sm text-[#2a2a2a]/70 dark:text-white/70 hover:text-[#1A1A1A] dark:hover:text-white transition-colors">How It Works</a>
          <a href="#features" className="text-sm text-[#2a2a2a]/70 dark:text-white/70 hover:text-[#1A1A1A] dark:hover:text-white transition-colors">Features</a>
        </div>

        {/* Right Side */}
        <div className="flex items-center gap-3">
          <ThemeToggle />
          <motion.button
            onClick={handleGetStarted}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#6f8f88] text-white rounded-lg font-medium text-sm hover:bg-[#5a7a73] transition-colors"
          >
            <span>Get Started</span>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </motion.button>
        </div>
      </div>
    </motion.nav>
  )
}

function CTA() {
  const navigate = useNavigate()

  const handleGetStarted = () => {
    const token = localStorage.getItem('token')
    navigate(token ? '/app' : '/login')
  }

  return (
    <section className="py-24 px-6 border-t border-black/10 dark:border-white/10">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="relative rounded-3xl overflow-hidden"
        >
          {/* Background */}
          <div className="absolute inset-0 bg-gradient-to-br from-[#6f8f88] to-[#5a7a73]" />

          {/* Pattern Overlay */}
          <div
            className="absolute inset-0 opacity-10"
            style={{
              backgroundImage: `
                radial-gradient(circle at 20% 50%, rgba(255,255,255,0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 50%, rgba(255,255,255,0.2) 0%, transparent 40%)
              `
            }}
          />

          {/* Content */}
          <div className="relative z-10 p-12 md:p-16 text-center">
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/30 backdrop-blur-sm text-[#1a1a1a]/80 dark:text-white/90 text-sm font-medium mb-8"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
              <span>Beta Access Live</span>
            </motion.div>

            {/* Headline */}
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="text-4xl md:text-5xl lg:text-6xl font-semibold text-[#1a1a1a] dark:text-white mb-6 leading-tight"
              style={{ fontFamily: 'Georgia, serif' }}
            >
              Ready to Verify<br />Document Integrity?
            </motion.h2>

            {/* Subtext */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="text-xl text-[#1a1a1a]/70 dark:text-white/80 mb-10 max-w-xl mx-auto"
            >
              Join the beta and be among the first to experience enterprise-grade document forensics.
            </motion.p>

            {/* CTA Button */}
            <motion.button
              onClick={handleGetStarted}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5 }}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              className="group inline-flex items-center gap-3 px-8 py-4 bg-white text-[#6f8f88] rounded-xl font-medium text-lg shadow-lg hover:shadow-xl transition-all duration-300"
            >
              <span>Start Free Beta</span>
              <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </motion.button>

            {/* Trust Note */}
            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.7 }}
              className="mt-8 text-sm text-[#1a1a1a]/50 dark:text-white/60"
            >
              No credit card required. Free during beta.
            </motion.p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
