import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

type PreviewState = 'upload' | 'analyzing' | 'results'

interface AnalysisResult {
  category: string
  status: 'clean' | 'warning' | 'flagged'
  confidence: number
  details: string
}

const mockResults: AnalysisResult[] = [
  { category: 'Digital Signatures', status: 'clean', confidence: 98, details: 'Valid certificate chain verified' },
  { category: 'Metadata Integrity', status: 'clean', confidence: 95, details: 'Creation timestamps consistent' },
  { category: 'Font Analysis', status: 'warning', confidence: 72, details: 'Non-standard font embedding detected' },
  { category: 'Image Forensics', status: 'clean', confidence: 94, details: 'No manipulation artifacts found' },
]

const StatusIcon = ({ status }: { status: 'clean' | 'warning' | 'flagged' }) => {
  if (status === 'clean') return (
    <svg className="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  )
  return (
    <svg className="w-4 h-4 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  )
}

export function ProductPreview() {
  const [previewState, setPreviewState] = useState<PreviewState>('upload')
  const [isHovering, setIsHovering] = useState(false)

  const handleUploadClick = () => {
    setPreviewState('analyzing')
    setTimeout(() => setPreviewState('results'), 2500)
  }

  const resetPreview = () => {
    setPreviewState('upload')
  }

  return (
    <section id="product-preview" className="py-24 px-6 border-t border-black/10 dark:border-white/10">
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
            PRODUCT PREVIEW
          </span>
          <h2 className="text-4xl md:text-5xl font-semibold mb-6 dark:text-white" style={{ fontFamily: 'Georgia, serif' }}>
            See It In Action
          </h2>
          <p className="text-[#2a2a2a]/70 dark:text-white/70 text-lg max-w-2xl mx-auto">
            Experience the power of AI-driven document forensics. Upload, analyze, and verify in seconds.
          </p>
        </motion.div>

        {/* Product Mockup Container */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.2 }}
          onMouseEnter={() => setIsHovering(true)}
          onMouseLeave={() => setIsHovering(false)}
          className="relative"
        >
          {/* Browser Frame */}
          <div className="relative rounded-2xl overflow-hidden shadow-[0_35px_60px_-15px_rgba(0,0,0,0.25)] border border-black/10 dark:border-white/10">
            {/* Browser Header */}
            <div className="bg-[#b8b8af]/90 dark:bg-[#2a2a2a]/90 backdrop-blur-md px-4 py-3 border-b border-black/10 dark:border-white/10 flex items-center gap-4">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-400/60" />
                <div className="w-3 h-3 rounded-full bg-yellow-400/60" />
                <div className="w-3 h-3 rounded-full bg-green-400/60" />
              </div>
              <div className="flex-1 flex justify-center">
                <div className="bg-[#C8C8BF]/50 dark:bg-white/10 rounded-lg px-4 py-1.5 text-sm text-[#2a2a2a]/60 dark:text-white/60 font-mono">
                  app.authentia.ai
                </div>
              </div>
              <div className="w-20" />
            </div>

            {/* App Content */}
            <div className="bg-[#C8C8BF] dark:bg-[#1a1a1a] flex min-h-[500px]">
              {/* Sidebar */}
              <div className="w-72 bg-[#b8b8af]/90 dark:bg-[#252525]/90 backdrop-blur-md border-r border-black/10 dark:border-white/10 p-6 flex flex-col">
                <div className="mb-6">
                  <h3 className="text-xl font-bold text-[#6f8f88]">Authentia AI</h3>
                  <p className="text-xs text-[#2a2a2a]/60 dark:text-white/60 mt-1">Forensic Engine v1.0</p>
                </div>

                <div className="flex-1">
                  <p className="text-xs text-[#2a2a2a]/60 dark:text-white/60 mb-3 tracking-wider">RECENT AUDITS</p>
                  <div className="space-y-2">
                    {['Contract_2024.pdf', 'Invoice_Q4.pdf', 'Agreement_v2.pdf'].map((name, i) => (
                      <motion.div
                        key={name}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="p-3 rounded-xl bg-white/30 dark:bg-white/5 border border-black/10 dark:border-white/10 cursor-pointer hover:bg-white/40 dark:hover:bg-white/10 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <svg className="w-4 h-4 text-[#2a2a2a]/60 dark:text-white/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <span className="text-sm truncate dark:text-white">{name}</span>
                          </div>
                          <div className={`w-2 h-2 rounded-full ${i === 1 ? 'bg-yellow-500' : 'bg-green-500'}`} />
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t border-black/10 dark:border-white/10">
                  <p className="text-xs text-[#2a2a2a]/40 dark:text-white/40">Forensic Document Engine v1.0</p>
                </div>
              </div>

              {/* Main Content */}
              <div className="flex-1 p-8 flex items-center justify-center">
                <AnimatePresence mode="wait">
                  {previewState === 'upload' && (
                    <motion.div
                      key="upload"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="text-center max-w-md"
                    >
                      <motion.div
                        whileHover={{ scale: 1.05, y: -5 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleUploadClick}
                        className="w-40 h-40 mx-auto mb-8 rounded-full bg-white/30 dark:bg-white/5 border border-black/10 dark:border-white/10 flex items-center justify-center cursor-pointer shadow-[0_25px_50px_-12px_rgba(0,0,0,0.15)] hover:shadow-[0_35px_60px_-15px_rgba(0,0,0,0.25)] hover:bg-white/40 dark:hover:bg-white/10 transition-all"
                      >
                        <svg className="w-12 h-12 text-[#6f8f88]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                        </svg>
                      </motion.div>
                      <h3 className="text-2xl font-semibold mb-2 dark:text-white">Upload Document</h3>
                      <p className="text-[#2a2a2a]/60 dark:text-white/60 mb-4">
                        Drop a document to begin forensic analysis
                      </p>
                      <p className="text-xs text-[#2a2a2a]/40 dark:text-white/40">
                        Supports: PDF, DOCX, DOC, PNG, JPG
                      </p>
                    </motion.div>
                  )}

                  {previewState === 'analyzing' && (
                    <motion.div
                      key="analyzing"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="text-center max-w-md"
                    >
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                        className="w-24 h-24 mx-auto mb-8 rounded-full border-4 border-[#6f8f88]/30 border-t-[#6f8f88]"
                      />
                      <h3 className="text-2xl font-semibold mb-2 dark:text-white">Analyzing Document</h3>
                      <p className="text-[#2a2a2a]/60 dark:text-white/60 mb-6">
                        Running forensic analysis...
                      </p>
                      <div className="space-y-2 text-left">
                        {['Extracting metadata', 'Verifying signatures', 'Analyzing patterns', 'Generating report'].map((step, i) => (
                          <motion.div
                            key={step}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.4 }}
                            className="flex items-center gap-2 text-sm text-[#2a2a2a]/60 dark:text-white/60"
                          >
                            <motion.div
                              initial={{ scale: 0 }}
                              animate={{ scale: 1 }}
                              transition={{ delay: i * 0.4 + 0.3 }}
                              className="w-4 h-4 rounded-full bg-green-500 flex items-center justify-center"
                            >
                              <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                              </svg>
                            </motion.div>
                            {step}
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {previewState === 'results' && (
                    <motion.div
                      key="results"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="w-full max-w-2xl"
                    >
                      {/* Results Header */}
                      <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 rounded-xl bg-white/30 dark:bg-white/5 border border-black/10 dark:border-white/10 flex items-center justify-center">
                            <svg className="w-6 h-6 text-[#6f8f88]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          </div>
                          <div>
                            <h3 className="font-semibold dark:text-white">Employment_Contract.pdf</h3>
                            <p className="text-sm text-[#2a2a2a]/60 dark:text-white/60">Analysis complete</p>
                          </div>
                        </div>
                        <motion.button
                          onClick={resetPreview}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          className="px-4 py-2 text-sm bg-[#6f8f88] text-white rounded-lg hover:bg-[#5a7a73] transition-colors"
                        >
                          New Analysis
                        </motion.button>
                      </div>

                      {/* Overall Status */}
                      <div className="p-4 rounded-xl bg-green-500/10 dark:bg-green-500/20 border border-green-500/30 mb-6 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center">
                          <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                          </svg>
                        </div>
                        <div>
                          <p className="font-semibold text-green-800 dark:text-green-400">Document Verified</p>
                          <p className="text-sm text-green-700/70 dark:text-green-400/70">High confidence authenticity score: 92%</p>
                        </div>
                      </div>

                      {/* Results Grid */}
                      <div className="grid grid-cols-2 gap-3">
                        {mockResults.map((result, i) => (
                          <motion.div
                            key={result.category}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className="p-4 rounded-xl bg-white/30 dark:bg-white/5 border border-black/10 dark:border-white/10 hover:bg-white/40 dark:hover:bg-white/10 transition-colors"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium dark:text-white">{result.category}</span>
                              <StatusIcon status={result.status} />
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-xs text-[#2a2a2a]/60 dark:text-white/60">{result.details}</span>
                              <span className="text-xs font-mono text-[#6f8f88]">{result.confidence}%</span>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>

          {/* Glow Effect on Hover */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: isHovering ? 1 : 0 }}
            transition={{ duration: 0.3 }}
            className="absolute -inset-4 bg-[#6f8f88]/10 rounded-3xl blur-2xl -z-10"
          />
        </motion.div>

        {/* Feature Highlights Below Preview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {[
            { title: 'Instant Analysis', desc: 'Results in under 5 seconds' },
            { title: '40+ Signals', desc: 'Comprehensive forensic checks' },
            { title: 'Audit History', desc: 'Track all document reviews' },
          ].map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="flex items-center gap-4 p-4 rounded-xl backdrop-blur-md bg-white/30 dark:bg-white/5 border border-black/10 dark:border-white/10"
            >
              <div className="w-10 h-10 rounded-lg bg-[#6f8f88]/10 dark:bg-[#6f8f88]/20 flex items-center justify-center">
                <svg className="w-5 h-5 text-[#6f8f88]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <p className="font-medium dark:text-white">{feature.title}</p>
                <p className="text-sm text-[#2a2a2a]/60 dark:text-white/60">{feature.desc}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
