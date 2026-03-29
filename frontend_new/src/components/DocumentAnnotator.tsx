import { useState, useRef, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

// ─── Types ─────────────────────────────────────────────────────────────────────

interface Region {
  id: string
  label: string
  /** Normalized 0–1 relative to image natural size */
  x: number
  y: number
  w: number
  h: number
  color: string
  createdAt: string
}

interface DraftRegion {
  startX: number  // normalized
  startY: number
  x: number
  y: number
  w: number
  h: number
}

interface Props {
  /** URL of the document rendered as an image */
  imageUrl: string
  initialRegions?: Region[]
  onChange?: (regions: Region[]) => void
}

// ─── Constants ─────────────────────────────────────────────────────────────────

const REGION_COLORS = [
  '#ef4444', '#f97316', '#eab308', '#22c55e',
  '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6',
]

function genId() {
  return `rgn_${Math.random().toString(36).slice(2, 9)}`
}

function genLabel(idx: number) {
  return `Region_${String(idx + 1).padStart(2, '0')}`
}

function pickColor(idx: number) {
  return REGION_COLORS[idx % REGION_COLORS.length]
}

function fmt(n: number) {
  return n.toFixed(3)
}

// ─── Sidebar Card ──────────────────────────────────────────────────────────────

function RegionCard({
  region,
  index,
  isActive,
  onHover,
  onLeave,
  onDelete,
  onLabelChange,
}: {
  region: Region
  index: number
  isActive: boolean
  onHover: () => void
  onLeave: () => void
  onDelete: () => void
  onLabelChange: (label: string) => void
}) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(region.label)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (editing) inputRef.current?.focus()
  }, [editing])

  const commit = () => {
    onLabelChange(draft.trim() || region.label)
    setEditing(false)
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 24 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 24, scale: 0.95 }}
      transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
      onMouseEnter={onHover}
      onMouseLeave={onLeave}
      className={`relative rounded-xl border transition-all duration-150 cursor-default ${
        isActive
          ? 'border-white/20 bg-white/8 shadow-lg shadow-black/30'
          : 'border-white/6 bg-white/4 hover:bg-white/6 hover:border-white/12'
      }`}
      style={{ borderLeftColor: region.color, borderLeftWidth: 3 }}
    >
      <div className="px-3 py-2.5">
        {/* Header row */}
        <div className="flex items-center justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 min-w-0">
            {/* Color dot */}
            <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: region.color }} />
            {/* Index badge */}
            <span className="text-[10px] font-mono text-white/30 flex-shrink-0">#{String(index + 1).padStart(2, '0')}</span>
            {/* Label */}
            {editing ? (
              <input
                ref={inputRef}
                value={draft}
                onChange={e => setDraft(e.target.value)}
                onBlur={commit}
                onKeyDown={e => { if (e.key === 'Enter') commit(); if (e.key === 'Escape') { setDraft(region.label); setEditing(false) } }}
                className="text-xs font-mono bg-white/10 border border-white/20 rounded px-1.5 py-0.5 text-white outline-none w-full"
              />
            ) : (
              <button
                onClick={() => { setDraft(region.label); setEditing(true) }}
                className="text-xs font-semibold text-white truncate hover:text-white/70 transition-colors text-left"
              >
                {region.label}
              </button>
            )}
          </div>
          <button
            onClick={onDelete}
            className="w-5 h-5 flex items-center justify-center rounded-md hover:bg-red-500/20 text-white/30 hover:text-red-400 transition-colors flex-shrink-0 text-sm leading-none"
          >
            ×
          </button>
        </div>

        {/* Coordinates */}
        <div className="grid grid-cols-2 gap-x-3 gap-y-0.5">
          {[['x', region.x], ['y', region.y], ['w', region.w], ['h', region.h]].map(([k, v]) => (
            <div key={k as string} className="flex items-center gap-1">
              <span className="text-[9px] font-mono text-white/25 w-3">{k}</span>
              <span className="text-[10px] font-mono text-white/50">{fmt(v as number)}</span>
            </div>
          ))}
        </div>

        {/* ID pill */}
        <div className="mt-2">
          <span
            className="inline-flex items-center gap-1 text-[9px] font-mono px-2 py-0.5 rounded-full border"
            style={{ color: region.color, borderColor: `${region.color}40`, background: `${region.color}12` }}
          >
            <svg className="w-2 h-2" fill="currentColor" viewBox="0 0 24 24">
              <path d="M4 5h16a1 1 0 010 2H4a1 1 0 010-2zm0 6h16a1 1 0 010 2H4a1 1 0 010-2zm0 6h8a1 1 0 010 2H4a1 1 0 010-2z"/>
            </svg>
            {region.id}
          </span>
        </div>
      </div>
    </motion.div>
  )
}

