import { motion } from 'framer-motion'

/* ─── Animated radial signal diagram ─── */
function RadialDiagram({
  nodes,
  accentColor,
  label,
}: {
  nodes: { label: string; angle: number; icon: string }[]
  accentColor: string
  label: string
}) {
  const cx = 200
  const cy = 200
  const r = 130

  return (
    <div className="relative w-full" style={{ aspectRatio: '1/1', maxWidth: 340 }}>
      <svg viewBox="0 0 400 400" className="w-full h-full overflow-visible">
        <defs>
          <filter id={`glow-${label}`} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Background rings */}
        {[55, 92, 130].map((radius) => (
          <circle key={radius} cx={cx} cy={cy} r={radius}
            fill="none" stroke="rgba(0,0,0,0.06)" strokeWidth="1" />
        ))}

        {/* Dashed lines from center to nodes */}
        {nodes.map((n, i) => {
          const rad = (n.angle * Math.PI) / 180
          const nx = cx + r * Math.cos(rad)
          const ny = cy + r * Math.sin(rad)
          return (
            <line key={i} x1={cx} y1={cy} x2={nx} y2={ny}
              stroke={`${accentColor}`} strokeWidth="1" strokeOpacity="0.2"
              strokeDasharray="4 5" />
          )
        })}

        {/* Glowing bottom arc */}
        <path
          d={`M ${cx - 110} ${cy + 28} A 112 112 0 0 1 ${cx + 110} ${cy + 28}`}
          fill="none" stroke={accentColor} strokeWidth="2.5" strokeOpacity="0.5"
          filter={`url(#glow-${label})`}
          strokeLinecap="round"
        />

        {/* Node labels */}
        {nodes.map((n, i) => {
          const rad = (n.angle * Math.PI) / 180
          const nx = cx + r * Math.cos(rad)
          const ny = cy + r * Math.sin(rad)
          return (
            <g key={i}>
              <rect x={nx - 32} y={ny - 14} width={64} height={28} rx={7}
                fill="#f0f0ed" stroke={accentColor} strokeOpacity="0.4" strokeWidth="1" />
              <text x={nx} y={ny - 3} textAnchor="middle"
                fill={accentColor} fontSize="7" fontFamily="monospace" letterSpacing="0.8" fillOpacity="0.9">
                {n.icon}
              </text>
              <text x={nx} y={ny + 7} textAnchor="middle"
                fill="rgba(0,0,0,0.55)" fontSize="6.5" fontFamily="monospace" letterSpacing="0.5">
                {n.label}
              </text>
            </g>
          )
        })}

        {/* Traveling pulse dots */}
        {nodes.map((n, i) => {
          const rad = (n.angle * Math.PI) / 180
          const nx = cx + r * Math.cos(rad)
          const ny = cy + r * Math.sin(rad)
          return (
            <motion.circle key={i} r={3} fill={accentColor}
              animate={{
                cx: [cx, nx],
                cy: [cy, ny],
                opacity: [0, 1, 0],
              }}
              transition={{ duration: 2, repeat: Infinity, delay: i * 0.45, ease: 'easeOut' }}
            />
          )
        })}

        {/* Center node */}
        <circle cx={cx} cy={cy} r={34} fill="#f0f0ed" stroke={accentColor} strokeWidth="1.5" strokeOpacity="0.6" />
        <circle cx={cx} cy={cy} r={34} fill={accentColor} fillOpacity="0.08" />

        {/* Center glow pulse */}
        <motion.circle cx={cx} cy={cy} r={38} fill="none" stroke={accentColor} strokeWidth="1.5"
          animate={{ r: [34, 46], strokeOpacity: [0.4, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeOut' }}
        />
      </svg>

      {/* Center icon */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div style={{ color: accentColor }}>
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
      </div>
    </div>
  )
}

/* ─── Step icons ─── */
function SearchIcon() {
  return (
    <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.3}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  )
}
function BrainIcon() {
  return (
    <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.3}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>
  )
}
function ShieldIcon() {
  return (
    <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.3}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  )
}

const steps = [
  {
    icon: <SearchIcon />,
    title: 'Ingest & Extract',
    desc: 'Upload any document — PDF, DOCX, image, spreadsheet. Authentia immediately extracts raw text, embedded metadata, file structure, and all objects from every page.',
  },
  {
    icon: <BrainIcon />,
    title: 'Analyze & Score',
    desc: '40+ forensic signals fire simultaneously: metadata timestamps, digital signature chains, ELA image analysis, and an LLM semantic pass checking internal consistency.',
  },
  {
    icon: <ShieldIcon />,
    title: 'Verify & Report',
    desc: 'An Authentia Score (0–100) is generated with per-signal confidence breakdowns, a SHA-256 file manifest, and a full annotated audit trail ready for legal review.',
  },
]

