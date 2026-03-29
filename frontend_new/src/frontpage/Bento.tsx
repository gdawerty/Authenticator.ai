import { motion } from 'framer-motion'

function ScoreRing({ score = 98.7 }: { score?: number }) {
  const r = 52
  const circ = 2 * Math.PI * r
  const offset = circ - (score / 100) * circ
  return (
    <div className="flex flex-col items-center justify-center h-full gap-3">
      <div className="relative">
        <svg width="130" height="130" className="-rotate-90">
          <circle cx="65" cy="65" r={r} fill="none" stroke="#1c1c22" strokeWidth="8" />
          <motion.circle
            cx="65" cy="65" r={r}
            fill="none"
            stroke="#6f8f88"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circ}
            initial={{ strokeDashoffset: circ }}
            whileInView={{ strokeDashoffset: offset }}
            viewport={{ once: true }}
            transition={{ duration: 1.4, ease: 'easeOut', delay: 0.2 }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-[28px] font-bold text-[#1a1a1a] leading-none">{score}</span>
          <span className="text-[10px] font-mono text-[#888] mt-0.5">/ 100</span>
        </div>
      </div>
      <div className="text-center">
        <div className="text-[13px] font-semibold text-[#1a1a1a]">Authentia Score</div>
        <div className="text-[11px] text-[#999] mt-0.5">Weighted forensic confidence</div>
      </div>
    </div>
  )
}

function PipelineFlow() {
  const steps = ['Ingest', 'OCR', 'Forensics', 'AI', 'Score']
  return (
    <div className="flex flex-col h-full justify-center gap-3 py-2">
      {steps.map((step, i) => (
        <motion.div
          key={step}
          initial={{ opacity: 0, x: -20 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ delay: i * 0.1, duration: 0.5 }}
          className="flex items-center gap-3"
        >
          <div className="w-6 h-6 rounded-full bg-[#6f8f88]/15 border border-[#6f8f88]/30 flex items-center justify-center text-[10px] font-bold text-[#6f8f88] flex-shrink-0">
            {i + 1}
          </div>
          <div className="flex-1 h-px bg-gradient-to-r from-[#6f8f88]/30 to-transparent" />
          <span className="text-[12px] font-mono text-[#999]">{step}</span>
          {i < steps.length - 1 && (
            <motion.div
              className="w-1.5 h-1.5 rounded-full bg-[#6f8f88]"
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.3 }}
            />
          )}
        </motion.div>
      ))}
    </div>
  )
}

const bentoItems = [
  {
    className: 'col-span-2 row-span-2',
    label: 'Confidence Engine',
    content: <ScoreRing />,
  },
  {
    className: 'col-span-1',
    label: 'Processing Pipeline',
    content: <PipelineFlow />,
  },
  {
    className: 'col-span-1',
    label: 'Supported Formats',
    content: (
      <div className="flex flex-wrap gap-2 items-start">
        {['PDF', 'DOCX', 'PNG', 'JPG', 'TIFF', 'XLSX', 'CSV', 'TXT'].map((f) => (
          <span key={f} className="text-[11px] font-mono px-2 py-1 rounded bg-[#1c1c22] text-[#999] border border-black/10">{f}</span>
        ))}
      </div>
    ),
  },
  {
    className: 'col-span-1',
    label: 'Security',
    content: (
      <div className="space-y-2">
        {['SOC 2 Type II', 'GDPR Compliant', 'Zero data retention', 'AES-256 at rest'].map((s) => (
          <div key={s} className="flex items-center gap-2 text-[12px]">
            <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full flex-shrink-0" />
            <span className="text-[#999]">{s}</span>
          </div>
        ))}
      </div>
    ),
  },
  {
    className: 'col-span-1',
    label: 'Zero Config Setup',
    content: (
      <div className="space-y-1 font-mono text-[11px]">
        <div className="text-[#999]">$ <span className="text-[#6f8f88]">upload</span> contract.pdf</div>
        <div className="text-[#999]">→ scanning metadata...</div>
        <div className="text-[#999]">→ running AI analysis...</div>
        <div className="text-emerald-400">✓ score: 98.7 (authentic)</div>
      </div>
    ),
  },
]

export function Bento() {
  return (
    <section className="py-24 px-8 border-t border-black/10">
      <div className="max-w-[1280px] mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-14"
        >
          <span className="text-[11px] font-mono tracking-[0.14em] text-[#888] uppercase">Built different</span>
          <h2 className="text-[40px] md:text-[52px] font-bold tracking-[-0.03em] text-[#1a1a1a] mt-3 leading-[1.05]">
            One platform. Every angle covered.
          </h2>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 auto-rows-[160px]">
          {bentoItems.map((item, i) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.07, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
              className={`${item.className} bg-white border border-black/10 rounded-2xl p-5 flex flex-col hover:border-[#2a2a35] transition-colors group relative overflow-hidden`}
            >
              {/* Corner glow on hover */}
              <div className="absolute -top-8 -right-8 w-24 h-24 bg-[#6f8f88]/5 rounded-full blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

              <div className="text-[11px] font-mono text-[#999] mb-3 uppercase tracking-wider">{item.label}</div>
              <div className="flex-1 overflow-hidden">
                {item.content}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