// ─── Main Component ────────────────────────────────────────────────────────────

export function DocumentAnnotator({ imageUrl, initialRegions = [], onChange }: Props) {
  const [regions, setRegions] = useState<Region[]>(initialRegions)
  const [draft, setDraft] = useState<DraftRegion | null>(null)
  const [activeId, setActiveId] = useState<string | null>(null)
  const [zoom, setZoom] = useState(1)
  const [copied, setCopied] = useState(false)

  const containerRef = useRef<HTMLDivElement>(null)
  const isDragging = useRef(false)

  const getRel = useCallback((clientX: number, clientY: number): { x: number; y: number } => {
    const el = containerRef.current
    if (!el) return { x: 0, y: 0 }
    const rect = el.getBoundingClientRect()
    return {
      x: Math.max(0, Math.min(1, (clientX - rect.left) / rect.width)),
      y: Math.max(0, Math.min(1, (clientY - rect.top) / rect.height)),
    }
  }, [])

  const onMouseDown = useCallback((e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('[data-region]')) return
    e.preventDefault()
    const { x, y } = getRel(e.clientX, e.clientY)
    isDragging.current = true
    setDraft({ startX: x, startY: y, x, y, w: 0, h: 0 })
    setActiveId(null)
  }, [getRel])

  const onMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging.current || !draft) return
    const { x, y } = getRel(e.clientX, e.clientY)
    setDraft({
      startX: draft.startX,
      startY: draft.startY,
      x: Math.min(draft.startX, x),
      y: Math.min(draft.startY, y),
      w: Math.abs(x - draft.startX),
      h: Math.abs(y - draft.startY),
    })
  }, [draft, getRel])

  const onMouseUp = useCallback(() => {
    if (!isDragging.current || !draft) return
    isDragging.current = false
    if (draft.w < 0.01 || draft.h < 0.005) { setDraft(null); return }
    const idx = regions.length
    const newRegion: Region = {
      id: genId(),
      label: genLabel(idx),
      x: draft.x, y: draft.y, w: draft.w, h: draft.h,
      color: pickColor(idx),
      createdAt: new Date().toISOString(),
    }
    const updated = [...regions, newRegion]
    setRegions(updated)
    onChange?.(updated)
    setDraft(null)
    setActiveId(newRegion.id)
  }, [draft, regions, onChange])

  const deleteRegion = useCallback((id: string) => {
    const updated = regions.filter(r => r.id !== id)
    setRegions(updated)
    onChange?.(updated)
    if (activeId === id) setActiveId(null)
  }, [regions, onChange, activeId])

  const updateLabel = useCallback((id: string, label: string) => {
    const updated = regions.map(r => r.id === id ? { ...r, label } : r)
    setRegions(updated)
    onChange?.(updated)
  }, [regions, onChange])

  const exportJSON = () => {
    const data = regions.map(({ id, label, x, y, w, h, color }) => ({
      id, label, color,
      normalized: { x: +x.toFixed(4), y: +y.toFixed(4), w: +w.toFixed(4), h: +h.toFixed(4) },
    }))
    navigator.clipboard.writeText(JSON.stringify(data, null, 2))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const clearAll = () => { setRegions([]); onChange?.([]) }

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <div className="flex h-full bg-[#0f0f0f] text-white overflow-hidden" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>

      {/* ── Left: Canvas pane ── */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">

        {/* Top bar */}
        <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/8 bg-[#151515] flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
              <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80" />
              <div className="w-2.5 h-2.5 rounded-full bg-green-500/80" />
            </div>
            <span className="text-sm font-semibold text-white/80">Document Annotator</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-red-500/15 text-red-400 border border-red-500/25 font-mono">
              region-tool
            </span>
          </div>
          <div className="flex items-center gap-2">
            {/* Zoom controls */}
            <div className="flex items-center gap-1 bg-white/5 rounded-lg px-1 border border-white/8">
              <button onClick={() => setZoom(z => Math.max(0.25, z - 0.25))}
                className="w-7 h-7 flex items-center justify-center text-white/50 hover:text-white transition-colors text-lg leading-none">−</button>
              <span className="text-xs font-mono text-white/40 w-10 text-center">{Math.round(zoom * 100)}%</span>
              <button onClick={() => setZoom(z => Math.min(4, z + 0.25))}
                className="w-7 h-7 flex items-center justify-center text-white/50 hover:text-white transition-colors text-lg leading-none">+</button>
            </div>
            <button onClick={() => setZoom(1)}
              className="text-xs px-2.5 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-white/40 hover:text-white transition-colors border border-white/8">
              Reset
            </button>
          </div>
        </div>

        {/* Canvas */}
        <div className="flex-1 overflow-auto bg-[#0a0a0a]" style={{ backgroundImage: 'radial-gradient(circle, #1a1a1a 1px, transparent 1px)', backgroundSize: '20px 20px' }}>
          <div className="flex items-start justify-center p-8 min-h-full">
            <div
              style={{ transform: `scale(${zoom})`, transformOrigin: 'top center', transition: 'transform 0.15s ease' }}
            >
              <div
                ref={containerRef}
                className="relative cursor-crosshair select-none"
                style={{ lineHeight: 0 }}
                onMouseDown={onMouseDown}
                onMouseMove={onMouseMove}
                onMouseUp={onMouseUp}
                onMouseLeave={onMouseUp}
              >
                {/* Document image */}
                <img
                  src={imageUrl}
                  alt="Document"
                  className="block shadow-2xl border border-white/10"
                  draggable={false}
                  style={{ maxWidth: 900 }}
                />

                {/* SVG overlay */}
                <svg
                  className="absolute inset-0 pointer-events-none"
                  style={{ width: '100%', height: '100%', overflow: 'visible' }}
                  viewBox="0 0 1 1"
                  preserveAspectRatio="none"
                >
                  <defs>
                    {regions.map(r => (
                      <filter key={`glow-${r.id}`} id={`glow-${r.id}`} x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="0.005" result="blur" />
                        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                      </filter>
                    ))}
                  </defs>

                  {/* Committed regions */}
                  {regions.map(r => {
                    const isHov = activeId === r.id
                    return (
                      <g key={r.id} data-region="1" style={{ pointerEvents: 'none' }}>
                        {/* Fill */}
                        <rect
                          x={r.x} y={r.y} width={r.w} height={r.h}
                          fill={r.color}
                          fillOpacity={isHov ? 0.22 : 0.12}
                          stroke={r.color}
                          strokeWidth={isHov ? 0.003 : 0.002}
                          strokeOpacity={isHov ? 1 : 0.7}
                          rx="0.003"
                          filter={isHov ? `url(#glow-${r.id})` : undefined}
                        />
                        {/* Corner anchors */}
                        {isHov && (
                          <>
                            {[[r.x, r.y], [r.x + r.w, r.y], [r.x, r.y + r.h], [r.x + r.w, r.y + r.h]].map(([cx, cy], i) => (
                              <circle key={i} cx={cx} cy={cy} r="0.006" fill={r.color} opacity={0.9} />
                            ))}
                          </>
                        )}
                        {/* Label pill */}
                        <foreignObject x={r.x} y={Math.max(0, r.y - 0.045)} width={0.2} height={0.04}
                          style={{ overflow: 'visible' }}>
                          <div
                            style={{
                              background: r.color,
                              color: '#fff',
                              fontSize: 9,
                              fontFamily: 'monospace',
                              padding: '1px 5px',
                              borderRadius: 4,
                              display: 'inline-block',
                              whiteSpace: 'nowrap',
                              opacity: 0.92,
                            }}
                          >
                            {r.label}
                          </div>
                        </foreignObject>
                      </g>
                    )
                  })}

                  {/* Draft */}
                  {draft && draft.w > 0.005 && draft.h > 0.005 && (
                    <rect
                      x={draft.x} y={draft.y} width={draft.w} height={draft.h}
                      fill="rgba(239,68,68,0.18)"
                      stroke="#ef4444"
                      strokeWidth="0.003"
                      strokeDasharray="0.01 0.008"
                      rx="0.003"
                    />
                  )}
                </svg>

                {/* Hit-area divs for hover */}
                {regions.map(r => (
                  <div
                    key={r.id}
                    data-region="1"
                    className="absolute"
                    style={{
                      left: `${r.x * 100}%`,
                      top: `${r.y * 100}%`,
                      width: `${r.w * 100}%`,
                      height: `${r.h * 100}%`,
                      cursor: 'pointer',
                    }}
                    onMouseEnter={() => setActiveId(r.id)}
                    onMouseLeave={() => setActiveId(null)}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Right: Sidebar ── */}
      <div className="w-72 flex-shrink-0 flex flex-col border-l border-white/8 bg-[#111111]">

        {/* Sidebar header */}
        <div className="px-4 py-3 border-b border-white/8 flex-shrink-0">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm font-semibold text-white/80">Annotations</span>
            <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-white/8 text-white/40 border border-white/10">
              {regions.length}
            </span>
          </div>
          <p className="text-[11px] text-white/30">Click + drag to draw regions</p>
        </div>

        {/* Region cards */}
        <div className="flex-1 overflow-y-auto px-3 py-3 space-y-2">
          <AnimatePresence mode="popLayout">
            {regions.length === 0 ? (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center py-12 text-center"
              >
                <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/8 flex items-center justify-center mb-3">
                  <svg className="w-5 h-5 text-white/20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 20H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v3"/>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 14l4 4m0 0l4-4m-4 4V10"/>
                  </svg>
                </div>
                <p className="text-xs text-white/30">No regions yet</p>
                <p className="text-[11px] text-white/20 mt-1">Draw on the document to start</p>
              </motion.div>
            ) : (
              regions.map((r, i) => (
                <RegionCard
                  key={r.id}
                  region={r}
                  index={i}
                  isActive={activeId === r.id}
                  onHover={() => setActiveId(r.id)}
                  onLeave={() => setActiveId(null)}
                  onDelete={() => deleteRegion(r.id)}
                  onLabelChange={label => updateLabel(r.id, label)}
                />
              ))
            )}
          </AnimatePresence>
        </div>

        {/* Footer actions */}
        <div className="px-3 py-3 border-t border-white/8 space-y-2 flex-shrink-0">
          <button
            onClick={exportJSON}
            disabled={regions.length === 0}
            className="w-full flex items-center justify-center gap-2 py-2 rounded-xl bg-white/8 hover:bg-white/12 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-sm text-white/80 border border-white/10"
          >
            {copied ? (
              <>
                <svg className="w-3.5 h-3.5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7"/>
                </svg>
                <span className="text-green-400 text-xs font-mono">Copied to clipboard!</span>
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                </svg>
                Export JSON
              </>
            )}
          </button>
          {regions.length > 0 && (
            <button
              onClick={clearAll}
              className="w-full py-2 rounded-xl text-xs text-red-400/60 hover:text-red-400 hover:bg-red-500/8 transition-colors"
            >
              Clear all regions
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