/* ─── Section 1: How It Works ─── */
function HowSection() {
  return (
    <div className="px-4 md:px-8 space-y-4">
      {/* Header card */}
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.65 }}
        className="bg-white rounded-[28px] px-10 py-14 text-center"
      >
        <div className="inline-flex items-center px-4 py-1.5 rounded-full border border-black/12 text-[11px] font-mono tracking-[0.12em] text-[#888] uppercase mb-8">
          How Authentia Works
        </div>
        <h2 className="text-[40px] md:text-[52px] font-bold text-white tracking-[-0.03em] leading-[1.05] max-w-2xl mx-auto mb-5">
          Forensic-grade verification, automated end-to-end
        </h2>
        <p className="text-[16px] text-[#6b6b6b] leading-relaxed max-w-2xl mx-auto">
          From upload to audit report in under 5 seconds. Authentia runs every signal in parallel so you get a complete picture instantly, not a slow sequential checklist.
        </p>
      </motion.div>

      {/* 3 step cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {steps.map((s, i) => (
          <motion.div
            key={s.title}
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1, duration: 0.6 }}
            className="bg-white rounded-[24px] p-8 flex flex-col"
          >
            {/* Icon with glow */}
            <div className="mb-8">
              <div className="relative inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[#6f8f88]/12 text-[#6f8f88]">
                {s.icon}
                <div className="absolute inset-0 rounded-2xl bg-[#6f8f88]/10 blur-md" />
              </div>
            </div>
            <div className="text-[10px] font-mono text-[#bbb] mb-2 tracking-wider">STEP {String(i + 1).padStart(2, '0')}</div>
            <h3 className="text-[22px] font-bold text-white mb-4 leading-tight">{s.title}</h3>
            <p className="text-[14px] text-[#6b6b6b] leading-relaxed">{s.desc}</p>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

/* ─── Section 2: Why It Matters ─── */
const signalNodes = [
  { label: 'METADATA',  angle: -90,  icon: '⏱' },
  { label: 'SIGNATURE', angle: -30,  icon: '✍' },
  { label: 'AI LAYER',  angle: 30,   icon: '🧠' },
  { label: 'ELA SCAN',  angle: 90,   icon: '📷' },
  { label: 'SHA-256',   angle: 150,  icon: '🔒' },
  { label: 'AUTHOR',    angle: 210,  icon: '👤' },
]

const formatNodes = [
  { label: 'PDF',        angle: -90,  icon: '📄' },
  { label: 'DOCX',       angle: -30,  icon: '📝' },
  { label: 'XLSX',       angle: 30,   icon: '📊' },
  { label: 'PNG/JPG',    angle: 90,   icon: '🖼' },
  { label: 'CSV',        angle: 150,  icon: '📋' },
  { label: 'TIFF',       angle: 210,  icon: '🗂' },
]

function WhySection() {
  return (
    <div className="px-4 md:px-8 space-y-4">
      {/* Header card */}
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.65 }}
        className="bg-white rounded-[28px] px-10 py-14 text-center"
      >
        <div className="inline-flex items-center px-4 py-1.5 rounded-full border border-black/12 text-[11px] font-mono tracking-[0.12em] text-[#888] uppercase mb-8">
          Why It Matters
        </div>
        <h2 className="text-[40px] md:text-[52px] font-bold text-white tracking-[-0.03em] leading-[1.05] max-w-2xl mx-auto mb-5">
          Document fraud is invisible.<br />Until it isn't.
        </h2>
        <p className="text-[16px] text-[#6b6b6b] leading-relaxed max-w-2xl mx-auto">
          A forged contract, a manipulated invoice, a backdated agreement — the signals are always there. They just need a system designed to find them before the damage is done.
        </p>
      </motion.div>

      {/* 2 diagram cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1, duration: 0.6 }}
          className="bg-white rounded-[24px] p-8"
        >
          <div className="text-[11px] font-mono text-[#6f8f88] uppercase tracking-wider mb-2">Signal Graph</div>
          <h3 className="text-[22px] font-bold text-white mb-2 leading-tight">
            Fraud hides in the details.
          </h3>
          <p className="text-[13px] text-[#888] leading-relaxed mb-8 max-w-sm">
            Every document emits forensic signals. Authentia reads all of them simultaneously — no single point of failure.
          </p>
          <div className="flex justify-center">
            <RadialDiagram nodes={signalNodes} accentColor="#6f8f88" label="signals" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="bg-white rounded-[24px] p-8"
        >
          <div className="text-[11px] font-mono text-amber-400 uppercase tracking-wider mb-2">Format Coverage</div>
          <h3 className="text-[22px] font-bold text-white mb-2 leading-tight">
            Every format is a vector.
          </h3>
          <p className="text-[13px] text-[#888] leading-relaxed mb-8 max-w-sm">
            Fraud doesn't care what file type you're using. Authentia's engine works across every document format you'll encounter.
          </p>
          <div className="flex justify-center">
            <RadialDiagram nodes={formatNodes} accentColor="#f59e0b" label="formats" />
          </div>
        </motion.div>
      </div>
    </div>
  )
}

/* ─── Export ─── */
export function HowItWorks() {
  return (
    <div className="py-8 space-y-8 max-w-[1280px] mx-auto">
      <HowSection />
      <WhySection />
    </div>
  )
}
