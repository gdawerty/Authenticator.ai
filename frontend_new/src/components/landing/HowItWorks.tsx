import { motion } from 'framer-motion'

const steps = [
  {
    id: 'ingestion',
    title: 'Ingestion',
    description: 'Supports PDF, DOCX, and images, processed via a forensic-ready OCR layer.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
    ),
  },
  {
    id: 'ocr',
    title: 'pytesseract OCR',
    description: 'Advanced optical character recognition extracts text with forensic precision.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
  },
  {
    id: 'forensic',
    title: 'Forensic Metadata',
    description: 'Scans metadata, digital signatures, and image forensics for manipulation artifacts.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
      </svg>
    ),
  },
  {
    id: 'content',
    title: 'Mistral Content Analysis',
    description: 'LLM performs semantic logic checks, summarizing intent and flagging inconsistencies.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
  },
  {
    id: 'score',
    title: 'The Authentia Score',
    description: 'A weighted combination of forensic flags and content breakdowns with explainable AI.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
  },
]

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 px-6 border-t border-black/10 dark:border-white/10">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="text-[#6f8f88] font-mono text-sm tracking-wider mb-4 block">
            HOW IT WORKS
          </span>
          <h2 className="text-4xl md:text-5xl font-semibold mb-6 dark:text-white" style={{ fontFamily: 'Georgia, serif' }}>
            Technical Architecture
          </h2>
          <p className="text-[#2a2a2a]/70 dark:text-white/70 text-lg max-w-2xl mx-auto">
            A sophisticated pipeline combining forensic analysis with AI-powered content verification.
          </p>
        </motion.div>

        {/* Architecture Diagram */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="relative"
        >
          {/* Main Flow Container */}
          <div className="relative backdrop-blur-xl bg-white/40 dark:bg-white/5 rounded-3xl border border-black/10 dark:border-white/10 p-8 md:p-12 overflow-hidden">
            {/* Background Grid Pattern */}
            <div
              className="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]"
              style={{
                backgroundImage: `
                  linear-gradient(rgba(0,0,0,0.3) 1px, transparent 1px),
                  linear-gradient(90deg, rgba(0,0,0,0.3) 1px, transparent 1px)
                `,
                backgroundSize: '40px 40px'
              }}
            />

            {/* Glow Effects */}
            <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-[#6f8f88]/20 rounded-full blur-[100px] pointer-events-none" />
            <div className="absolute bottom-1/4 right-1/4 w-48 h-48 bg-[#6f8f88]/15 rounded-full blur-[80px] pointer-events-none" />

            {/* Flow Diagram */}
            <div className="relative z-10">
              {/* Document Input Node */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2 }}
                className="flex justify-center mb-8"
              >
                <div className="relative">
                  <div className="px-8 py-4 rounded-2xl backdrop-blur-md bg-white/60 dark:bg-white/10 border border-black/10 dark:border-white/20 shadow-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-[#6f8f88]/20 dark:bg-[#6f8f88]/30 flex items-center justify-center">
                        <svg className="w-6 h-6 text-[#6f8f88]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <div>
                        <p className="font-semibold text-[#1A1A1A] dark:text-white">Document Input</p>
                        <p className="text-sm text-[#2a2a2a]/60 dark:text-white/60">PDF, DOCX, Images</p>
                      </div>
                    </div>
                  </div>
                  {/* Animated Pulse Ring */}
                  <motion.div
                    className="absolute inset-0 rounded-2xl border-2 border-[#6f8f88]/50"
                    animate={{ scale: [1, 1.1, 1], opacity: [0.5, 0, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                </div>
              </motion.div>

              {/* Animated Connection Line */}
              <div className="flex justify-center mb-4">
                <motion.div
                  initial={{ height: 0 }}
                  whileInView={{ height: 40 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.4, duration: 0.5 }}
                  className="w-0.5 bg-gradient-to-b from-[#6f8f88] to-[#6f8f88]/30 relative"
                >
                  <motion.div
                    className="absolute top-0 left-1/2 -translate-x-1/2 w-2 h-2 bg-[#6f8f88] rounded-full"
                    animate={{ y: [0, 32, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  />
                </motion.div>
              </div>

              {/* OCR Layer */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.5 }}
                className="flex justify-center mb-8"
              >
                <div className="px-6 py-3 rounded-xl backdrop-blur-md bg-[#6f8f88]/10 dark:bg-[#6f8f88]/20 border border-[#6f8f88]/30 shadow-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-[#6f8f88] rounded-full animate-pulse" />
                    <span className="font-mono text-sm text-[#6f8f88] font-medium">pytesseract OCR</span>
                  </div>
                </div>
              </motion.div>

              {/* Split into Two Paths */}
              <div className="flex justify-center mb-4">
                <motion.svg
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.6 }}
                  width="200"
                  height="60"
                  viewBox="0 0 200 60"
                  className="overflow-visible"
                >
                  {/* Left Path */}
                  <motion.path
                    d="M100 0 L100 20 Q100 30 80 30 L40 30 Q20 30 20 40 L20 60"
                    fill="none"
                    stroke="url(#greenGradient)"
                    strokeWidth="2"
                    initial={{ pathLength: 0 }}
                    whileInView={{ pathLength: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.7, duration: 0.8 }}
                  />
                  {/* Right Path */}
                  <motion.path
                    d="M100 0 L100 20 Q100 30 120 30 L160 30 Q180 30 180 40 L180 60"
                    fill="none"
                    stroke="url(#greenGradient)"
                    strokeWidth="2"
                    initial={{ pathLength: 0 }}
                    whileInView={{ pathLength: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.7, duration: 0.8 }}
                  />
                  <defs>
                    <linearGradient id="greenGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#6f8f88" />
                      <stop offset="100%" stopColor="#6f8f88" stopOpacity="0.3" />
                    </linearGradient>
                  </defs>
                </motion.svg>
              </div>

              {/* Dual Path Processing */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                {/* Forensic Analysis Path */}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.8 }}
                  className="relative"
                >
                  <div className="p-6 rounded-2xl backdrop-blur-md bg-white/60 dark:bg-white/10 border border-black/10 dark:border-white/20 shadow-lg hover:shadow-xl transition-shadow">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-xl bg-[#6f8f88]/20 dark:bg-[#6f8f88]/30 flex items-center justify-center">
                        <svg className="w-5 h-5 text-[#6f8f88]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                        </svg>
                      </div>
                      <h3 className="font-semibold text-[#1A1A1A] dark:text-white">Forensic Analysis</h3>
                    </div>
                    <ul className="space-y-2 text-sm text-[#2a2a2a]/70 dark:text-white/70">
                      <li className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-[#6f8f88] rounded-full" />
                        Metadata extraction
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-[#6f8f88] rounded-full" />
                        Digital signature verification
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-[#6f8f88] rounded-full" />
                        Image forensics scan
                      </li>
                    </ul>
                  </div>
                  {/* Glowing Border Effect */}
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-[#6f8f88]/20 to-transparent -z-10 blur-xl" />
                </motion.div>

                {/* Content Analysis Path */}
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.9 }}
                  className="relative"
                >
                  <div className="p-6 rounded-2xl backdrop-blur-md bg-white/60 dark:bg-white/10 border border-black/10 dark:border-white/20 shadow-lg hover:shadow-xl transition-shadow">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-xl bg-[#6f8f88]/20 dark:bg-[#6f8f88]/30 flex items-center justify-center">
                        <svg className="w-5 h-5 text-[#6f8f88]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                      </div>
                      <h3 className="font-semibold text-[#1A1A1A] dark:text-white">Mistral Content Analysis</h3>
                    </div>
                    <ul className="space-y-2 text-sm text-[#2a2a2a]/70 dark:text-white/70">
                      <li className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-[#6f8f88] rounded-full" />
                        Semantic logic checks
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-[#6f8f88] rounded-full" />
                        Intent summarization
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-[#6f8f88] rounded-full" />
                        Inconsistency flagging
                      </li>
                    </ul>
                  </div>
                  {/* Glowing Border Effect */}
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-l from-[#6f8f88]/20 to-transparent -z-10 blur-xl" />
                </motion.div>
              </div>

              {/* Converging Lines */}
              <div className="flex justify-center mb-4">
                <motion.svg
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: 1 }}
                  width="200"
                  height="60"
                  viewBox="0 0 200 60"
                  className="overflow-visible"
                >
                  {/* Left Path Converging */}
                  <motion.path
                    d="M20 0 L20 20 Q20 30 40 30 L80 30 Q100 30 100 40 L100 60"
                    fill="none"
                    stroke="url(#greenGradient2)"
                    strokeWidth="2"
                    initial={{ pathLength: 0 }}
                    whileInView={{ pathLength: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 1.1, duration: 0.8 }}
                  />
                  {/* Right Path Converging */}
                  <motion.path
                    d="M180 0 L180 20 Q180 30 160 30 L120 30 Q100 30 100 40 L100 60"
                    fill="none"
                    stroke="url(#greenGradient2)"
                    strokeWidth="2"
                    initial={{ pathLength: 0 }}
                    whileInView={{ pathLength: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 1.1, duration: 0.8 }}
                  />
                  <defs>
                    <linearGradient id="greenGradient2" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#6f8f88" stopOpacity="0.3" />
                      <stop offset="100%" stopColor="#6f8f88" />
                    </linearGradient>
                  </defs>
                </motion.svg>
              </div>

              {/* Confidence Score Card */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8, y: 20 }}
                whileInView={{ opacity: 1, scale: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 1.2, type: "spring", stiffness: 100 }}
                className="flex justify-center"
              >
                <div className="relative">
                  <div className="px-10 py-6 rounded-2xl backdrop-blur-md bg-gradient-to-br from-[#6f8f88] to-[#5a7a73] border border-white/20 shadow-2xl">
                    <div className="flex items-center gap-4">
                      <div className="w-14 h-14 rounded-xl bg-white/20 flex items-center justify-center">
                        <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                      </div>
                      <div className="text-white">
                        <p className="text-sm text-white/70 font-medium">The Authentia Score</p>
                        <p className="text-3xl font-bold">98.7%</p>
                        <p className="text-xs text-white/60">Confidence Level</p>
                      </div>
                    </div>
                  </div>
                  {/* Glow Effect */}
                  <motion.div
                    className="absolute inset-0 rounded-2xl bg-[#6f8f88]/50 -z-10 blur-2xl"
                    animate={{ opacity: [0.5, 0.8, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                  {/* Animated Ring */}
                  <motion.div
                    className="absolute inset-0 rounded-2xl border-2 border-white/30"
                    animate={{ scale: [1, 1.05, 1], opacity: [0.3, 0, 0.3] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                </div>
              </motion.div>
            </div>
          </div>
        </motion.div>

        {/* Step Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
          className="mt-16 grid grid-cols-1 md:grid-cols-5 gap-4"
        >
          {steps.map((step, i) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 * i }}
              className="relative p-4 rounded-xl backdrop-blur-md bg-white/30 dark:bg-white/5 border border-black/10 dark:border-white/10 text-center group hover:bg-white/50 dark:hover:bg-white/10 transition-colors"
            >
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-6 h-6 rounded-full bg-[#6f8f88] text-white text-xs font-bold flex items-center justify-center">
                {i + 1}
              </div>
              <div className="w-10 h-10 mx-auto mt-2 rounded-lg bg-[#6f8f88]/10 dark:bg-[#6f8f88]/20 flex items-center justify-center text-[#6f8f88] group-hover:bg-[#6f8f88]/20 transition-colors">
                {step.icon}
              </div>
              <h4 className="font-semibold text-sm mt-3 mb-1 dark:text-white">{step.title}</h4>
              <p className="text-xs text-[#2a2a2a]/60 dark:text-white/60 leading-relaxed">{step.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
