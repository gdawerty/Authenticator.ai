import { motion } from 'framer-motion'

const stats = [
  { value: '40+', label: 'Forensic Signals', sub: 'per document scan' },
  { value: '<5s', label: 'Analysis Time', sub: 'average processing' },
  { value: '99.7%', label: 'Detection Rate', sub: 'across document types' },
  { value: '256-bit', label: 'Encryption', sub: 'at rest and in transit' },
]

export function Stats() {
  return (
    <section className="px-8 py-4">
      <div className="max-w-[1280px] mx-auto">
        <div className="bg-white rounded-2xl border border-black/8 shadow-sm overflow-hidden">
          <div className="grid grid-cols-2 md:grid-cols-4">
            {stats.map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08, duration: 0.5 }}
                className={`px-8 py-10 ${i < stats.length - 1 ? 'border-r border-black/8' : ''} ${i >= 2 ? 'border-t border-black/8 md:border-t-0' : ''}`}
              >
                <div className="text-[40px] font-bold tracking-[-0.03em] text-[#1a1a1a] leading-none mb-1">
                  {stat.value}
                </div>
                <div className="text-[13px] font-medium text-[#1a1a1a] mt-2">{stat.label}</div>
                <div className="text-[11px] text-[#888] mt-0.5">{stat.sub}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
