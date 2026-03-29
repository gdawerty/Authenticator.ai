import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

// ─── Theme ────────────────────────────────────────────────────────────────────
const T = {
  bg:       '#08080d',
  surface:  '#0f0f16',
  surface2: '#13131c',
  border:   '#1c1c2a',
  border2:  '#252535',
  text:     '#e2e2f0',
  muted:    '#5a5a78',
  accent:   '#7c3aed',
  accentLt: '#a78bfa',
  red:      '#ef4444',
}

// ─── Types ────────────────────────────────────────────────────────────────────
type Step    = 1 | 2
type View    = 'document' | 'workflow'
type DocTab  = 'annotations' | 'viewer' | 'metadata' | 'audit'
type RightTab = 'pearl' | 'configure' | 'code' | 'console' | 'history'

interface Region {
  id: string
  x: number; y: number
  w: number; h: number
  label: string
  color: string
}

interface FileNode {
  id: string; name: string
  type: 'folder' | 'pdf' | 'docx'
  children?: FileNode[]
}

// ─── Constants ────────────────────────────────────────────────────────────────
const MARCH_CSS = `
  @keyframes march { to { stroke-dashoffset: -20; } }
  .march { animation: march 0.8s linear infinite; }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
  .blink { animation: blink 1.1s step-end infinite; }
`

const MOCK_TREE: FileNode[] = []
const CANVAS_DOCS: { id: string; name: string; ext: string }[] = []

// ─── Helpers ──────────────────────────────────────────────────────────────────
function uid() { return Math.random().toString(36).slice(2, 9) }
function extColor(ext: string) {
  return ext === 'pdf' ? '#ef4444' : ext === 'docx' ? '#3b82f6' : '#8b5cf6'
}

// ─── Top Nav ──────────────────────────────────────────────────────────────────
function TopNav({ step, view, setView, onBack }: {
  step: Step; view: View; setView: (v: View) => void; onBack?: () => void
}) {
  return (
    <div
      className="flex items-center flex-shrink-0 px-4"
      style={{ height: 48, background: T.surface, borderBottom: `1px solid ${T.border}`, gap: 0 }}
    >
      {/* Back */}
      {onBack && (
        <button
          onClick={onBack}
          className="flex items-center gap-1.5 text-[11px] mr-4 transition-colors"
          style={{ color: T.muted, fontFamily: 'monospace' }}
          onMouseEnter={e => (e.currentTarget.style.color = T.text)}
          onMouseLeave={e => (e.currentTarget.style.color = T.muted)}
        >
          <svg className="w-3.5 h-3.5" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
            <path d="M13 16l-5-6 5-6"/>
          </svg>
          back
        </button>
      )}

      {/* Progress — centered */}
      <div className="flex-1 flex items-center justify-center gap-0">
        {/* Step 1 */}
        <div className="flex items-center gap-2">
          <div
            className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold"
            style={{
              background: step >= 1 ? T.accent : T.border2,
              color: step >= 1 ? '#fff' : T.muted,
              boxShadow: step >= 1 ? `0 0 10px rgba(124,58,237,0.5)` : 'none',
            }}
          >1</div>
          <span className="text-[11px] font-medium" style={{ color: step === 1 ? T.accentLt : T.muted }}>
            Input
          </span>
        </div>

        {/* Connector */}
        <div className="flex items-center mx-3 gap-0.5">
          {[0,1,2,3,4,5].map(i => (
            <div key={i} className="w-2 h-px rounded-full transition-colors"
              style={{ background: step === 2 ? T.accent : i < 3 ? T.border2 : T.border }} />
          ))}
        </div>

        {/* Step 2 */}
        <div className="flex items-center gap-2">
          <div
            className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold transition-all"
            style={{
              background: step >= 2 ? T.accent : T.border2,
              color: step >= 2 ? '#fff' : T.muted,
              boxShadow: step >= 2 ? `0 0 10px rgba(124,58,237,0.5)` : 'none',
            }}
          >2</div>
          <span className="text-[11px] font-medium transition-colors"
            style={{ color: step === 2 ? T.accentLt : T.muted }}>
            Analysis
          </span>
        </div>
      </div>

      {/* View toggle */}
      <div
        className="flex rounded-lg overflow-hidden flex-shrink-0"
        style={{ border: `1px solid ${T.border2}`, background: T.bg }}
      >
        {(['document', 'workflow'] as View[]).map(v => (
          <button
            key={v}
            onClick={() => setView(v)}
            className="px-3 py-1 text-[11px] font-medium transition-colors"
            style={{
              background: view === v ? T.accent : 'transparent',
              color: view === v ? '#fff' : T.muted,
            }}
          >
            {v === 'document' ? 'Document View' : 'Workflow View'}
          </button>
        ))}
      </div>
    </div>
  )
}

