import { motion } from 'framer-motion'

const features = [
  {
    title: 'Digital Fingerprinting',
    description: 'Advanced signature verification and certificate chain validation.',
  },
  {
    title: 'Metadata Analysis',
    description: 'Deep inspection of document metadata and modification history.',
  },
  {
    title: 'AI Pattern Recognition',
    description: 'ML models trained to detect anomalies and fraud patterns.',
  },
  {
    title: 'Enterprise Security',
    description: 'SOC 2 compliant with 256-bit encryption.',
  },
  {
    title: 'Confidence Scoring',
    description: 'Detailed authenticity scores with explainable insights.',
  },
  {
    title: 'Multi-Format Support',
    description: 'PDF, DOCX, images, and scanned documents.',
  },
]

export function Features() {
  return (
    <section id="features" className="py-24 px-6 border-t border-black/10">
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
            CAPABILITIES
          </span>
          <h2 className="text-4xl md:text-5xl font-semibold mb-6" style={{ fontFamily: 'Georgia, serif' }}>
            Enterprise-Grade Forensics
          </h2>
          <p className="text-[#2a2a2a]/70 text-lg max-w-2xl mx-auto">
            Built for security teams and enterprises who need bulletproof document verification.
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              whileHover={{ y: -5, scale: 1.02 }}
              className="group p-6 rounded-2xl backdrop-blur-md bg-white/30 border border-black/10 hover:border-[#6f8f88]/30 transition-all duration-300"
            >
              {/* Icon */}
              <div className="w-12 h-12 rounded-xl bg-[#6f8f88]/10 flex items-center justify-center mb-4 group-hover:bg-[#6f8f88]/20 transition-colors">
                <svg className="w-6 h-6 text-[#6f8f88]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>

              {/* Content */}
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-[#2a2a2a]/60 text-sm leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Stats Row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8"
        >
          {[
            { value: '40+', label: 'Forensic Signals' },
            { value: '<5s', label: 'Analysis Time' },
            { value: '99.7%', label: 'Detection Rate' },
            { value: '256-bit', label: 'Encryption' },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl font-semibold text-[#6f8f88] mb-2" style={{ fontFamily: 'Georgia, serif' }}>
                {stat.value}
              </div>
              <div className="text-sm text-[#2a2a2a]/60">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
