import { useState, useRef, useCallback } from 'react'

interface BoundingBox {
  id: string
  label: string
  x: number   // % of image width
  y: number   // % of image height
  w: number   // % of image width
  h: number   // % of image height
}

interface Draft {
  startX: number
  startY: number
  x: number
  y: number
  w: number
  h: number
}

interface Props {
  /** URL of the PDF page rendered as an image */
  imageUrl: string
  /** Optional initial boxes */
  initialBoxes?: BoundingBox[]
  onChange?: (boxes: BoundingBox[]) => void
}

function genId() {
  return Math.random().toString(36).slice(2, 9)
}

export function PDFAnnotationLayer({ imageUrl, initialBoxes = [], onChange }: Props) {
  const [boxes, setBoxes] = useState<BoundingBox[]>(initialBoxes)
  const [draft, setDraft] = useState<Draft | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editLabel, setEditLabel] = useState('')
  const [copied, setCopied] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const isDragging = useRef(false)

  const getRel = useCallback((clientX: number, clientY: number) => {
    const rect = containerRef.current!.getBoundingClientRect()
    return {
      x: Math.max(0, Math.min(100, (clientX - rect.left) / rect.width * 100)),
      y: Math.max(0, Math.min(100, (clientY - rect.top) / rect.height * 100)),
    }
  }, [])

  const onMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('[data-box]')) return
    e.preventDefault()
    const { x, y } = getRel(e.clientX, e.clientY)
    isDragging.current = true
    setDraft({ startX: x, startY: y, x, y, w: 0, h: 0 })
    setEditingId(null)
  }

  const onMouseMove = (e: React.MouseEvent) => {
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
  }

  const onMouseUp = () => {
    if (!isDragging.current || !draft) return
    isDragging.current = false
    if (draft.w < 1 || draft.h < 1) { setDraft(null); return }
    const newBox: BoundingBox = { id: genId(), label: '', x: draft.x, y: draft.y, w: draft.w, h: draft.h }
    const updated = [...boxes, newBox]
    setBoxes(updated)
    onChange?.(updated)
    setDraft(null)
    setEditingId(newBox.id)
    setEditLabel('')
  }

  const confirmLabel = (id: string) => {
    const updated = boxes.map(b => b.id === id ? { ...b, label: editLabel.trim() || `Region_${boxes.findIndex(b2 => b2.id === id) + 1}` } : b)
    setBoxes(updated)
    onChange?.(updated)
    setEditingId(null)
  }

  const deleteBox = (id: string) => {
    const updated = boxes.filter(b => b.id !== id)
    setBoxes(updated)
    onChange?.(updated)
    if (editingId === id) setEditingId(null)
  }

  const exportJSON = () => {
    const data = boxes.map(({ id, label, x, y, w, h }) => ({
      id, label,
      x: +x.toFixed(2), y: +y.toFixed(2),
      w: +w.toFixed(2), h: +h.toFixed(2),
    }))
    navigator.clipboard.writeText(JSON.stringify(data, null, 2))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="flex flex-col h-full bg-[#f4f4f0] select-none">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-white border-b border-black/10 flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#6f8f88]" />
          <span className="text-sm font-semibold text-[#1a1a1a]">PDF Annotation Layer</span>
          <span className="text-xs text-[#888] ml-2">Click and drag to draw regions</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-[#888]">{boxes.length} region{boxes.length !== 1 ? 's' : ''}</span>
          <button
            onClick={exportJSON}
            className="text-xs px-3 py-1.5 rounded-lg bg-[#1a1a1a] text-white hover:bg-[#2a2a2a] transition-colors flex items-center gap-1.5"
          >
            {copied ? (
              <>
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7"/>
                </svg>
                Copied!
              </>
            ) : (
              <>
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                </svg>
                Export JSON
              </>
            )}
          </button>
        </div>
      </div>

      {/* Canvas area */}
      <div className="flex-1 overflow-auto flex items-start justify-center p-6">
        <div
          ref={containerRef}
          className="relative inline-block cursor-crosshair"
          style={{ lineHeight: 0 }}
          onMouseDown={onMouseDown}
          onMouseMove={onMouseMove}
          onMouseUp={onMouseUp}
          onMouseLeave={onMouseUp}
        >
          <img
            src={imageUrl}
            alt="PDF page"
            className="block max-w-full shadow-lg border border-black/10"
            draggable={false}
          />

          {/* Committed boxes */}
          {boxes.map((box, idx) => (
            <div
              key={box.id}
              data-box="1"
              className="absolute"
              style={{ left: `${box.x}%`, top: `${box.y}%`, width: `${box.w}%`, height: `${box.h}%` }}
            >
              {/* Fill */}
              <div className="absolute inset-0 bg-red-500/15 border border-red-500/60 rounded-[2px]" />

              {/* Label chip */}
              <div className="absolute -top-5 left-0 flex items-center gap-1">
                <span className="bg-red-500 text-white text-[10px] font-mono px-1.5 py-0.5 rounded whitespace-nowrap leading-none">
                  {box.label || `Region_${idx + 1}`}
                </span>
                <button
                  onClick={() => deleteBox(box.id)}
                  className="w-4 h-4 bg-white border border-red-300 rounded text-red-500 flex items-center justify-center hover:bg-red-50 transition-colors text-[10px] leading-none"
                >
                  ×
                </button>
              </div>

              {/* Edit label overlay */}
              {editingId === box.id && (
                <div className="absolute top-full left-0 mt-1 z-50" onClick={e => e.stopPropagation()}>
                  <div className="flex items-center gap-1 bg-white border border-black/15 rounded-lg shadow-lg px-2 py-1.5">
                    <input
                      autoFocus
                      value={editLabel}
                      onChange={e => setEditLabel(e.target.value)}
                      onKeyDown={e => { if (e.key === 'Enter') confirmLabel(box.id); if (e.key === 'Escape') setEditingId(null) }}
                      placeholder={`Region_${idx + 1}`}
                      className="text-xs font-mono outline-none w-32 text-[#1a1a1a] placeholder:text-[#bbb]"
                    />
                    <button
                      onClick={() => confirmLabel(box.id)}
                      className="text-[10px] px-1.5 py-0.5 bg-[#1a1a1a] text-white rounded hover:bg-[#333] transition-colors"
                    >
                      Set
                    </button>
                  </div>
                </div>
              )}

              {/* Click box to re-edit label */}
              {editingId !== box.id && (
                <div
                  className="absolute inset-0 cursor-pointer"
                  onClick={e => { e.stopPropagation(); setEditingId(box.id); setEditLabel(box.label) }}
                />
              )}
            </div>
          ))}

          {/* Draft box */}
          {draft && draft.w > 0.5 && draft.h > 0.5 && (
            <div
              className="absolute pointer-events-none"
              style={{ left: `${draft.x}%`, top: `${draft.y}%`, width: `${draft.w}%`, height: `${draft.h}%` }}
            >
              <div className="absolute inset-0 bg-red-500/20 border-2 border-red-500 border-dashed rounded-[2px]" />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