// ─── Vault Sidebar ────────────────────────────────────────────────────────────
function FileIcon({ type }: { type: FileNode['type'] }) {
  if (type === 'folder') return (
    <svg className="w-3.5 h-3.5 flex-shrink-0 text-[#facc15]" viewBox="0 0 20 20" fill="currentColor">
      <path fillRule="evenodd" d="M2 6a2 2 0 012-2h4l2 2h6a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clipRule="evenodd"/>
    </svg>
  )
  const color = type === 'pdf' ? '#ef4444' : '#3b82f6'
  return (
    <svg className="w-3 h-3.5 flex-shrink-0" viewBox="0 0 12 16" fill="none">
      <path d="M2 0h6l3 3v11a2 2 0 01-2 2H2a2 2 0 01-2-2V2a2 2 0 012-2z" fill={color} opacity={0.18}/>
      <path d="M8 0l3 3H8V0z" fill={color} opacity={0.5}/>
      <rect x="2" y="6" width="8" height="1" rx="0.5" fill={color} opacity={0.6}/>
      <rect x="2" y="8.5" width="6" height="1" rx="0.5" fill={color} opacity={0.4}/>
    </svg>
  )
}

function TreeItem({ node, depth = 0, selected, onSelect }: {
  node: FileNode; depth?: number
  selected: string | null; onSelect: (id: string) => void
}) {
  const [open, setOpen] = useState(true)
  const isFolder = node.type === 'folder'
  const isSel = selected === node.id
  return (
    <div>
      <button
        onClick={() => isFolder ? setOpen(o => !o) : onSelect(node.id)}
        className="w-full flex items-center gap-1.5 py-[5px] pr-2 rounded text-left group"
        style={{
          paddingLeft: 8 + depth * 14,
          background: isSel ? 'rgba(124,58,237,0.15)' : undefined,
          color: isSel ? T.accentLt : T.muted,
        }}
        onMouseEnter={e => { if (!isSel) (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.04)' }}
        onMouseLeave={e => { if (!isSel) (e.currentTarget as HTMLElement).style.background = '' }}
      >
        {isFolder && (
          <svg className={`w-2 h-2 flex-shrink-0 transition-transform ${open ? 'rotate-90' : ''}`}
            viewBox="0 0 8 8" fill="currentColor" style={{ opacity: 0.4 }}>
            <path d="M2 1l4 3-4 3V1z"/>
          </svg>
        )}
        {!isFolder && <span className="w-2 flex-shrink-0" />}
        <FileIcon type={node.type} />
        <span className="text-[11px] truncate" style={{ fontFamily: 'monospace', color: isSel ? T.accentLt : isFolder ? T.text : T.muted }}>
          {node.name}
        </span>
      </button>
      {isFolder && open && node.children?.map(c =>
        <TreeItem key={c.id} node={c} depth={depth + 1} selected={selected} onSelect={onSelect} />
      )}
    </div>
  )
}

function VaultSidebar({ selected, onSelect }: { selected: string | null; onSelect: (id: string) => void }) {
  return (
    <div className="flex flex-col flex-shrink-0" style={{ width: 210, background: T.surface, borderRight: `1px solid ${T.border}` }}>
      <div className="flex items-center justify-between px-3 py-2.5 flex-shrink-0" style={{ borderBottom: `1px solid ${T.border}` }}>
        <span className="text-[9px] font-semibold uppercase tracking-[0.14em]" style={{ color: T.muted }}>The Vault</span>
        <div className="flex gap-1">
          {[
            { title: 'New Folder', path: 'M10 4v12M4 10h12' },
            { title: 'Upload', path: 'M10 13V7m0 0L7 10m3-3l3 3M3 17a7 7 0 1114 0H3z' },
          ].map(({ title, path }) => (
            <button key={title} title={title}
              className="w-6 h-6 flex items-center justify-center rounded transition-colors"
              style={{ border: `1px solid ${T.border2}`, color: T.muted }}
              onMouseEnter={e => { (e.currentTarget as HTMLElement).style.color = T.accentLt; (e.currentTarget as HTMLElement).style.borderColor = T.accent }}
              onMouseLeave={e => { (e.currentTarget as HTMLElement).style.color = T.muted; (e.currentTarget as HTMLElement).style.borderColor = T.border2 }}
            >
              <svg className="w-3 h-3" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
                <path d={path}/>
              </svg>
            </button>
          ))}
        </div>
      </div>
      <div className="flex-1 overflow-y-auto py-1.5 px-1 flex flex-col">
        {MOCK_TREE.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center gap-2 px-4 py-8">
            <svg className="w-5 h-5 opacity-20" viewBox="0 0 20 20" fill="currentColor" style={{ color: T.text }}>
              <path fillRule="evenodd" d="M2 6a2 2 0 012-2h4l2 2h6a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clipRule="evenodd"/>
            </svg>
            <p className="text-[9px] font-mono text-center" style={{ color: T.muted }}>No files yet</p>
          </div>
        ) : (
          MOCK_TREE.map(n => <TreeItem key={n.id} node={n} selected={selected} onSelect={onSelect} />)
        )}
      </div>
      <div className="px-3 py-2 flex-shrink-0" style={{ borderTop: `1px solid ${T.border}` }}>
        <p className="text-[9px] font-mono" style={{ color: T.muted }}>0 files · 0 B</p>
      </div>
    </div>
  )
}

// ─── Mock Document ────────────────────────────────────────────────────────────
const MOCK_DOC_LINES = [
  { bold: true,  text: 'NON-DISCLOSURE AGREEMENT' },
  { bold: false, text: '' },
  { bold: false, text: 'This Non-Disclosure Agreement ("Agreement") is entered into as of March 1, 2026, by and between Authentia Inc., a Delaware corporation ("Disclosing Party"), and the undersigned party ("Receiving Party").' },
  { bold: false, text: '' },
  { bold: true,  text: '1. Definition of Confidential Information' },
  { bold: false, text: 'For purposes of this Agreement, "Confidential Information" means any data or information that is proprietary to the Disclosing Party and not generally known to the public, whether in tangible or intangible form.' },
  { bold: false, text: '' },
  { bold: true,  text: '2. Obligations of Receiving Party' },
  { bold: false, text: 'The Receiving Party agrees to: (a) hold the Confidential Information in strict confidence; (b) not disclose the Confidential Information to third parties; (c) use the Confidential Information solely for the purpose of evaluating a potential business relationship.' },
  { bold: false, text: '' },
  { bold: true,  text: '3. Term and Termination' },
  { bold: false, text: 'This Agreement shall remain in effect for a period of three (3) years from the Effective Date unless earlier terminated by mutual written agreement of the parties.' },
  { bold: false, text: '' },
  { bold: true,  text: '4. Return of Information' },
  { bold: false, text: 'Upon request by the Disclosing Party, the Receiving Party shall promptly return or destroy all materials containing Confidential Information.' },
  { bold: false, text: '' },
  { bold: true,  text: '5. No License' },
  { bold: false, text: 'Nothing in this Agreement grants the Receiving Party any rights in or to the Confidential Information except as expressly set forth herein.' },
]

// ─── Annotations Tab ──────────────────────────────────────────────────────────
function AnnotationsTab({ regions, setRegions }: {
  regions: Region[]; setRegions: (r: Region[]) => void
}) {
  const canvasRef = useRef<HTMLDivElement>(null)
  const drawing = useRef<{ startX: number; startY: number } | null>(null)
  const [draft, setDraft] = useState<{ x: number; y: number; w: number; h: number } | null>(null)
  const [labelTarget, setLabelTarget] = useState<{ rect: { x: number; y: number; w: number; h: number } } | null>(null)
  const [labelInput, setLabelInput] = useState('')

  const getRelXY = (e: React.MouseEvent) => {
    const rect = canvasRef.current!.getBoundingClientRect()
    return { x: e.clientX - rect.left, y: e.clientY - rect.top }
  }

  const onMouseDown = (e: React.MouseEvent) => {
    const { x, y } = getRelXY(e)
    drawing.current = { startX: x, startY: y }
    setDraft({ x, y, w: 0, h: 0 })
  }
  const onMouseMove = (e: React.MouseEvent) => {
    if (!drawing.current) return
    const { x, y } = getRelXY(e)
    const sx = drawing.current.startX, sy = drawing.current.startY
    setDraft({ x: Math.min(x, sx), y: Math.min(y, sy), w: Math.abs(x - sx), h: Math.abs(y - sy) })
  }
  const onMouseUp = () => {
    if (!draft || draft.w < 8 || draft.h < 8) { drawing.current = null; setDraft(null); return }
    drawing.current = null
    setLabelTarget({ rect: draft })
    setDraft(null)
    setLabelInput('')
  }
  const confirmLabel = () => {
    if (!labelTarget) return
    setRegions([...regions, { id: uid(), ...labelTarget.rect, label: labelInput || 'Region', color: T.red }])
    setLabelTarget(null)
  }

  return (
    <div className="flex-1 flex min-h-0 overflow-hidden">
      {/* Document + drawing canvas */}
      <div className="flex-1 overflow-auto flex flex-col items-center py-8" style={{ background: '#0e0e16' }}>
        <div className="relative" style={{ width: 680 }}>
          {/* Paper */}
          <div
            ref={canvasRef}
            className="relative rounded-sm select-none"
            style={{ background: '#1a1a26', border: `1px solid ${T.border2}`, padding: '48px 56px', cursor: 'crosshair' }}
            onMouseDown={onMouseDown}
            onMouseMove={onMouseMove}
            onMouseUp={onMouseUp}
          >
            {MOCK_DOC_LINES.map((line, i) => (
              <p key={i} className="leading-relaxed mb-1"
                style={{ fontWeight: line.bold ? 700 : 400, fontSize: line.bold ? 13 : 12, color: line.bold ? T.text : '#9090b0', fontFamily: 'Georgia, serif', minHeight: 16 }}>
                {line.text}
              </p>
            ))}

            {/* Saved regions */}
            {regions.map(r => (
              <div key={r.id}
                className="absolute pointer-events-none rounded-sm"
                style={{ left: r.x, top: r.y, width: r.w, height: r.h, border: `1.5px solid ${r.color}`, background: `${r.color}18` }}>
                <span className="absolute -top-4 left-0 text-[9px] font-mono px-1 rounded"
                  style={{ background: r.color, color: '#fff' }}>{r.label}</span>
              </div>
            ))}

            {/* Draft rect */}
            {draft && draft.w > 2 && draft.h > 2 && (
              <div className="absolute pointer-events-none rounded-sm"
                style={{ left: draft.x, top: draft.y, width: draft.w, height: draft.h, border: `1.5px dashed ${T.red}`, background: `${T.red}12` }} />
            )}

            {/* Label popup */}
            {labelTarget && (
              <div
                className="absolute z-30 flex gap-1.5 p-2 rounded-lg shadow-xl"
                style={{ left: labelTarget.rect.x, top: labelTarget.rect.y + labelTarget.rect.h + 6, background: T.surface2, border: `1px solid ${T.border2}`, minWidth: 180 }}
                onClick={e => e.stopPropagation()}
              >
                <input
                  autoFocus
                  value={labelInput}
                  onChange={e => setLabelInput(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter') confirmLabel(); if (e.key === 'Escape') setLabelTarget(null) }}
                  placeholder="Label (Enter to save)"
                  className="flex-1 text-[11px] font-mono px-2 py-1 rounded outline-none"
                  style={{ background: T.bg, border: `1px solid ${T.border2}`, color: T.text }}
                />
                <button onClick={confirmLabel}
                  className="px-2 py-1 rounded text-[10px] font-bold text-white"
                  style={{ background: T.red }}>✓</button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Annotation list */}
      <div className="w-52 flex-shrink-0 flex flex-col" style={{ background: T.surface, borderLeft: `1px solid ${T.border}` }}>
        <div className="px-3 py-2.5 flex-shrink-0 flex items-center justify-between" style={{ borderBottom: `1px solid ${T.border}` }}>
          <span className="text-[9px] font-semibold uppercase tracking-widest" style={{ color: T.muted }}>Regions</span>
          <span className="text-[9px] font-mono" style={{ color: T.muted }}>{regions.length}</span>
        </div>
        {regions.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center gap-2 p-4">
            <svg className="w-6 h-6 opacity-20" style={{ color: T.red }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 9h6v6H9z"/></svg>
            <p className="text-[10px] text-center" style={{ color: T.muted }}>Click and drag to draw annotation regions</p>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto py-2">
            {regions.map((r, i) => (
              <div key={r.id} className="flex items-start gap-2 px-3 py-2 group">
                <div className="w-2.5 h-2.5 rounded-sm flex-shrink-0 mt-0.5" style={{ background: r.color }} />
                <div className="flex-1 min-w-0">
                  <p className="text-[11px] font-mono truncate" style={{ color: T.text }}>{r.label}</p>
                  <p className="text-[9px] font-mono" style={{ color: T.muted }}>
                    {Math.round(r.x)},{Math.round(r.y)} · {Math.round(r.w)}×{Math.round(r.h)}
                  </p>
                </div>
                <button onClick={() => setRegions(regions.filter((_, j) => j !== i))}
                  className="opacity-0 group-hover:opacity-100 text-[10px] transition-opacity"
                  style={{ color: T.muted }}>×</button>
              </div>
            ))}
          </div>
        )}
        <div className="px-3 py-2.5 flex-shrink-0" style={{ borderTop: `1px solid ${T.border}` }}>
          <button
            onClick={() => setRegions([])}
            className="w-full text-[10px] py-1 rounded transition-colors"
            style={{ color: T.muted, border: `1px solid ${T.border2}` }}
            onMouseEnter={e => { (e.currentTarget as HTMLElement).style.borderColor = T.red; (e.currentTarget as HTMLElement).style.color = T.red }}
            onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = T.border2; (e.currentTarget as HTMLElement).style.color = T.muted }}
          >
            Clear all
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── Viewer Tab (clean) ───────────────────────────────────────────────────────
function ViewerTab() {
  return (
    <div className="flex-1 overflow-auto flex flex-col items-center py-8" style={{ background: '#0e0e16' }}>
      <div style={{ width: 680, background: '#1a1a26', border: `1px solid ${T.border2}`, padding: '48px 56px', borderRadius: 2 }}>
        {MOCK_DOC_LINES.map((line, i) => (
          <p key={i} className="leading-relaxed mb-1"
            style={{ fontWeight: line.bold ? 700 : 400, fontSize: line.bold ? 13 : 12, color: line.bold ? T.text : '#9090b0', fontFamily: 'Georgia, serif', minHeight: 16 }}>
            {line.text}
          </p>
        ))}
      </div>
    </div>
  )
}

// ─── Metadata Tab ─────────────────────────────────────────────────────────────
function MetadataTab() {
  const rows = [
    ['Filename', 'nda_draft_v3.pdf'], ['Type', 'PDF Document'], ['Size', '184 KB'],
    ['Pages', '8'], ['Created', '2026-03-01'], ['Modified', '2026-03-29'],
    ['SHA-256', 'a3f9e2...c81d'], ['Author', 'Authentia Legal'], ['Language', 'en-US'],
  ]
  return (
    <div className="flex-1 overflow-auto p-6" style={{ background: '#0e0e16' }}>
      <div className="max-w-xl mx-auto">
        <p className="text-[9px] font-semibold uppercase tracking-widest mb-4" style={{ color: T.muted }}>Document Metadata</p>
        <div className="rounded-xl overflow-hidden" style={{ border: `1px solid ${T.border}` }}>
          {rows.map(([k, v], i) => (
            <div key={k} className="flex" style={{ borderBottom: i < rows.length - 1 ? `1px solid ${T.border}` : undefined }}>
              <div className="w-32 px-4 py-2.5 flex-shrink-0" style={{ background: T.surface }}>
                <p className="text-[10px] font-mono" style={{ color: T.muted }}>{k}</p>
              </div>
              <div className="flex-1 px-4 py-2.5" style={{ background: T.bg }}>
                <p className="text-[11px] font-mono" style={{ color: T.text }}>{v}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// ─── Audit Trail Tab ──────────────────────────────────────────────────────────
function AuditTab() {
  const events = [
    { time: '2026-03-29 14:32', actor: 'pratham@authentia.ai', action: 'Opened document', icon: '👁' },
    { time: '2026-03-29 14:30', actor: 'system', action: 'Indexing complete — 142 chunks', icon: '⚙' },
    { time: '2026-03-29 14:29', actor: 'pratham@authentia.ai', action: 'Uploaded nda_draft_v3.pdf', icon: '⬆' },
    { time: '2026-03-01 09:00', actor: 'legal@corp.com', action: 'Document created', icon: '✦' },
  ]
  return (
    <div className="flex-1 overflow-auto p-6" style={{ background: '#0e0e16' }}>
      <div className="max-w-xl mx-auto space-y-3">
        <p className="text-[9px] font-semibold uppercase tracking-widest mb-4" style={{ color: T.muted }}>Audit Trail</p>
        {events.map((ev, i) => (
          <div key={i} className="flex gap-3 items-start">
            <div className="w-6 h-6 rounded-full flex items-center justify-center text-[11px] flex-shrink-0 mt-0.5"
              style={{ background: T.surface2, border: `1px solid ${T.border}` }}>
              {ev.icon}
            </div>
            <div className="flex-1 pb-3" style={{ borderBottom: i < events.length - 1 ? `1px solid ${T.border}` : undefined }}>
              <p className="text-[11px]" style={{ color: T.text }}>{ev.action}</p>
              <p className="text-[9px] font-mono mt-0.5" style={{ color: T.muted }}>
                {ev.time} · {ev.actor}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── Document View (center) ───────────────────────────────────────────────────
function DocumentView({ regions, setRegions }: {
  regions: Region[]; setRegions: (r: Region[]) => void
}) {
  const [tab, setTab] = useState<DocTab>('annotations')
  const DOC_TABS: { id: DocTab; label: string }[] = [
    { id: 'annotations', label: 'Annotations' },
    { id: 'viewer', label: 'Document Viewer' },
    { id: 'metadata', label: 'Metadata' },
    { id: 'audit', label: 'Audit Trail' },
  ]
  return (
    <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
      {/* Sub-tabs */}
      <div className="flex items-center flex-shrink-0 px-4" style={{ background: T.surface, borderBottom: `1px solid ${T.border}`, height: 38 }}>
        {DOC_TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className="relative px-3.5 py-2 text-[11px] font-medium flex-shrink-0 transition-colors h-full flex items-center"
            style={{ color: tab === t.id ? T.accentLt : T.muted }}
          >
            {t.label}
            {tab === t.id && (
              <motion.div layoutId="doc-tab-ind" className="absolute bottom-0 left-0 right-0 h-[2px]"
                style={{ background: T.accent }} />
            )}
          </button>
        ))}
        {/* Region count badge */}
        {tab === 'annotations' && regions.length > 0 && (
          <span className="ml-auto text-[9px] font-mono px-1.5 py-0.5 rounded-full"
            style={{ background: `${T.red}20`, color: T.red, border: `1px solid ${T.red}40` }}>
            {regions.length} region{regions.length > 1 ? 's' : ''}
          </span>
        )}
      </div>
      {/* Tab content */}
      <AnimatePresence mode="wait">
        <motion.div key={tab} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          transition={{ duration: 0.1 }} className="flex-1 flex flex-col min-h-0 overflow-hidden">
          {tab === 'annotations' && <AnnotationsTab regions={regions} setRegions={setRegions} />}
          {tab === 'viewer'      && <ViewerTab />}
          {tab === 'metadata'    && <MetadataTab />}
          {tab === 'audit'       && <AuditTab />}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}

// ─── Workflow Canvas — Step 1 (Source Folder only) ────────────────────────────
function WorkflowStep1({ contractName, onProceed }: { contractName?: string; onProceed: () => void }) {
  return (
    <div
      className="flex-1 flex flex-col items-center justify-center overflow-hidden"
      style={{
        background: T.bg,
        backgroundImage: `radial-gradient(circle, rgba(124,58,237,0.10) 1px, transparent 1px)`,
        backgroundSize: '28px 28px',
      }}
    >
      <style>{MARCH_CSS}</style>

      {/* Source folder node */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 12 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
        className="rounded-2xl overflow-hidden"
        style={{
          width: 320,
          background: T.surface2,
          border: `1px solid ${T.border2}`,
          boxShadow: '0 8px 40px rgba(0,0,0,0.6)',
        }}
      >
        {/* Top stripe */}
        <div className="h-0.5" style={{ background: `linear-gradient(90deg, #facc15, #f59e0b)` }} />
        <div className="p-5">
          {/* Header */}
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
              style={{ background: 'rgba(250,204,21,0.1)', border: '1px solid rgba(250,204,21,0.25)' }}>
              📁
            </div>
            <div>
              <p className="text-[14px] font-semibold" style={{ color: T.text }}>Source Folder</p>
              <p className="text-[11px] font-mono" style={{ color: T.muted }}>{contractName ?? 'Contract Package'}</p>
            </div>
            <div className="ml-auto">
              <span className="text-[9px] font-mono px-1.5 py-0.5 rounded-full"
                style={{ background: 'rgba(90,90,120,0.15)', color: T.muted, border: `1px solid ${T.border2}` }}>
                empty
              </span>
            </div>
          </div>

          {/* Empty state / upload area */}
          <div
            className="rounded-lg flex flex-col items-center justify-center gap-2 py-6 mb-4"
            style={{ border: `1px dashed ${T.border2}`, background: T.bg }}
          >
            <svg className="w-6 h-6 opacity-25" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} style={{ color: T.text }}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 16v-8m0 0l-3 3m3-3l3 3M3 17a9 9 0 1018 0"/>
            </svg>
            <p className="text-[10px] font-mono text-center" style={{ color: T.muted }}>
              No documents yet.<br/>Upload files to get started.
            </p>
          </div>

          {/* Proceed button */}
          <motion.button
            onClick={onProceed}
            whileHover={{ scale: 1.02, boxShadow: '0 0 20px rgba(124,58,237,0.4)' }}
            whileTap={{ scale: 0.97 }}
            className="w-full py-2.5 rounded-xl text-[12px] font-semibold text-white flex items-center justify-center gap-2"
            style={{ background: `linear-gradient(135deg, ${T.accent}, ${T.accentLt})` }}
          >
            Proceed to Step 2
            <svg className="w-3.5 h-3.5" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 10h12M11 5l5 5-5 5"/>
            </svg>
          </motion.button>
        </div>
      </motion.div>

      {/* Hint */}
      <p className="mt-6 text-[10px] font-mono" style={{ color: T.muted, opacity: 0.5 }}>
        Upload documents then proceed to analysis
      </p>
    </div>
  )
}

// ─── Workflow Canvas — Step 2 (full flow) ─────────────────────────────────────
function WorkflowStep2({ selectedNode, setSelectedNode }: {
  selectedNode: string | null; setSelectedNode: (id: string | null) => void
}) {
  const NODE_X = 52, NODE_Y_START = 60, GAP = 110
  const NODE_W = 192, NODE_H = 72
  const AGENT_X = 388, AGENT_Y = 120

  return (
    <div
      className="flex-1 overflow-auto"
      style={{
        background: T.bg,
        backgroundImage: `radial-gradient(circle, rgba(124,58,237,0.10) 1px, transparent 1px)`,
        backgroundSize: '28px 28px',
      }}
    >
      <style>{MARCH_CSS}</style>

      {/* Badge */}
      <div className="absolute top-3 right-3 z-10">
        <div className="px-2.5 py-1 rounded-lg text-[10px] font-mono"
          style={{ background: T.surface2, border: `1px solid ${T.border}`, color: T.muted }}>
          Step 2 · Analysis Mode
        </div>
      </div>

      <div className="relative" style={{ width: 720, height: 500 }}>
        {/* SVG lines */}
        <svg className="absolute inset-0 pointer-events-none overflow-visible" style={{ width: '100%', height: '100%' }}>
          {CANVAS_DOCS.map((doc, i) => {
            const fx = NODE_X + NODE_W, fy = NODE_Y_START + i * GAP + NODE_H / 2
            const tx = AGENT_X, ty = AGENT_Y + 88
            const mx = (fx + tx) / 2
            const path = `M ${fx} ${fy} C ${mx} ${fy}, ${mx} ${ty}, ${tx} ${ty}`
            const active = selectedNode === doc.id
            return (
              <g key={doc.id}>
                <path d={path} fill="none" stroke={T.border} strokeWidth={1} strokeDasharray="4 4" className="march" opacity={0.35}/>
                <path d={path} fill="none" stroke={active ? T.accent : '#4c1d95'} strokeWidth={active ? 1.5 : 1}
                  strokeDasharray="4 4" className="march" opacity={active ? 1 : 0.4}/>
                <circle cx={tx} cy={ty} r={2.5} fill={active ? T.accent : '#4c1d95'} opacity={active ? 1 : 0.5}/>
              </g>
            )
          })}
        </svg>

        {/* Document nodes */}
        {CANVAS_DOCS.map((doc, i) => {
          const color = extColor(doc.ext)
          const isSel = selectedNode === doc.id
          return (
            <motion.button
              key={doc.id}
              className="absolute rounded-xl text-left overflow-hidden"
              style={{
                left: NODE_X, top: NODE_Y_START + i * GAP, width: NODE_W,
                background: T.surface2,
                border: `1px solid ${isSel ? T.accent : T.border}`,
                boxShadow: isSel ? `0 0 0 1px ${T.accent}, 0 4px 20px rgba(124,58,237,0.2)` : '0 2px 12px rgba(0,0,0,0.4)',
              }}
              whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
              onClick={() => setSelectedNode(isSel ? null : doc.id)}
            >
              <div className="h-0.5" style={{ background: color }} />
              <div className="px-3 py-2.5 flex items-center gap-2">
                <div className="w-6 h-6 rounded-md flex items-center justify-center text-[9px] font-bold flex-shrink-0"
                  style={{ background: color + '22', border: `1px solid ${color}44`, color }}>
                  {doc.ext.toUpperCase().slice(0, 3)}
                </div>
                <p className="text-[11px] font-mono truncate flex-1" style={{ color: T.text }}>{doc.name}</p>
              </div>
              <div className="px-3 pb-2.5 flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                <p className="text-[9px] font-mono" style={{ color: T.muted }}>indexed · ready</p>
              </div>
            </motion.button>
          )
        })}

        {/* Agent node */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="absolute rounded-xl overflow-hidden"
          style={{ left: AGENT_X, top: AGENT_Y, width: 240, background: T.surface2, border: `1px solid ${T.accent}`, boxShadow: `0 0 0 1px ${T.accent}33, 0 8px 32px rgba(124,58,237,0.25)` }}
        >
          <div className="h-0.5" style={{ background: `linear-gradient(90deg, ${T.accent}, ${T.accentLt})` }} />
          <div className="p-4">
            <div className="flex items-center gap-2.5 mb-3">
              <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                style={{ background: `linear-gradient(135deg, ${T.accent}, ${T.accentLt})` }}>
                <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17H3a2 2 0 01-2-2V5a2 2 0 012-2h14a2 2 0 012 2v10a2 2 0 01-2 2h-2"/></svg>
              </div>
              <div>
                <p className="text-[13px] font-semibold" style={{ color: T.text }}>AI Agent</p>
                <p className="text-[9px] font-mono" style={{ color: T.accentLt }}>Contract Analyzer</p>
              </div>
            </div>
            <div className="space-y-1.5 text-[9px] font-mono" style={{ color: T.muted }}>
              <div className="flex justify-between"><span>model</span><span style={{ color: '#c4b5fd' }}>claude-sonnet-4-6</span></div>
              <div className="flex justify-between"><span>documents</span><span style={{ color: '#c4b5fd' }}>3 attached</span></div>
              <div className="flex justify-between"><span>status</span><span style={{ color: '#34d399' }}>ready</span></div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

// ─── Splitter ─────────────────────────────────────────────────────────────────
function Splitter({ onMouseDown }: { onMouseDown: () => void }) {
  const [hov, setHov] = useState(false)
  return (
    <div
      onMouseDown={onMouseDown}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      className="relative flex-shrink-0 transition-colors"
      style={{ width: 2, cursor: 'col-resize', background: hov ? T.accentLt : T.accent, opacity: hov ? 1 : 0.65, zIndex: 40 }}
    >
      <div className="absolute inset-y-0 -left-2 -right-2" />
      <AnimatePresence>
        {hov && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="absolute inset-y-0 flex flex-col items-center justify-center gap-1 pointer-events-none">
            {[0,1,2,3,4].map(i => <div key={i} className="w-[3px] h-[3px] rounded-full bg-white/80" />)}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// ─── Right Pane ───────────────────────────────────────────────────────────────
const RIGHT_TABS: { id: RightTab; label: string }[] = [
  { id: 'pearl', label: 'Pearl' },
  { id: 'configure', label: 'Configure' },
  { id: 'code', label: 'Code' },
  { id: 'console', label: 'Console' },
  { id: 'history', label: 'History' },
]

function Placeholder({ icon, title, sub }: { icon: string; title: string; sub: string }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-3 p-6">
      <div className="text-2xl opacity-30">{icon}</div>
      <p className="text-[12px] font-medium text-center" style={{ color: T.muted }}>{title}</p>
      <p className="text-[10px] text-center max-w-[180px]" style={{ color: T.muted, opacity: 0.6 }}>{sub}</p>
    </div>
  )
}

function RightPane({ activeTab, setActiveTab }: { activeTab: RightTab; setActiveTab: (t: RightTab) => void }) {
  return (
    <div className="flex flex-col min-w-0 overflow-hidden" style={{ background: T.surface, borderLeft: `1px solid ${T.border}` }}>
      {/* Tab bar */}
      <div className="flex flex-shrink-0 overflow-x-auto" style={{ background: T.bg, borderBottom: `1px solid ${T.border}`, height: 38 }}>
        {RIGHT_TABS.map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)}
            className="relative px-3.5 h-full text-[11px] font-medium flex-shrink-0 transition-colors"
            style={{ color: activeTab === tab.id ? T.accentLt : T.muted }}>
            {tab.label}
            {activeTab === tab.id && (
              <motion.div layoutId="rt-ind" className="absolute bottom-0 left-0 right-0 h-[2px]" style={{ background: T.accent }} />
            )}
          </button>
        ))}
      </div>
      {/* Content */}
      <AnimatePresence mode="wait">
        <motion.div key={activeTab} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          transition={{ duration: 0.1 }} className="flex-1 flex flex-col min-h-0 overflow-hidden">
          {activeTab === 'pearl'     && <Placeholder icon="◎" title="Pearl Analysis" sub="Run the agent to see AI-generated risk insights." />}
          {activeTab === 'configure' && <Placeholder icon="⚙" title="Configure" sub="Model settings and pipeline configuration." />}
          {activeTab === 'code'      && <Placeholder icon="</>" title="Code View" sub="Generated API code appears here after analysis." />}
          {activeTab === 'console'   && (
            <div className="flex-1 flex flex-col overflow-hidden" style={{ background: '#050508' }}>
              <div className="flex items-center gap-2 px-3 py-1.5 flex-shrink-0" style={{ borderBottom: `1px solid ${T.border}`, background: T.surface }}>
                <div className="flex gap-1.5">
                  {['#ff5f57','#febc2e','#28c840'].map(c => <div key={c} className="w-2 h-2 rounded-full" style={{ background: c }} />)}
                </div>
                <span className="text-[9px] font-mono ml-2" style={{ color: T.muted }}>console — authentia</span>
              </div>
              <div className="flex-1 p-4 font-mono text-[11px]" style={{ color: '#4ade80' }}>
                <p style={{ color: T.muted, opacity: 0.5 }}>Authentia Console v1.0.0 — Ready</p>
                <p style={{ color: T.muted, opacity: 0.3 }} className="mb-4">Run an analysis to see execution output here.</p>
                <div className="flex items-center gap-1">
                  <span style={{ color: T.accent }}>❯</span>
                  <span style={{ color: T.muted }}>$</span>
                  <span className="blink ml-1" style={{ color: '#4ade80' }}>_</span>
                </div>
              </div>
            </div>
          )}
          {activeTab === 'history'   && <Placeholder icon="◷" title="No Run History" sub="Past analysis runs will appear here." />}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}

// ─── Main export ──────────────────────────────────────────────────────────────
export function ContractBuilder(_props: { contractId?: string; contractName?: string; token?: string }) {
  const [step, setStep] = useState<Step>(1)
  const [view, setView] = useState<View>('workflow')
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [activeRightTab, setActiveRightTab] = useState<RightTab>('console')
  const [regions, setRegions] = useState<Region[]>([])
  const [rightWidth, setRightWidth] = useState(340)
  const [vaultOpen, setVaultOpen] = useState(false)
  const isDragging = useRef(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const showRightPane = step === 2

  // When file selected, switch to Document View (no right pane)
  const handleFileSelect = (id: string) => {
    setSelectedFile(id)
    setView('document')
  }

  const onSplitterDown = useCallback(() => {
    isDragging.current = true
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }, [])

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!isDragging.current || !containerRef.current) return
      const fromRight = containerRef.current.getBoundingClientRect().right - e.clientX
      setRightWidth(Math.min(560, Math.max(260, fromRight)))
    }
    const onUp = () => { isDragging.current = false; document.body.style.cursor = ''; document.body.style.userSelect = '' }
    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
    return () => { document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp) }
  }, [])

  return (
    <div ref={containerRef} className="flex flex-col w-full h-full overflow-hidden"
      style={{ background: T.bg, fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif' }}>

      {/* Top Nav */}
      <TopNav step={step} view={view} setView={setView} />

      {/* Body */}
      <div className="flex flex-1 min-h-0 overflow-hidden">
        {/* Vault toggle strip */}
        <div
          className="flex flex-col flex-shrink-0 items-center pt-3 gap-2"
          style={{ width: 36, background: T.surface, borderRight: `1px solid ${T.border}` }}
        >
          <button
            onClick={() => setVaultOpen(o => !o)}
            title={vaultOpen ? 'Hide Vault' : 'Show Vault'}
            className="w-6 h-6 flex items-center justify-center rounded transition-colors"
            style={{ color: vaultOpen ? T.accentLt : T.muted, background: vaultOpen ? `${T.accent}22` : 'transparent' }}
            onMouseEnter={e => { if (!vaultOpen) (e.currentTarget as HTMLElement).style.color = T.text }}
            onMouseLeave={e => { if (!vaultOpen) (e.currentTarget as HTMLElement).style.color = T.muted }}
          >
            <svg className="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M2 6a2 2 0 012-2h4l2 2h6a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clipRule="evenodd"/>
            </svg>
          </button>
        </div>

        {/* Vault */}
        {vaultOpen && <VaultSidebar selected={selectedFile} onSelect={handleFileSelect} />}

        {/* Center */}
        <AnimatePresence mode="wait">
          {view === 'document' ? (
            <motion.div key="doc" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }} className="flex-1 flex flex-col min-w-0 overflow-hidden">
              <DocumentView regions={regions} setRegions={setRegions} />
            </motion.div>
          ) : step === 1 ? (
            <motion.div key="wf1" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }} className="flex-1 flex min-w-0 overflow-hidden relative">
              <WorkflowStep1 contractName={_props.contractName} onProceed={() => setStep(2)} />
            </motion.div>
          ) : (
            <motion.div key="wf2" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }} className="flex-1 flex min-w-0 overflow-hidden relative">
              <WorkflowStep2 selectedNode={selectedNode} setSelectedNode={setSelectedNode} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Splitter + Right Pane (only in doc view or step 2) */}
        <AnimatePresence>
          {showRightPane && (
            <motion.div key="right" initial={{ width: 0, opacity: 0 }} animate={{ width: rightWidth, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }} transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="flex flex-shrink-0 min-w-0 overflow-hidden">
              <Splitter onMouseDown={onSplitterDown} />
              <div style={{ flex: 1, minWidth: 0 }} className="flex flex-col overflow-hidden">
                <RightPane activeTab={activeRightTab} setActiveTab={setActiveRightTab} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
