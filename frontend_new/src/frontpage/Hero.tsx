import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'

const scanResults = [
  { label: 'Digital Signature', status: 'verified', delay: 1.2 },
  { label: 'Metadata Integrity', status: 'clean', delay: 1.7 },
  { label: 'AI Semantic Check', status: 'running', delay: 2.2 },
  { label: 'Authentia Score', status: 'score', delay: 2.8 },
]

function ScanCard() {
  const [step, setStep] = useState(0)

  useEffect(() => {
    const timers = scanResults.map((r, i) =>
      setTimeout(() => setStep(i + 1), r.delay * 1000)
    )
    return () => timers.forEach(clearTimeout)
  }, [])

  return (
    <div className="relative">
      {/* Corner brackets — Vast Space style */}
      <div className="absolute -top-2 -left-2 w-5 h-5 border-t-2 border-l-2 border-[#6f8f88]/60" />
      <div className="absolute -top-2 -right-2 w-5 h-5 border-t-2 border-r-2 border-[#6f8f88]/60" />
      <div className="absolute -bottom-2 -left-2 w-5 h-5 border-b-2 border-l-2 border-[#6f8f88]/60" />
      <div className="absolute -bottom-2 -right-2 w-5 h-5 border-b-2 border-r-2 border-[#6f8f88]/60" />

      <div className="bg-[#111115] border border-black/10 rounded-2xl overflow-hidden w-[360px]">
        {/* Card header */}
        <div className="flex items-center gap-2 px-4 py-3 border-b border-black/10">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f57]" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#febc2e]" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#28c840]" />
          </div>
          <span className="text-[11px] font-mono text-[#6b6b6b] ml-1">authentia — forensic scan</span>
        </div>

        {/* Document being scanned */}
        <div className="p-4 border-b border-black/10">
          <div className="flex items-center gap-3 p-3 bg-[#C8C8BF] rounded-xl border border-black/10">
            <div className="w-9 h-11 rounded-md bg-[#1c1c22] border border-[#2a2a32] flex items-center justify-center flex-shrink-0 relative overflow-hidden">
              <span className="text-[9px] font-mono text-[#6b6b6b]">PDF</span>
              {/* Scan line animation */}
              <motion.div
                className="absolute inset-x-0 h-[1px] bg-[#6f8f88]/60"
                animate={{ top: ['0%', '100%'] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
              />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[12px] text-[#1a1a1a] font-medium truncate">employment_contract.pdf</p>
              <p className="text-[10px] text-[#6b6b6b] mt-0.5">2.4 MB · Uploaded just now</p>
            </div>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }}
              className="w-4 h-4 rounded-full border-2 border-[#6f8f88] border-t-transparent flex-shrink-0"
            />
          </div>
        </div>

        {/* Scan results */}
        <div className="p-4 space-y-2.5">
          <AnimatePresence>
            {scanResults.slice(0, step).map((r) => (
              <motion.div
                key={r.label}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                className="flex items-center justify-between"
              >
                <span className="text-[11px] text-[#52525b] font-mono">{r.label}</span>
                {r.status === 'score' ? (
                  <span className="text-[11px] font-bold text-[#6f8f88] bg-[#6f8f88]/10 px-2 py-0.5 rounded-full">
                    98.7 / 100
                  </span>
                ) : r.status === 'running' ? (
                  <div className="flex items-center gap-1.5">
                    <motion.div
                      className="w-1 h-1 bg-[#6f8f88] rounded-full"
                      animate={{ opacity: [1, 0, 1] }}
                      transition={{ duration: 0.8, repeat: Infinity, delay: 0 }}
                    />
                    <motion.div
                      className="w-1 h-1 bg-[#6f8f88] rounded-full"
                      animate={{ opacity: [1, 0, 1] }}
                      transition={{ duration: 0.8, repeat: Infinity, delay: 0.2 }}
                    />
                    <motion.div
                      className="w-1 h-1 bg-[#6f8f88] rounded-full"
                      animate={{ opacity: [1, 0, 1] }}
                      transition={{ duration: 0.8, repeat: Infinity, delay: 0.4 }}
                    />
                  </div>
                ) : (
                  <span className="text-[11px] text-emerald-400 flex items-center gap-1">
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                    </svg>
                    {r.status}
                  </span>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Progress bar */}
          <div className="mt-3 pt-3 border-t border-black/10">
            <div className="flex justify-between mb-1.5">
              <span className="text-[10px] font-mono text-[#6b6b6b]">Analysis progress</span>
              <span className="text-[10px] font-mono text-[#6f8f88]">{Math.round((step / scanResults.length) * 100)}%</span>
            </div>
            <div className="h-0.5 bg-[#1c1c22] rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-[#6f8f88] to-[#4d7d77] rounded-full"
                animate={{ width: `${(step / scanResults.length) * 100}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export function Hero() {
  const navigate = useNavigate()

  const handleGetStarted = () => {
    const token = localStorage.getItem('token')
    navigate(token ? '/app' : '/login')
  }

  return (
    <section className="relative min-h-screen flex items-center pt-24 pb-20 px-8 overflow-hidden">
      {/* Background texture — dot grid */}
      <div
        className="absolute inset-0 opacity-[0.18]"
        style={{
          backgroundImage: `radial-gradient(circle, #2a2a35 1px, transparent 1px)`,
          backgroundSize: '28px 28px',
        }}
      />

      {/* Ambient glow */}
      <div className="absolute top-1/3 left-1/4 w-[600px] h-[600px] bg-[#6f8f88]/8 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-[#6f8f88]/5 rounded-full blur-[100px] pointer-events-none" />

      <div className="relative z-10 max-w-[1280px] mx-auto w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">

          {/* Left — Text */}
          <div>
            {/* Eyebrow */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="flex items-center gap-3 mb-8"
            >
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-[#6f8f88]/25 bg-[#6f8f88]/8">
                <span className="w-1.5 h-1.5 bg-[#6f8f88] rounded-full animate-pulse" />
                <span className="text-[11px] font-mono tracking-[0.12em] text-[#6f8f88] uppercase">Forensic Intelligence Platform</span>
              </div>
            </motion.div>

            {/* Headline — massive, left-aligned, Vast Space scale */}
            <div className="mb-8 overflow-hidden">
              <motion.h1
                initial={{ y: '100%', opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.8, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
                className="text-[64px] md:text-[80px] lg:text-[88px] font-bold leading-[0.95] tracking-[-0.03em] text-[#1a1a1a]"
              >
                Document
              </motion.h1>
              <motion.h1
                initial={{ y: '100%', opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.8, delay: 0.18, ease: [0.22, 1, 0.36, 1] }}
                className="text-[64px] md:text-[80px] lg:text-[88px] font-bold leading-[0.95] tracking-[-0.03em] text-[#6f8f88]"
              >
                Fraud
              </motion.h1>
              <motion.h1
                initial={{ y: '100%', opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.8, delay: 0.26, ease: [0.22, 1, 0.36, 1] }}
                className="text-[64px] md:text-[80px] lg:text-[88px] font-bold leading-[0.95] tracking-[-0.03em] text-[#1a1a1a]"
              >
                Detected.
              </motion.h1>
            </div>

            {/* Subtext */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.55 }}
              className="text-[17px] text-[#6b6b6b] leading-relaxed max-w-md mb-10"
            >
              Authentia combines forensic metadata analysis, AI content verification, and
              explainable scoring to catch document fraud before it costs you.
            </motion.p>

            {/* CTAs */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.7 }}
              className="flex flex-wrap items-center gap-4"
            >
              <motion.button
                onClick={handleGetStarted}
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.97 }}
                className="inline-flex items-center gap-2.5 px-7 py-3.5 bg-[#6f8f88] text-[#09090b] rounded-xl font-semibold text-[15px] hover:bg-[#5c7a74] transition-colors shadow-[0_0_40px_rgba(127,200,192,0.25)]"
              >
                <span>Start Free</span>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </motion.button>

              <motion.button
                onClick={() => {}}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.97 }}
                className="inline-flex items-center gap-2.5 px-7 py-3.5 border border-[#2a2a32] text-[#52525b] rounded-xl font-medium text-[15px] hover:border-[#3a3a45] hover:text-[#1a1a1a] hover:bg-[#111115] transition-all"
              >
                <svg className="w-4 h-4 text-[#6f8f88]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Watch Demo</span>
              </motion.button>
            </motion.div>

            {/* Trust badges */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 1.0 }}
              className="flex items-center gap-5 mt-10 text-[12px] text-[#52525b]"
            >
              {['SOC 2 Compliant', '256-bit Encryption', 'GDPR Ready'].map((badge) => (
                <div key={badge} className="flex items-center gap-1.5">
                  <svg className="w-3 h-3 text-[#6f8f88]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>{badge}</span>
                </div>
              ))}
            </motion.div>
          </div>

          {/* Right — Animated Scan Card */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.9, delay: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className="flex justify-center lg:justify-end"
          >
            <ScanCard />
          </motion.div>
        </div>
      </div>
    </section>
  )
}
