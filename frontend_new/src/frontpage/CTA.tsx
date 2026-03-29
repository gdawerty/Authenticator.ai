import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'

export function CTA() {
  const navigate = useNavigate()

  const handleGetStarted = () => {
    const token = localStorage.getItem('token')
    navigate(token ? '/app' : '/login')
  }

  return (
    <section className="py-32 px-8 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[800px] h-[400px] bg-[#6f8f88]/6 rounded-full blur-[120px]" />
      </div>

      {/* Top border line */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-px h-16 bg-gradient-to-b from-transparent to-[#6f8f88]/40" />

      <div className="max-w-[1280px] mx-auto relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="text-center max-w-3xl mx-auto"
        >
          {/* Eyebrow */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-[#6f8f88]/20 bg-[#6f8f88]/6 mb-8">
            <span className="w-1.5 h-1.5 bg-[#6f8f88] rounded-full animate-pulse" />
            <span className="text-[11px] font-mono tracking-[0.14em] text-[#6f8f88] uppercase">Get Started Today</span>
          </div>

          <h2 className="text-[52px] md:text-[68px] font-bold tracking-[-0.03em] text-[#1a1a1a] leading-[1.0] mb-6">
            Stop trusting.<br />
            <span className="text-[#6f8f88]">Start verifying.</span>
          </h2>

          <p className="text-[17px] text-[#6b6b6b] leading-relaxed mb-12 max-w-xl mx-auto">
            Every document that passes through your organization is a potential risk.
            Authentia makes verification instant, automated, and defensible.
          </p>

          {/* CTA buttons */}
          <div className="flex flex-wrap items-center justify-center gap-4 mb-14">
            <motion.button
              onClick={handleGetStarted}
              whileHover={{ scale: 1.03, y: -2 }}
              whileTap={{ scale: 0.97 }}
              className="inline-flex items-center gap-2.5 px-9 py-4 bg-[#6f8f88] text-[#09090b] rounded-xl font-semibold text-[15px] hover:bg-[#5c7a74] transition-colors shadow-[0_0_60px_rgba(127,200,192,0.3)]"
            >
              <span>Start for Free</span>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              className="inline-flex items-center gap-2 px-9 py-4 border border-black/15 text-[#52525b] rounded-xl font-medium text-[15px] hover:border-[#3a3a45] hover:text-[#1a1a1a] hover:bg-black/5 transition-all"
            >
              <span>Schedule a Demo</span>
            </motion.button>
          </div>

          {/* Social proof strip */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3, duration: 0.7 }}
            className="flex flex-col items-center gap-4"
          >
            <div className="flex items-center gap-2">
              {/* Avatars */}
              <div className="flex -space-x-2.5">
                {['#6f8f88', '#4d7d77', '#3d9990', '#6f8f88', '#4d7d77'].map((color, i) => (
                  <div
                    key={i}
                    className="w-8 h-8 rounded-full border-2 border-[#09090b] flex items-center justify-center text-[10px] font-bold text-white"
                    style={{ background: color, zIndex: 5 - i }}
                  >
                    {String.fromCharCode(65 + i)}
                  </div>
                ))}
              </div>
              <div className="text-left ml-2">
                <div className="text-[13px] font-medium text-[#1a1a1a]">Trusted by 2,400+ analysts</div>
                <div className="flex items-center gap-1 mt-0.5">
                  {[...Array(5)].map((_, i) => (
                    <svg key={i} className="w-3 h-3 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                  <span className="text-[11px] text-[#6b6b6b] ml-1">4.9 / 5 from 400+ reviews</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-6 text-[11px] text-[#52525b] font-mono mt-2">
              {['No credit card required', 'Cancel anytime', 'SOC 2 certified'].map((t) => (
                <div key={t} className="flex items-center gap-1.5">
                  <svg className="w-3 h-3 text-[#6f8f88]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                  {t}
                </div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
