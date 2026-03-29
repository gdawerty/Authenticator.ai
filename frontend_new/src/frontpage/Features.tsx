import { useRef, useState } from 'react'
import { motion, useScroll, useTransform, useMotionValueEvent, AnimatePresence, MotionValue } from 'framer-motion'

// Each feature has a distinct color — Apollo-style colored tabs
const TAB_COLORS = [
  { active: '#2563eb', bg: 'rgba(37,99,235,0.08)', text: '#2563eb', fill: '#2563eb' },   // 01 blue
  { active: '#16a34a', bg: 'rgba(22,163,74,0.08)',  text: '#16a34a', fill: '#16a34a' },   // 02 green
  { active: '#ca8a04', bg: 'rgba(202,138,4,0.08)',  text: '#ca8a04', fill: '#ca8a04' },   // 03 yellow
  { active: '#dc2626', bg: 'rgba(220,38,38,0.08)',  text: '#dc2626', fill: '#dc2626' },   // 04 red
]

const features = [
  {
    id: 'forensics',
    num: '01',
    label: 'Document Forensics',
    headline: 'Deep metadata & signature inspection',
    description: 'Every document carries hidden fingerprints. Authentia reads them — creation timestamps, software traces, edit history, embedded signatures — and flags any inconsistency that human eyes would miss.',
    bullets: ['PDF metadata extraction', 'Digital signature chain validation', 'Image manipulation detection (ELA)', 'Edit history reconstruction'],
  },
  {
    id: 'ai',
    num: '02',
    label: 'AI Content Analysis',
    headline: 'LLM-powered semantic reasoning',
    description: 'Our AI content layer reads the document as a human would — and smarter. It checks for logical inconsistencies, suspicious phrasing, fabricated figures, and contradictions across sections.',
    bullets: ['Semantic coherence scoring', 'Named entity cross-validation', 'Fabricated number detection', 'Inconsistency flagging with citations'],
  },
  {
    id: 'contracts',
    num: '03',
    label: 'Contract Workspace',
    headline: 'Annotate, flag, and collaborate',
    description: 'Organize documents into contract projects. Highlight suspicious text, draw region annotations, add forensic notes — all with animated leader lines pointing directly at the evidence.',
    bullets: ['Multi-document project folders', 'Region & text highlight annotations', 'Leader-line forensic notes', 'SHA-256 integrity manifest'],
  },
  {
    id: 'audit',
    num: '04',
    label: 'Audit Reports',
    headline: 'Exportable forensic audit trail',
    description: 'Every scan generates a structured audit report — Authentia Score, signal breakdown, annotation history, and a SHA-256 verified content manifest. Defensible documentation for compliance and legal review.',
    bullets: ['Structured Markdown export', 'Per-signal confidence breakdown', 'Timestamped annotation log', 'Cryptographic file manifest'],
  },
]

/* ─── Visuals (dark cards — intentional product screenshot aesthetic) ─── */

function ForensicsVisual() {
  const rows = [
    { name: 'Creation timestamp', value: '2019-03-12', flag: false },
    { name: 'Last modified', value: '2024-11-08 ⚠', flag: true },
    { name: 'Author field', value: 'Unknown', flag: true },
    { name: 'PDF version', value: '1.7 (Acrobat)', flag: false },
    { name: 'Digital signature', value: 'Missing', flag: true },
    { name: 'Image ELA score', value: '2.3 / 10', flag: false },
  ]
  return (
    <div className="bg-[#111115] rounded-xl border border-white/8 overflow-hidden w-full">
      <div className="px-4 py-3 border-b border-white/8 flex items-center gap-2">
        <span className="text-[11px] font-mono text-[#71717a]">metadata_scan.json</span>
        <span className="ml-auto text-[10px] font-mono text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded-full">3 flags</span>
      </div>
      <div className="p-4 space-y-2.5">
        {rows.map((s) => (
          <div key={s.name} className="flex items-center justify-between text-[12px]">
            <span className="text-[#71717a] font-mono">{s.name}</span>
            <span className={`font-mono ${s.flag ? 'text-amber-400' : 'text-[#a1a1aa]'}`}>{s.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function AIVisual() {
  return (
    <div className="bg-[#111115] rounded-xl border border-white/8 overflow-hidden w-full">
      <div className="px-4 py-3 border-b border-white/8">
        <span className="text-[11px] font-mono text-[#71717a]">ai · semantic analysis</span>
      </div>
      <div className="p-4 space-y-3">
        {[
          { label: 'Logical coherence', pct: 88, color: '#22c55e' },
          { label: 'Named entity match', pct: 61, color: '#f59e0b' },
          { label: 'Figure consistency', pct: 45, color: '#ef4444' },
          { label: 'Tone uniformity', pct: 92, color: '#22c55e' },
        ].map((s) => (
          <div key={s.label}>
            <div className="flex justify-between text-[11px] mb-1">
              <span className="text-[#a1a1aa]">{s.label}</span>
              <span className="font-mono" style={{ color: s.color }}>{s.pct}%</span>
            </div>
            <div className="h-1 bg-white/5 rounded-full overflow-hidden">
              <motion.div className="h-full rounded-full" style={{ background: s.color }}
                initial={{ width: 0 }} whileInView={{ width: `${s.pct}%` }}
                viewport={{ once: true }} transition={{ duration: 0.9, ease: 'easeOut' }} />
            </div>
          </div>
        ))}
        <div className="mt-3 p-3 bg-white/4 rounded-lg border border-red-500/20 text-[11px] text-red-400/80 font-mono">
          ⚠ Revenue figures in §3.2 conflict with totals in Appendix B.
        </div>
      </div>
    </div>
  )
}

function ContractVisual() {
  const files = ['master_agreement.pdf', 'exhibit_a_sow.docx', 'pricing_schedule.xlsx']
  return (
    <div className="bg-[#111115] rounded-xl border border-white/8 overflow-hidden w-full">
      <div className="px-4 py-3 border-b border-white/8 flex items-center gap-2">
        <span className="text-[11px] font-mono text-[#71717a]">Q4 Enterprise Deal</span>
        <span className="ml-auto text-[10px] font-mono text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded-full">3 files</span>
      </div>
      <div className="p-4 space-y-2">
        {files.map((f, i) => (
          <div key={f} className="flex items-center gap-2.5 p-2.5 rounded-lg bg-white/3 border border-white/6">
            <div className="w-5 h-5 rounded flex items-center justify-center text-[8px] font-bold font-mono"
              style={{ background: i === 0 ? '#c62828' : i === 1 ? '#1565c0' : '#2e7d32', color: '#fff' }}>
              {f.split('.').pop()?.toUpperCase().slice(0, 3)}
            </div>
            <span className="text-[11px] text-[#a1a1aa] font-mono truncate">{f}</span>
            {i === 0 && <span className="ml-auto text-[10px] text-amber-400 flex-shrink-0">2 flags</span>}
          </div>
        ))}
        <div className="mt-2 p-2.5 rounded-lg bg-[#ca8a04]/10 border border-[#ca8a04]/20">
          <span className="text-[10px] text-[#ca8a04] font-mono">✏ "Clause 4.3 date mismatch — verify original."</span>
        </div>
      </div>
    </div>
  )
}

function AuditVisual() {
  return (
    <div className="bg-[#111115] rounded-xl border border-white/8 overflow-hidden w-full font-mono text-[11px]">
      <div className="px-4 py-3 border-b border-white/8 flex items-center gap-2">
        <span className="text-[#71717a]">audit_report.md</span>
        <span className="ml-auto text-[10px] text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded-full">verified</span>
      </div>
      <div className="p-4 space-y-1 leading-relaxed">
        <div style={{ color: TAB_COLORS[3].fill }}># Forensic Audit Report</div>
        <div className="text-[#52525b]">Generated: 2026-03-28 09:14 UTC</div>
        <div className="mt-2" />
        <div className="text-[#fafaf9]">## Authentia Score</div>
        <div><span className="text-amber-400">score:</span><span className="text-[#fafaf9]"> 61.4 / 100</span></div>
        <div><span className="text-amber-400">verdict:</span><span className="text-red-400"> FLAGGED</span></div>
        <div className="mt-2" />
        <div className="text-[#fafaf9]">## File Integrity</div>
        <div className="text-[#3f3f46]">sha256: a3f9b2c1d4e5…</div>
        <div className="mt-2" style={{ color: TAB_COLORS[3].fill }}>## Annotations (2)</div>
        <div className="text-[#52525b]">- Region flag: §3.2 revenue mismatch</div>
        <div className="text-[#52525b]">- Highlight: "Date inconsistency"</div>
      </div>
    </div>
  )
}

const visuals = [<ForensicsVisual />, <AIVisual />, <ContractVisual />, <AuditVisual />]

/* ─── Tab in the horizontal bar ─── */

function TabItem({
  feature,
  colorIdx,
  isActive,
  progress,
}: {
  feature: (typeof features)[0]
  colorIdx: number
  isActive: boolean
  progress: MotionValue<number>
}) {
  const fillWidth = useTransform(progress, [0, 1], ['0%', '100%'])
  const color = TAB_COLORS[colorIdx]

  return (
    <div
      className="flex-1 px-6 py-5 relative border-r border-black/8 last:border-r-0 transition-colors duration-300 cursor-default"
      style={{ backgroundColor: isActive ? color.bg : 'transparent' }}
    >
      <div
        className="text-[10px] font-mono mb-1 transition-colors duration-300"
        style={{ color: isActive ? color.text : '#aaa' }}
      >
        {feature.num}
      </div>
      <div
        className="text-[13px] font-semibold transition-colors duration-300"
        style={{ color: isActive ? '#1a1a1a' : '#888' }}
      >
        {feature.label}
      </div>

      {/* Bottom progress fill */}
      <div className="absolute bottom-0 left-0 right-0 h-[2.5px] bg-black/5">
        <motion.div
          className="h-full origin-left"
          style={{ width: fillWidth, backgroundColor: color.fill }}
        />
      </div>
    </div>
  )
}

/* ─── Scroll canvas ─── */

function ScrollFeatures() {
  const sectionRef = useRef<HTMLDivElement>(null)
  const [activeIdx, setActiveIdx] = useState(0)

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ['start start', 'end end'],
  })

  const continuousIdx = useTransform(scrollYProgress, [0, 1], [0, features.length - 1])

  useMotionValueEvent(continuousIdx, 'change', (v) => {
    setActiveIdx(Math.round(v))
  })

  const p0 = useTransform(scrollYProgress, [0,    0.25], [0, 1])
  const p1 = useTransform(scrollYProgress, [0.25, 0.5 ], [0, 1])
  const p2 = useTransform(scrollYProgress, [0.5,  0.75], [0, 1])
  const p3 = useTransform(scrollYProgress, [0.75, 1.0 ], [0, 1])
  const progresses = [p0, p1, p2, p3]

  const f = features[activeIdx]
  const color = TAB_COLORS[activeIdx]

  return (
    <div ref={sectionRef} style={{ height: `${features.length * 100}vh` }}>
      {/* Sticky container — sits inside the beige page bg */}
      <div className="sticky top-14 h-[calc(100vh-3.5rem)] flex items-start py-6 px-8">
        {/* White card — Apollo style */}
        <div className="w-full max-w-[1280px] mx-auto bg-white rounded-2xl shadow-sm border border-black/8 overflow-hidden flex flex-col" style={{ height: 'calc(100vh - 3.5rem - 3rem)' }}>

          {/* ── Tab bar ── */}
          <div className="flex border-b border-black/8 flex-shrink-0">
            {features.map((feat, i) => (
              <TabItem
                key={feat.id}
                feature={feat}
                colorIdx={i}
                isActive={activeIdx === i}
                progress={progresses[i]}
              />
            ))}
          </div>

          {/* ── Content ── */}
          <div className="flex-1 flex items-center overflow-hidden min-h-0">
            <div className="w-full px-12">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeIdx}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                  className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center"
                >
                  {/* Text */}
                  <div>
                    <div className="text-[11px] font-mono uppercase tracking-[0.12em] mb-4" style={{ color: color.text }}>
                      {f.num} — {f.label}
                    </div>
                    <h3 className="text-[36px] md:text-[42px] font-bold tracking-[-0.02em] text-[#1a1a1a] leading-tight mb-5">
                      {f.headline}
                    </h3>
                    <p className="text-[15px] text-[#6b6b6b] leading-relaxed mb-8 max-w-md">
                      {f.description}
                    </p>
                    <ul className="space-y-3">
                      {f.bullets.map((b, bi) => (
                        <motion.li
                          key={b}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: bi * 0.07, duration: 0.4 }}
                          className="flex items-center gap-3 text-[14px] text-[#3a3a3a]"
                        >
                          <div
                            className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0"
                            style={{ background: color.bg }}
                          >
                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" style={{ color: color.text }}>
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                            </svg>
                          </div>
                          {b}
                        </motion.li>
                      ))}
                    </ul>
                  </div>

                  {/* Visual */}
                  <div className="hidden lg:flex items-center">
                    {visuals[activeIdx]}
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>
          </div>

          {/* ── Bottom dot indicator ── */}
          <div className="flex-shrink-0 flex justify-center pb-5 pt-3 border-t border-black/5">
            <div className="flex items-center gap-2">
              {features.map((_, i) => (
                <div
                  key={i}
                  className="h-1 rounded-full transition-all duration-500"
                  style={{
                    width: i === activeIdx ? 28 : 8,
                    background: i === activeIdx ? color.fill : 'rgba(0,0,0,0.12)',
                  }}
                />
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}

/* ─── Export ─── */

export function Features() {
  return (
    <section className="pt-20 pb-0">
      {/* Section header */}
      <div className="max-w-[1280px] mx-auto px-8 pb-12">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <span className="text-[11px] font-mono tracking-[0.14em] text-[#888] uppercase">
            Platform Capabilities
          </span>
          <h2 className="text-[44px] md:text-[56px] font-bold tracking-[-0.03em] text-[#1a1a1a] mt-3 leading-[1.05]">
            Everything you need to<br />
            <span style={{ color: TAB_COLORS[0].fill }}>verify</span>{' '}
            <span style={{ color: TAB_COLORS[1].fill }}>any</span>{' '}
            <span style={{ color: TAB_COLORS[2].fill }}>docu</span><span style={{ color: TAB_COLORS[3].fill }}>ment.</span>
          </h2>
        </motion.div>
      </div>

      <ScrollFeatures />
    </section>
  )
}
