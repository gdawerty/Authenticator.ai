import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.min.css'

const API_BASE_URL = 'http://localhost:8002/api/v1'

// Programming / markup / config extensions → rendered with syntax highlighting
const CODE_EXTENSIONS = new Set([
  'js','jsx','ts','tsx','py','rb','java','c','cpp','h','hpp','cs','go','rs',
  'swift','kt','scala','php','sh','bash','zsh','fish','ps1',
  'html','htm','xml','svg','css','scss','sass','less',
  'json','yaml','yml','toml','ini','cfg','conf','env',
  'sql','graphql','gql','dockerfile','makefile','gitignore',
  'r','m','lua','dart','ex','exs','clj','hs','elm','vue',
])

// Plain prose → raw text, selectable
const TEXT_EXTENSIONS = new Set(['txt','md','markdown','rst','csv','tsv','log'])

const IMAGE_EXTENSIONS = new Set(['png','jpg','jpeg','gif','webp','svg','bmp','ico','tiff'])

function getFileCategory(filename: string): 'pdf' | 'image' | 'text' | 'code' | 'video' | 'audio' | 'docx' | 'other' {
  const ext = filename.split('.').pop()?.toLowerCase() ?? ''
  if (ext === 'pdf') return 'pdf'
  if (ext === 'docx' || ext === 'doc') return 'docx'
  if (IMAGE_EXTENSIONS.has(ext)) return 'image'
  if (CODE_EXTENSIONS.has(ext)) return 'code'
  if (TEXT_EXTENSIONS.has(ext)) return 'text'
  if (['mp4','mov','avi','webm','mkv'].includes(ext)) return 'video'
  if (['mp3','wav','ogg','flac','aac'].includes(ext)) return 'audio'
  return 'other'
}

// VS Code-style icon colors per extension
const EXT_COLORS: Record<string, { bg: string; fg: string; label?: string }> = {
  pdf:  { bg: '#e53935', fg: '#fff', label: 'PDF' },
  py:   { bg: '#3572A5', fg: '#fff', label: 'PY' },
  js:   { bg: '#F7DF1E', fg: '#222', label: 'JS' },
  jsx:  { bg: '#61DAFB', fg: '#222', label: 'JSX' },
  ts:   { bg: '#3178C6', fg: '#fff', label: 'TS' },
  tsx:  { bg: '#3178C6', fg: '#fff', label: 'TSX' },
  json: { bg: '#CBCB41', fg: '#222', label: 'JSON' },
  html: { bg: '#E34C26', fg: '#fff', label: 'HTML' },
  htm:  { bg: '#E34C26', fg: '#fff', label: 'HTML' },
  css:  { bg: '#563D7C', fg: '#fff', label: 'CSS' },
  scss: { bg: '#c6538c', fg: '#fff', label: 'SCSS' },
  md:   { bg: '#083fa1', fg: '#fff', label: 'MD' },
  markdown: { bg: '#083fa1', fg: '#fff', label: 'MD' },
  yaml: { bg: '#cb171e', fg: '#fff', label: 'YAML' },
  yml:  { bg: '#cb171e', fg: '#fff', label: 'YAML' },
  toml: { bg: '#9c4121', fg: '#fff', label: 'TOML' },
  sh:   { bg: '#4EAA25', fg: '#fff', label: 'SH' },
  bash: { bg: '#4EAA25', fg: '#fff', label: 'SH' },
  zsh:  { bg: '#4EAA25', fg: '#fff', label: 'SH' },
  go:   { bg: '#00ADD8', fg: '#fff', label: 'GO' },
  rs:   { bg: '#DEA584', fg: '#222', label: 'RS' },
  java: { bg: '#B07219', fg: '#fff', label: 'JAVA' },
  c:    { bg: '#555555', fg: '#fff', label: 'C' },
  cpp:  { bg: '#f34b7d', fg: '#fff', label: 'C++' },
  cs:   { bg: '#178600', fg: '#fff', label: 'C#' },
  rb:   { bg: '#701516', fg: '#fff', label: 'RB' },
  php:  { bg: '#4F5D95', fg: '#fff', label: 'PHP' },
  swift:{ bg: '#F05138', fg: '#fff', label: 'SWIFT' },
  kt:   { bg: '#A97BFF', fg: '#fff', label: 'KT' },
  sql:  { bg: '#336791', fg: '#fff', label: 'SQL' },
  vue:  { bg: '#41B883', fg: '#fff', label: 'VUE' },
  r:    { bg: '#198CE7', fg: '#fff', label: 'R' },
  lua:  { bg: '#000080', fg: '#fff', label: 'LUA' },
  dart: { bg: '#00B4AB', fg: '#fff', label: 'DART' },
  // images
  png:  { bg: '#a259ff', fg: '#fff', label: 'PNG' },
  jpg:  { bg: '#a259ff', fg: '#fff', label: 'JPG' },
  jpeg: { bg: '#a259ff', fg: '#fff', label: 'JPG' },
  gif:  { bg: '#a259ff', fg: '#fff', label: 'GIF' },
  svg:  { bg: '#a259ff', fg: '#fff', label: 'SVG' },
  webp: { bg: '#a259ff', fg: '#fff', label: 'WEBP' },
  // media
  mp4:  { bg: '#ff5252', fg: '#fff', label: 'MP4' },
  mov:  { bg: '#ff5252', fg: '#fff', label: 'MOV' },
  mp3:  { bg: '#ff9800', fg: '#fff', label: 'MP3' },
  wav:  { bg: '#ff9800', fg: '#fff', label: 'WAV' },
  // misc
  csv:  { bg: '#207245', fg: '#fff', label: 'CSV' },
  txt:  { bg: '#888', fg: '#fff', label: 'TXT' },
  log:  { bg: '#888', fg: '#fff', label: 'LOG' },
  env:  { bg: '#ecd53f', fg: '#222', label: 'ENV' },
  xml:  { bg: '#e37933', fg: '#fff', label: 'XML' },
  zip:  { bg: '#8B4513', fg: '#fff', label: 'ZIP' },
}

function VsCodeIcon({ filename, size = 52 }: { filename: string; size?: number }) {
  const ext = filename.split('.').pop()?.toLowerCase() ?? ''
  const cfg = EXT_COLORS[ext] ?? { bg: '#607d8b', fg: '#fff', label: ext.toUpperCase().slice(0, 4) || 'FILE' }
  const label = cfg.label ?? (ext.toUpperCase().slice(0, 4) || 'FILE')
  const fold = size * 0.22

  return (
    <svg width={size} height={size * 1.1} viewBox={`0 0 ${size} ${size * 1.1}`} fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Document body */}
      <path
        d={`M4,0 H${size - fold} L${size},${fold} V${size * 1.1 - 4} Q${size},${size * 1.1} ${size - 4},${size * 1.1} H4 Q0,${size * 1.1} 0,${size * 1.1 - 4} V4 Q0,0 4,0 Z`}
        fill="#f0f0eb"
        stroke="#d0d0c8"
        strokeWidth="1"
      />
      {/* Fold corner */}
      <path
        d={`M${size - fold},0 L${size - fold},${fold} L${size},${fold}`}
        fill="#d0d0c8"
        stroke="#c0c0b8"
        strokeWidth="1"
      />
      {/* Color badge at bottom */}
      <rect
        x="0" y={size * 1.1 - size * 0.32}
        width={size} height={size * 0.32}
        rx="0" ry="0"
        fill={cfg.bg}
      />
      {/* Rounded bottom corners on badge */}
      <rect x="0" y={size * 1.1 - 4} width={size} height={4} rx="0" fill={cfg.bg} />
      <rect x="0" y={size * 1.1 - size * 0.32} width={size} height={size * 0.32} rx="0" fill={cfg.bg}
        style={{ borderBottomLeftRadius: 4, borderBottomRightRadius: 4 }}
      />
      {/* Extension label */}
      <text
        x={size / 2} y={size * 1.1 - size * 0.32 / 2 + size * 0.055}
        textAnchor="middle"
        fill={cfg.fg}
        fontSize={label.length > 3 ? size * 0.17 : size * 0.19}
        fontFamily="ui-monospace, SFMono-Regular, Menlo, monospace"
        fontWeight="700"
        letterSpacing="-0.5"
      >
        {label}
      </text>
    </svg>
  )
}

interface DocumentSummary {
  id: string
  original_filename: string
  type: string
  created_at: string
  folder_id: string | null
}

interface FolderNode {
  id: string
  name: string
  parent_id: string | null
  children: FolderNode[]
  documents: DocumentSummary[]
}

interface ContractDetail {
  id: string
  name: string
  status: string
  created_at: string
  folders: FolderNode[]
  root_documents: DocumentSummary[]
}

interface Props {
  contractId: string
  contractName: string
  token: string
  initialFiles?: File[]
  onFileOpen?: (documentId: string) => void
  onClose: () => void
}

type InspectTool = 'highlight' | 'region' | 'annotate' | null

interface ForensicAnnotation {
  id: string
  docId: string
  type: 'text-selection' | 'region' | 'note'
  content: string        // user comment
  excerpt?: string       // selected text (text-selection)
  region?: { x: number; y: number; w: number; h: number }
  timestamp: string
}

interface RegionDraft {
  x: number; y: number; w: number; h: number
  startX: number; startY: number
  active: boolean
}

// ─── Inline create input (VS Code style) ────────────────────────────────────
function InlineCreateInput({
  depth,
  value,
  error,
  onChange,
  onConfirm,
  onCancel,
  inputRef,
}: {
  depth: number
  value: string
  error: string | null
  onChange: (v: string) => void
  onConfirm: () => void
  onCancel: () => void
  inputRef: React.RefObject<HTMLInputElement>
}) {
  return (
    <div style={{ paddingLeft: depth * 16 }}>
      <div className="flex items-center gap-1 px-2 py-0.5">
        <span className="w-3 flex-shrink-0" />
        <span className="text-sm flex-shrink-0">📁</span>
        <div className="flex-1 relative">
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={e => onChange(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !error) onConfirm()
              if (e.key === 'Escape') onCancel()
            }}
            className={`w-full text-sm px-1.5 py-0.5 rounded outline-none border ${
              error
                ? 'border-red-400 bg-red-50/30 dark:bg-red-900/20 text-red-600 dark:text-red-400'
                : 'border-[#6f8f88]/60 bg-white/40 dark:bg-white/10 text-[#1A1A1A] dark:text-white'
            }`}
            placeholder="folder name"
            autoComplete="off"
            spellCheck={false}
          />
          {error && (
            <div className="absolute top-full left-0 mt-0.5 z-10 px-2 py-1 bg-red-500/90 text-white text-[10px] rounded-lg whitespace-nowrap shadow-lg flex items-center gap-1">
              <span>⚠</span> {error}
            </div>
          )}
        </div>
        <button
          onClick={onConfirm}
          disabled={!!error || !value.trim()}
          className="text-[10px] px-1.5 py-0.5 rounded bg-[#6f8f88] text-white disabled:opacity-30 disabled:cursor-not-allowed flex-shrink-0 leading-none"
          title={error ?? 'Create folder'}
        >✓</button>
      </div>
    </div>
  )
}

// ─── Folder tree (folders + files, VS Code style) ────────────────────────────
function FolderTree({
  folders,
  documents,
  parentFolderId,
  selectedDocId,
  expandedIds,
  onToggle,
  onSelectDoc,
  onStartCreating,
  creatingInFolderId,
  creatingName,
  creatingError,
  onCreatingNameChange,
  onCreateConfirm,
  onCreateCancel,
  inlineInputRef,
  // drag-and-drop
  draggedDocId,
  dropTargetId,
  onDocDragStart,
  onDocDragEnd,
  onFolderDrop,
  depth = 0,
}: {
  folders: FolderNode[]
  documents: DocumentSummary[]
  parentFolderId: string | null
  selectedDocId: string | null
  expandedIds: Set<string>
  onToggle: (id: string) => void
  onSelectDoc: (doc: DocumentSummary) => void
  onStartCreating: (parentId: string | null) => void
  creatingInFolderId: string | null | undefined
  creatingName: string
  creatingError: string | null
  onCreatingNameChange: (v: string) => void
  onCreateConfirm: () => void
  onCreateCancel: () => void
  inlineInputRef: React.RefObject<HTMLInputElement>
  draggedDocId: string | null
  dropTargetId: string | 'root' | null
  onDocDragStart: (docId: string) => void
  onDocDragEnd: () => void
  onFolderDrop: (targetFolderId: string | null) => void
  depth?: number
}) {
  const showInputHere = creatingInFolderId !== undefined && creatingInFolderId === parentFolderId
  const indent = depth * 12

  return (
    <div>
      {/* Folder rows */}
      {folders.map(folder => {
        const isExpanded = expandedIds.has(folder.id)
        const hasChildren = folder.children.length > 0 || folder.documents.length > 0
        const creatingInsideThis = creatingInFolderId === folder.id
        const isDragTarget = draggedDocId && dropTargetId === folder.id

        return (
          <div key={folder.id}>
            <div
              style={{ paddingLeft: 8 + indent }}
              className={`group flex items-center gap-1 py-[3px] pr-1 cursor-pointer select-none transition-colors ${
                isDragTarget
                  ? 'bg-[#6f8f88]/20 ring-1 ring-[#6f8f88]/40 ring-inset'
                  : 'hover:bg-white/5'
              }`}
              onClick={() => onToggle(folder.id)}
              onDragOver={e => { e.preventDefault(); e.stopPropagation(); if (draggedDocId) onFolderDrop(folder.id) }}
              onDrop={e => { e.preventDefault(); e.stopPropagation() }}
            >
              <span className="w-3 flex-shrink-0 text-[10px] text-white/30 text-center">
                {hasChildren || creatingInsideThis ? (isExpanded ? '▾' : '▸') : ''}
              </span>
              <svg className={`w-3.5 h-3.5 flex-shrink-0 ${isDragTarget ? 'text-[#6f8f88]' : 'text-[#6f8f88]'}`} viewBox="0 0 16 16" fill="currentColor">
                <path d={isDragTarget
                  ? "M.54 3.87.5 3a2 2 0 0 1 2-2h3.19a2 2 0 0 1 1.345.51l.33.33h5.99a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2.16a2 2 0 0 1-1.61-.82L.5 12.27A2 2 0 0 1 .16 11l.38-7.13z"
                  : ".54 3.87.5 3a2 2 0 0 1 2-2h3.19a2 2 0 0 1 1.345.51l.33.33h5.99a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2.16a2 2 0 0 1-1.61-.82L.5 12.27A2 2 0 0 1 .16 11l.38-7.13z"
                }/>
              </svg>
              <span className="text-[13px] truncate text-white/60 flex-1">{folder.name}</span>
              {isDragTarget && <span className="text-[10px] text-[#6f8f88] flex-shrink-0 pr-1">drop here</span>}
              <button
                onClick={e => { e.stopPropagation(); onStartCreating(folder.id) }}
                className="opacity-0 group-hover:opacity-100 transition-opacity text-white/30 hover:text-[#6f8f88] text-xs px-1 flex-shrink-0"
                title="New subfolder"
              >+</button>
            </div>

            {(isExpanded || creatingInsideThis) && (
              <FolderTree
                folders={folder.children}
                documents={folder.documents}
                parentFolderId={folder.id}
                selectedDocId={selectedDocId}
                expandedIds={expandedIds}
                onToggle={onToggle}
                onSelectDoc={onSelectDoc}
                onStartCreating={onStartCreating}
                creatingInFolderId={creatingInFolderId}
                creatingName={creatingName}
                creatingError={creatingError}
                onCreatingNameChange={onCreatingNameChange}
                onCreateConfirm={onCreateConfirm}
                onCreateCancel={onCreateCancel}
                inlineInputRef={inlineInputRef}
                draggedDocId={draggedDocId}
                dropTargetId={dropTargetId}
                onDocDragStart={onDocDragStart}
                onDocDragEnd={onDocDragEnd}
                onFolderDrop={onFolderDrop}
                depth={depth + 1}
              />
            )}
          </div>
        )
      })}

      {/* Inline folder create input */}
      {showInputHere && (
        <InlineCreateInput
          depth={depth + 1}
          value={creatingName}
          error={creatingError}
          onChange={onCreatingNameChange}
          onConfirm={onCreateConfirm}
          onCancel={onCreateCancel}
          inputRef={inlineInputRef}
        />
      )}

      {/* File rows at this level */}
      {documents.map(doc => {
        const ext = doc.original_filename.split('.').pop()?.toLowerCase() ?? ''
        const cfg = EXT_COLORS[ext] ?? { bg: '#607d8b', fg: '#fff', label: ext.toUpperCase().slice(0, 3) || 'F' }
        const label = (cfg.label ?? ext.toUpperCase()).slice(0, 3)
        const isActive = selectedDocId === doc.id
        const isDragging = draggedDocId === doc.id

        return (
          <div
            key={doc.id}
            draggable
            style={{ paddingLeft: 8 + indent + 12 }}
            onClick={() => onSelectDoc(doc)}
            onDragStart={e => { e.dataTransfer.effectAllowed = 'move'; onDocDragStart(doc.id) }}
            onDragEnd={onDocDragEnd}
            className={`flex items-center gap-1.5 py-[3px] pr-2 cursor-pointer select-none transition-all ${
              isDragging ? 'opacity-40' :
              isActive ? 'bg-[#6f8f88]/20' : 'hover:bg-white/5'
            }`}
          >
            <span
              style={{ background: cfg.bg, color: cfg.fg }}
              className="inline-flex items-center justify-center w-4 h-4 rounded-[3px] text-[7px] font-bold font-mono flex-shrink-0 cursor-grab"
            >
              {label}
            </span>
            <span className={`text-[13px] truncate ${isActive ? 'text-[#6f8f88]' : 'text-white/50'}`}>
              {doc.original_filename}
            </span>
          </div>
        )
      })}
    </div>
  )
}

// ─── DOCX Loading Skeleton ────────────────────────────────────────────────────

// ─── Toast ────────────────────────────────────────────────────────────────────
function Toast({ msg, type }: { msg: string; type: 'info' | 'warn' | 'error' }) {
  const colors = {
    info:  'bg-[#1e1e1e]/90 text-white border-[#6f8f88]/40',
    warn:  'bg-amber-900/90 text-amber-100 border-amber-600/40',
    error: 'bg-red-900/90 text-red-100 border-red-600/40',
  }
  const icons = { info: 'ℹ', warn: '⚠', error: '✕' }
  return (
    <div className={`fixed bottom-5 left-1/2 -translate-x-1/2 z-[100] flex items-center gap-2 px-4 py-2.5 rounded-xl border shadow-2xl text-sm backdrop-blur-sm ${colors[type]}`}>
      <span className="text-base leading-none">{icons[type]}</span>
      <span>{msg}</span>
    </div>
  )
}

// ─── Annotation Modal ─────────────────────────────────────────────────────────
function AnnotationModal({ title, defaultText, onConfirm, onCancel }: {
  title: string
  defaultText?: string
  onConfirm: (comment: string) => void
  onCancel: () => void
}) {
  const [text, setText] = useState(defaultText ?? '')
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" onClick={onCancel}>
      <div className="bg-white dark:bg-[#1e1e1e] rounded-2xl shadow-2xl p-5 w-80 flex flex-col gap-3" onClick={e => e.stopPropagation()}>
        <p className="text-sm font-semibold text-[#1A1A1A] dark:text-white">{title}</p>
        {defaultText && (
          <div className="px-2 py-1.5 bg-[#6f8f88]/10 rounded-lg border border-[#6f8f88]/20">
            <p className="text-[11px] font-mono text-[#6f8f88] line-clamp-3">"{defaultText}"</p>
          </div>
        )}
        <textarea
          autoFocus
          className="w-full text-sm border border-black/15 dark:border-white/15 rounded-xl px-3 py-2 resize-none bg-transparent text-[#1A1A1A] dark:text-white outline-none focus:border-[#6f8f88] transition-colors"
          rows={3}
          placeholder="Add forensic note…"
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && e.metaKey) onConfirm(text) }}
        />
        <div className="flex gap-2 justify-end">
          <button onClick={onCancel} className="px-3 py-1.5 text-xs rounded-lg bg-black/5 hover:bg-black/10 transition-colors text-[#2a2a2a]">Cancel</button>
          <button onClick={() => onConfirm(text)} className="px-3 py-1.5 text-xs rounded-lg bg-[#6f8f88] hover:bg-[#5a7a73] transition-colors text-white">
            Save Annotation
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── Inspection Toolbar ────────────────────────────────────────────────────────
function InspectionToolbar({ activeTool, onToolChange, zoom, onZoom, annotationCount, onJumpToFlag }: {
  activeTool: InspectTool
  onToolChange: (t: InspectTool) => void
  zoom: number
  onZoom: (delta: number) => void
  annotationCount: number
  onJumpToFlag?: () => void
}) {
  const btn = (tool: InspectTool, label: string, icon: React.ReactNode, title: string) => (
    <button
      title={title}
      onClick={() => onToolChange(activeTool === tool ? null : tool)}
      className={`flex items-center gap-1 px-2 py-1.5 rounded-lg text-[11px] font-medium transition-all ${
        activeTool === tool
          ? 'bg-[#6f8f88] text-white shadow-sm'
          : 'text-white/50 hover:bg-white/8'
      }`}
    >
      {icon}
      <span className="hidden sm:inline">{label}</span>
    </button>
  )

  return (
    <div className="flex items-center gap-1 px-2 py-1.5 bg-[#1a1a1a]/90 backdrop-blur-sm border border-white/10 rounded-xl shadow-lg">
      {/* Zoom */}
      <button onClick={() => onZoom(-0.25)} title="Zoom out" className="w-6 h-6 flex items-center justify-center rounded-md hover:bg-white/8 text-white/50 transition-colors">
        <svg viewBox="0 0 16 16" className="w-3.5 h-3.5" fill="currentColor"><path d="M6.5 1a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11zM0 6.5a6.5 6.5 0 1 1 11.74 3.832l3.223 3.223a.5.5 0 0 1-.707.707L11.032 11.04A6.5 6.5 0 0 1 0 6.5zm3.5 0a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1H4a.5.5 0 0 1-.5-.5z"/></svg>
      </button>
      <span className="text-[11px] font-mono text-white/40 w-9 text-center">{Math.round(zoom * 100)}%</span>
      <button onClick={() => onZoom(0.25)} title="Zoom in" className="w-6 h-6 flex items-center justify-center rounded-md hover:bg-white/8 text-white/50 transition-colors">
        <svg viewBox="0 0 16 16" className="w-3.5 h-3.5" fill="currentColor"><path d="M6.5 1a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11zM0 6.5a6.5 6.5 0 1 1 11.74 3.832l3.223 3.223a.5.5 0 0 1-.707.707L11.032 11.04A6.5 6.5 0 0 1 0 6.5zm3.5 0a.5.5 0 0 1 .5.5V8H5.5a.5.5 0 0 1 0 1H4v1.5a.5.5 0 0 1-1 0V9H1.5a.5.5 0 0 1 0-1H3V7a.5.5 0 0 1 .5-.5z"/></svg>
      </button>
      <button onClick={() => onZoom(0)} title="Reset zoom" className="w-6 h-6 flex items-center justify-center rounded-md hover:bg-white/8 text-white/30 transition-colors text-[10px] font-mono">1:1</button>

      <div className="w-px h-5 bg-white/10 mx-0.5" />

      {/* Highlight */}
      {btn('highlight',
        'Highlight',
        <svg viewBox="0 0 16 16" className="w-3.5 h-3.5" fill="currentColor"><path d="M8.464 1.464A1 1 0 0 0 7.05 1.05l-5.5 5.5a1 1 0 0 0 0 1.414l6.486 6.486a1 1 0 0 0 1.414 0l5.5-5.5a1 1 0 0 0 0-1.414l-6.486-6.486zM11.5 11.5l-1.5 1.5-6-6 1.5-1.5 6 6zm1.5-1.5L9.5 6.5l1.5-1.5 3.5 3.5-1.5 1.5z"/></svg>,
        'Text Highlighter — select text to annotate'
      )}

      {/* Region Selector */}
      {btn('region',
        'Region',
        <svg viewBox="0 0 16 16" className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="2" y="2" width="12" height="12" rx="1"/><path d="M5 2v12M11 2v12M2 5h12M2 11h12" strokeDasharray="2 2"/></svg>,
        'Region Selector — draw a bounding box to flag an area'
      )}

      <div className="w-px h-5 bg-white/10 mx-0.5" />

      {/* Annotate (manual note) */}
      {btn('annotate',
        'Note',
        <svg viewBox="0 0 16 16" className="w-3.5 h-3.5" fill="currentColor"><path d="M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v12.793a.5.5 0 0 1-.854.353l-3-3L8 15.146l-2.146-2-3 3A.5.5 0 0 1 2 15.793V2zm5 10a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm-2-4a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1H5zm0-2a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1H5z"/></svg>,
        'Add forensic note'
      )}

      {annotationCount > 0 && (
        <>
          <div className="w-px h-5 bg-white/10 mx-0.5" />
          <button
            onClick={onJumpToFlag}
            title="Jump to first flagged region"
            className="text-[10px] font-mono text-[#6f8f88] px-1.5 py-0.5 rounded-lg hover:bg-[#6f8f88]/15 transition-colors flex items-center gap-0.5"
          >
            {annotationCount} flag{annotationCount !== 1 ? 's' : ''}
            <svg viewBox="0 0 12 12" className="w-2.5 h-2.5" fill="currentColor"><path d="M2 1.5a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 .354.854L7.207 4.5l2.647 2.646a.5.5 0 0 1-.354.854H2.5a.5.5 0 0 1-.5-.5v-6z"/></svg>
          </button>
        </>
      )}
    </div>
  )
}

// ─── Time ago helper ──────────────────────────────────────────────────────────
function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

// ─── File Preview ─────────────────────────────────────────────────────────────
function FilePreview({ doc, contractId, token, onClose, sha256, virtualContent, annotations, onAddAnnotation }: {
  doc: DocumentSummary
  contractId: string
  token: string
  onClose: () => void
  sha256?: string
  virtualContent?: string
  annotations: ForensicAnnotation[]
  onAddAnnotation: (a: Omit<ForensicAnnotation, 'id' | 'timestamp'>) => void
}) {
  const [content, setContent] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTool, setActiveTool] = useState<InspectTool>(null)
  const [zoom, setZoom] = useState(1)
  const [region, setRegion] = useState<RegionDraft | null>(null)
  const [modalConfig, setModalConfig] = useState<{ title: string; defaultText?: string; onConfirm: (c: string) => void } | null>(null)

  // Code viewer: syntax-highlighted HTML from highlight.js
  const [highlightedHtml, setHighlightedHtml] = useState<string | null>(null)

  // Spatial annotation state
  const [hoveredAnnId, setHoveredAnnId] = useState<string | null>(null)
  const [imgBounds, setImgBounds] = useState<{ x: number; y: number; w: number; h: number } | null>(null)

  // Panel layout state
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [sidebarWidth, setSidebarWidth] = useState(280)
  const [toolbarCollapsed, setToolbarCollapsed] = useState(false)
  const sidebarDragRef = useRef<{ startX: number; startW: number } | null>(null)

  // Context analyzer state
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analyzerDone, setAnalyzerDone] = useState(false)

  const imgRef = useRef<HTMLImageElement>(null)
  const previewBodyRef = useRef<HTMLDivElement>(null)       // outer flex: content + sidebar
  const imageContainerRef = useRef<HTMLDivElement>(null)    // left scrollable pane
  const blobUrlRef = useRef<string | null>(null)
  const cardRefs = useRef<Record<string, HTMLDivElement | null>>({})

  const isVirtual = doc.id === CONTENT_MD_ID
  const rawUrl = `${API_BASE_URL}/contracts/${contractId}/documents/${doc.id}/raw`

  const runContextAnalyzer = useCallback(async () => {
    if (isVirtual || isAnalyzing) return
    setIsAnalyzing(true)
    setAnalyzerDone(false)
    try {
      const res = await fetch(`${API_BASE_URL}/documents/${doc.id}/analyze-context`, { method: 'POST' })
      if (!res.ok) throw new Error('Analysis failed')
      setAnalyzerDone(true)
      setTimeout(() => setAnalyzerDone(false), 3000)
    } catch {
      setAnalyzerDone(false)
    } finally {
      setIsAnalyzing(false)
    }
  }, [doc.id, isVirtual, isAnalyzing])
  const category = isVirtual ? 'text' : getFileCategory(doc.original_filename)
  // sorted by timestamp ascending
  const docAnnotations = annotations
    .filter(a => a.docId === doc.id)
    .sort((a, b) => a.timestamp.localeCompare(b.timestamp))
  const regionAnnotations = docAnnotations.filter(a => a.type === 'region' && a.region)

  // ── Load content ────────────────────────────────────────────────────────────
  useEffect(() => {
    setContent(null); setError(null); setZoom(1); setActiveTool(null); setImgBounds(null)
    if (isVirtual) { setContent(virtualContent ?? ''); return }

    // DOCX: convert to PDF on the backend, then display with the PDF viewer
    if (category === 'docx') {
      setLoading(true)
      fetch(`${API_BASE_URL}/docx-to-pdf/${doc.id}`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => { if (!r.ok) throw new Error('Conversion failed'); return r.blob() })
        .then(blob => {
          if (blobUrlRef.current) URL.revokeObjectURL(blobUrlRef.current)
          const url = URL.createObjectURL(blob)
          blobUrlRef.current = url
          setContent(url); setLoading(false)
        })
        .catch(() => { setError('Could not convert document to PDF'); setLoading(false) })
      return
    }

    const needsBlob = ['text','code','image','video','audio','pdf'].includes(category)
    if (!needsBlob) return
    setLoading(true)
    fetch(rawUrl, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.blob())
      .then(blob => {
        if (blobUrlRef.current) URL.revokeObjectURL(blobUrlRef.current)
        if (category === 'text' || category === 'code') {
          blob.text().then(t => { setContent(t); setLoading(false) })
        } else {
          const url = URL.createObjectURL(blob)
          blobUrlRef.current = url
          setContent(url); setLoading(false)
        }
      })
      .catch(() => { setError('Could not load file'); setLoading(false) })
    return () => { if (blobUrlRef.current) URL.revokeObjectURL(blobUrlRef.current) }
  }, [doc.id])

  // ── Code: syntax-highlight whenever raw content changes ─────────────────────
  useEffect(() => {
    if (category !== 'code' || !content) { setHighlightedHtml(null); return }
    const ext = doc.original_filename.split('.').pop()?.toLowerCase() ?? ''
    try {
      const lang = hljs.getLanguage(ext) ? ext : undefined
      const result = lang
        ? hljs.highlight(content, { language: lang })
        : hljs.highlightAuto(content)
      setHighlightedHtml(result.value)
    } catch {
      // fallback: escape HTML entities
      setHighlightedHtml(
        content.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      )
    }
  }, [content, category, doc.original_filename])

  // ── Image bounds tracking ────────────────────────────────────────────────────
  // imgBounds = position of rendered img relative to imageContainerRef
  const updateImgBounds = useCallback(() => {
    if (!imgRef.current || !imageContainerRef.current) return
    const containerRect = imageContainerRef.current.getBoundingClientRect()
    const imgRect = imgRef.current.getBoundingClientRect()
    setImgBounds({
      x: imgRect.left - containerRect.left,
      y: imgRect.top - containerRect.top,
      w: imgRect.width,
      h: imgRect.height,
    })
  }, [])

  useEffect(() => {
    window.addEventListener('resize', updateImgBounds)
    return () => window.removeEventListener('resize', updateImgBounds)
  }, [updateImgBounds])

  // After zoom transition (150ms) re-measure
  useEffect(() => {
    const t = setTimeout(updateImgBounds, 160)
    return () => clearTimeout(t)
  }, [zoom, content, updateImgBounds])

  // ── Focus mode spotlight ─────────────────────────────────────────────────────
  const focusSpot = (() => {
    if (!hoveredAnnId || !imgBounds) return null
    const ann = docAnnotations.find(a => a.id === hoveredAnnId)
    if (!ann?.region) return null
    const { x, y, w, h } = ann.region
    return {
      x: imgBounds.x + x / 100 * imgBounds.w,
      y: imgBounds.y + y / 100 * imgBounds.h,
      w: w / 100 * imgBounds.w,
      h: h / 100 * imgBounds.h,
    }
  })()

  // ── Compute leader line (in previewBodyRef space) ────────────────────────────
  const leaderLine = (() => {
    if (!hoveredAnnId || !previewBodyRef.current) return null
    const ann = docAnnotations.find(a => a.id === hoveredAnnId)
    if (!ann?.region) return null

    const bodyRect = previewBodyRef.current.getBoundingClientRect()
    const cardEl = cardRefs.current[hoveredAnnId]
    if (!cardEl) return null
    const cardRect = cardEl.getBoundingClientRect()
    const cx = cardRect.left - bodyRect.left
    const cy = cardRect.top - bodyRect.top + cardRect.height / 2

    let bx: number, by: number
    if ((category === 'text' || category === 'code') && imageContainerRef.current) {
      const ic = imageContainerRef.current
      const icRect = ic.getBoundingClientRect()
      const { x, y, w, h } = ann.region
      bx = (icRect.left - bodyRect.left) + (x + w / 2) / 100 * ic.scrollWidth
      by = (icRect.top  - bodyRect.top)  + (y + h / 2) / 100 * ic.scrollHeight - ic.scrollTop
    } else {
      if (!imgBounds || !imageContainerRef.current) return null
      const icRect = imageContainerRef.current.getBoundingClientRect()
      bx = (icRect.left - bodyRect.left) + imgBounds.x + (ann.region.x + ann.region.w / 2) / 100 * imgBounds.w
      by = (icRect.top  - bodyRect.top)  + imgBounds.y + (ann.region.y + ann.region.h / 2) / 100 * imgBounds.h
    }

    return { x1: bx, y1: by, x2: cx, y2: cy }
  })()

  // ── Jump to region ────────────────────────────────────────────────────────────
  const jumpToRegion = useCallback((annId: string) => {
    const ann = docAnnotations.find(a => a.id === annId)
    if (!ann?.region || !imgBounds || !imageContainerRef.current) return
    const { x, y, w, h } = ann.region
    const cx = imgBounds.x + (x + w / 2) / 100 * imgBounds.w
    const cy = imgBounds.y + (y + h / 2) / 100 * imgBounds.h
    imageContainerRef.current.scrollTo({
      left: cx - imageContainerRef.current.clientWidth / 2,
      top: cy - imageContainerRef.current.clientHeight / 2,
      behavior: 'smooth',
    })
    setHoveredAnnId(annId)
    setTimeout(() => setHoveredAnnId(null), 2000)
  }, [docAnnotations, imgBounds])

  const jumpToFirstFlag = useCallback(() => {
    if (regionAnnotations.length) jumpToRegion(regionAnnotations[0].id)
  }, [regionAnnotations, jumpToRegion])

  // ── Tool effects ─────────────────────────────────────────────────────────────
  useEffect(() => {
    if (activeTool === 'annotate') {
      setModalConfig({
        title: `Forensic note — ${doc.original_filename}`,
        onConfirm: (comment) => {
          if (comment.trim()) onAddAnnotation({ docId: doc.id, type: 'note', content: comment })
          setModalConfig(null); setActiveTool(null)
        }
      })
    }
  }, [activeTool])

  // ── Text highlighter ─────────────────────────────────────────────────────────
  const handleTextMouseUp = useCallback(() => {
    if (activeTool !== 'highlight') return
    const selection = window.getSelection()
    const sel = selection?.toString().trim()
    if (!sel || !selection?.rangeCount) return

    // Capture the selection's bounding rect as a % of the scrollable content area
    let region: { x: number; y: number; w: number; h: number } | undefined
    try {
      const range = selection.getRangeAt(0)
      const selRect = range.getBoundingClientRect()
      if (selRect.width > 0 || selRect.height > 0) {
        let containerEl: HTMLElement | null = null
        let totalW: number, totalH: number, scrollX: number, scrollY: number
        if (imageContainerRef.current) {
          containerEl = imageContainerRef.current
          totalW = containerEl.scrollWidth
          totalH = containerEl.scrollHeight
          scrollX = containerEl.scrollLeft
          scrollY = containerEl.scrollTop
        } else {
          containerEl = null; totalW = 1; totalH = 1; scrollX = 0; scrollY = 0
        }
        if (containerEl) {
          const cRect = containerEl.getBoundingClientRect()
          const rx = (selRect.left - cRect.left + scrollX) / totalW * 100
          const ry = (selRect.top  - cRect.top  + scrollY) / totalH * 100
          const rw = selRect.width  / totalW * 100
          const rh = selRect.height / totalH * 100
          region = {
            x: Math.max(0, Math.round(rx * 10) / 10),
            y: Math.max(0, Math.round(ry * 10) / 10),
            w: Math.max(0.5, Math.round(rw * 10) / 10),
            h: Math.max(0.2, Math.round(rh * 10) / 10),
          }
        }
      }
    } catch { /* ignore — region stays undefined */ }

    setModalConfig({
      title: 'Annotate selected text',
      defaultText: sel,
      onConfirm: (comment) => {
        onAddAnnotation({ docId: doc.id, type: 'text-selection', content: comment, excerpt: sel, region })
        setModalConfig(null)
        window.getSelection()?.removeAllRanges()
      }
    })
  }, [activeTool, doc.id, category])

  // ── Region selector ──────────────────────────────────────────────────────────
  const getRel = (e: React.MouseEvent<HTMLDivElement>) => {
    const r = e.currentTarget.getBoundingClientRect()
    return { x: e.clientX - r.left, y: e.clientY - r.top }
  }

  const onRgnDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (activeTool !== 'region') return
    e.preventDefault()
    const { x, y } = getRel(e)
    setRegion({ x, y, w: 0, h: 0, startX: x, startY: y, active: true })
  }
  const onRgnMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!region?.active) return
    const { x, y } = getRel(e)
    setRegion(r => r ? { ...r, x: Math.min(r.startX, x), y: Math.min(r.startY, y), w: Math.abs(x - r.startX), h: Math.abs(y - r.startY) } : null)
  }
  const onRgnUp = () => {
    if (!region?.active) { setRegion(null); return }
    const { x, y, w, h } = region
    setRegion(r => r ? { ...r, active: false } : null)
    if (w < 10 || h < 10) { setRegion(null); return }

    let nx: number, ny: number, nw: number, nh: number
    if (!imgBounds) { setRegion(null); return }
    nx = Math.max(0, Math.round((x - imgBounds.x) / imgBounds.w * 100))
    ny = Math.max(0, Math.round((y - imgBounds.y) / imgBounds.h * 100))
    nw = Math.min(100 - nx, Math.round(w / imgBounds.w * 100))
    nh = Math.min(100 - ny, Math.round(h / imgBounds.h * 100))

    const normalized = { x: nx, y: ny, w: nw, h: nh }
    setModalConfig({
      title: 'Flag region',
      onConfirm: (comment) => {
        onAddAnnotation({ docId: doc.id, type: 'region', content: comment, region: normalized })
        setModalConfig(null); setRegion(null)
      }
    })
  }

  const handleZoom = (delta: number) => {
    if (delta === 0) { setZoom(1); return }
    setZoom(z => Math.min(4, Math.max(0.25, z + delta)))
  }

  const isRegionTool = activeTool === 'region' && (category === 'image' || category === 'pdf')
  const isHighlightTool = activeTool === 'highlight' && (category === 'text' || category === 'code')


  return (
    <div className="flex flex-col h-full">
      {/* ── Header ── */}
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-white/8 flex-shrink-0 bg-[#151515]">
        <VsCodeIcon filename={doc.original_filename} size={22} />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-white/90 truncate">{doc.original_filename}</p>
          {sha256 && (
            <p className="text-[10px] font-mono text-white/25 truncate" title={`SHA-256: ${sha256}`}>
              sha256:{sha256.slice(0, 20)}…
            </p>
          )}
        </div>
        {!isVirtual && (
          <button
            onClick={runContextAnalyzer}
            disabled={isAnalyzing}
            title="Run through context analyzer"
            className="text-xs px-2.5 py-1 rounded-lg bg-[#6f8f88]/12 hover:bg-[#6f8f88]/22 transition-colors text-[#6f8f88] flex-shrink-0 flex items-center gap-1.5 disabled:opacity-50"
          >
            {isAnalyzing ? (
              <svg className="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
            ) : analyzerDone ? (
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
            ) : (
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
            )}
            {analyzerDone ? 'Done' : 'Context Analyzer'}
          </button>
        )}
        {!isVirtual && (
          <a href={content && category !== 'text' ? content : rawUrl} download={doc.original_filename}
            className="text-xs px-2 py-1 rounded-lg bg-white/8 hover:bg-white/15 transition-colors text-white/50 hover:text-white flex-shrink-0">↓</a>
        )}
        <button onClick={onClose}
          className="w-6 h-6 flex items-center justify-center rounded-lg hover:bg-white/10 transition-colors text-white/40 hover:text-white/70 flex-shrink-0 text-sm">✕</button>
      </div>

      {/* ── Inspection Toolbar ── */}
      {!isVirtual && (
        <div className="flex items-center justify-center px-4 py-2 border-b border-white/6 flex-shrink-0 bg-[#111111]">
          <InspectionToolbar
            activeTool={activeTool}
            onToolChange={t => setActiveTool(t)}
            zoom={zoom}
            onZoom={handleZoom}
            annotationCount={docAnnotations.length}
            onJumpToFlag={jumpToFirstFlag}
          />
        </div>
      )}

      {/* ── Body: document pane + annotation sidebar ── */}
      <div ref={previewBodyRef} className="flex-1 overflow-hidden flex relative">

        {/* Leader line SVG – covers entire body */}
        {leaderLine && (
          <svg className="absolute inset-0 pointer-events-none z-30"
            style={{ width: '100%', height: '100%', overflow: 'visible' }}>
            <defs>
              <style>{`@keyframes ll-dash{to{stroke-dashoffset:-16}}.ll-flow{animation:ll-dash 0.55s linear infinite}`}</style>
              <marker id="ll-dot" markerWidth="6" markerHeight="6" refX="3" refY="3">
                <circle cx="3" cy="3" r="2.5" fill="#6f8f88" opacity="0.9"/>
              </marker>
            </defs>
            <line
              className="ll-flow"
              x1={leaderLine.x1} y1={leaderLine.y1}
              x2={leaderLine.x2} y2={leaderLine.y2}
              stroke="#6f8f88" strokeWidth="1.5" strokeDasharray="5 3"
              opacity="0.75" markerStart="url(#ll-dot)"
            />
          </svg>
        )}

        {/* ── Left: document content ── */}
        <div ref={imageContainerRef}
          className={`flex-1 overflow-auto relative bg-[#0a0a0a] ${isRegionTool ? 'cursor-crosshair select-none' : ''}`}
          onMouseDown={onRgnDown}
          onMouseMove={onRgnMove}
          onMouseUp={onRgnUp}
        >
          {/* Focus mode spotlight — placed first so annotation boxes stack above it */}
          <svg
            className="absolute inset-0 pointer-events-none"
            style={{ width: '100%', height: '100%', zIndex: 10, opacity: focusSpot ? 1 : 0, transition: 'opacity 0.2s ease' }}
          >
            <defs>
              <mask id="focus-mask">
                <rect width="100%" height="100%" fill="white" />
                {focusSpot && (
                  <rect x={focusSpot.x} y={focusSpot.y} width={focusSpot.w} height={focusSpot.h} fill="black" rx="4" />
                )}
              </mask>
            </defs>
            <rect width="100%" height="100%" fill="rgba(0,0,0,0.4)" mask="url(#focus-mask)" />
          </svg>

          {loading && <div className="absolute inset-0 flex items-center justify-center text-white/30 text-sm">Loading…</div>}
          {error && <div className="absolute inset-0 flex items-center justify-center text-red-500 text-sm">{error}</div>}

          {/* Image */}
          {!loading && !error && content && category === 'image' && (
            <div className="w-full h-full flex items-center justify-center p-8">
              {/* Wrapper gives the image a positioned context so % coords are relative to the image itself */}
              <div
                className="relative"
                style={{ transform: `scale(${zoom})`, transformOrigin: 'center', transition: 'transform 0.15s ease', lineHeight: 0 }}
              >
                <img
                  ref={imgRef}
                  src={content}
                  alt={doc.original_filename}
                  draggable={false}
                  onLoad={updateImgBounds}
                  className="block max-w-full max-h-full object-contain rounded-lg shadow-lg"
                />
                {/* Annotation boxes — % coords are directly relative to the image, always exact */}
                {regionAnnotations.map(a => {
                  if (!a.region) return null
                  const { x, y, w, h } = a.region
                  const isHov = hoveredAnnId === a.id
                  return (
                    <div key={a.id}
                      style={{
                        position: 'absolute',
                        left: `${x}%`, top: `${y}%`,
                        width: `${w}%`, height: `${h}%`,
                        pointerEvents: 'none',
                        transition: 'box-shadow 0.2s, border-color 0.2s',
                      }}
                      className={`border-2 rounded ${isHov
                        ? 'border-[#e53935] shadow-[0_0_0_3px_rgba(229,57,53,0.25),0_0_18px_rgba(229,57,53,0.4)]'
                        : 'border-[#e53935]/70 bg-[#e53935]/5'}`}
                    >
                      {!isHov && (
                        <span className="absolute -top-5 left-0 text-[9px] text-[#e53935] bg-white/90 px-1 rounded whitespace-nowrap max-w-28 truncate leading-4">
                          {a.content}
                        </span>
                      )}
                    </div>
                  )
                })}
              </div>
              {/* Active rubber-band — in container space (raw mouse coords), fine for draw-time feedback */}
              {region && (
                <div style={{ position: 'absolute', left: region.x, top: region.y, width: region.w, height: region.h }}
                  className="border-2 border-dashed border-[#6f8f88] bg-[#6f8f88]/12 pointer-events-none rounded" />
              )}
            </div>
          )}

          {/* PDF / DOCX (converted to PDF) */}
          {!loading && !error && content && (category === 'pdf' || category === 'docx') && (
            <div className="relative w-full h-full">
              <iframe src={content} title={doc.original_filename} className="w-full h-full border-0" />
              {isRegionTool && (
                <div className="absolute inset-0" style={{ background: 'transparent' }}>
                  {region && (
                    <div style={{ position: 'absolute', left: region.x, top: region.y, width: region.w, height: region.h }}
                      className="border-2 border-dashed border-[#6f8f88] bg-[#6f8f88]/12 pointer-events-none rounded" />
                  )}
                </div>
              )}
            </div>
          )}

          {/* Video */}
          {!loading && !error && content && category === 'video' && (
            <div className="w-full h-full flex items-center justify-center p-6">
              <video src={content} controls className="max-w-full max-h-full rounded-lg shadow-lg" />
            </div>
          )}

          {/* Audio */}
          {!loading && !error && content && category === 'audio' && (
            <div className="w-full h-full flex items-center justify-center p-6">
              <audio src={content} controls className="w-full max-w-md" />
            </div>
          )}

          {/* Text / Markdown */}
          {!loading && !error && category === 'text' && content !== null && (
            <div className={`w-full h-full overflow-auto ${isHighlightTool ? 'cursor-text' : ''}`}
              onMouseUp={handleTextMouseUp}>
              <div className="relative">
                {/* Annotation highlight overlay — scrolls with content */}
                <svg className="absolute inset-0 pointer-events-none" style={{ zIndex: 5, width: '100%', height: '100%' }}>
                  {docAnnotations.filter(a => a.region).map(ann => {
                    const { x, y, w, h } = ann.region!
                    const isHov = hoveredAnnId === ann.id
                    return (
                      <rect key={ann.id}
                        x={`${x}%`} y={`${y}%`} width={`${w}%`} height={`${h}%`}
                        fill={isHov ? 'rgba(111,143,136,0.30)' : 'rgba(111,143,136,0.15)'}
                        stroke={isHov ? '#6f8f88' : 'rgba(111,143,136,0.4)'}
                        strokeWidth={isHov ? 2 : 1} rx="3"
                        style={{ transition: 'fill 0.15s, stroke 0.15s' }}
                      />
                    )
                  })}
                </svg>
                <pre className={`p-6 text-xs font-mono text-[#1A1A1A] dark:text-[#e5e5e5] leading-relaxed whitespace-pre-wrap break-words ${isHighlightTool ? 'select-text' : ''}`}>
                  {content}
                </pre>
              </div>
            </div>
          )}

          {/* Code — GitHub dark style with syntax highlighting */}
          {!loading && !error && category === 'code' && content !== null && (() => {
            const lines = content.split('\n')
            const ext = doc.original_filename.split('.').pop()?.toLowerCase() ?? ''
            const langLabel = hljs.getLanguage(ext)?.name ?? ext.toUpperCase()
            return (
              <div className={`w-full h-full overflow-auto ${isHighlightTool ? 'cursor-text' : ''}`}
                onMouseUp={handleTextMouseUp}>
                <div className="relative">
                  {/* Annotation highlight overlay — inside scroll so rects scroll with code */}
                  <svg className="absolute inset-0 pointer-events-none" style={{ zIndex: 5, width: '100%', height: '100%' }}>
                    {docAnnotations.filter(a => a.region).map(ann => {
                      const { x, y, w, h } = ann.region!
                      const isHov = hoveredAnnId === ann.id
                      return (
                        <rect key={ann.id}
                          x={`${x}%`} y={`${y}%`} width={`${w}%`} height={`${h}%`}
                          fill={isHov ? 'rgba(111,143,136,0.30)' : 'rgba(111,143,136,0.15)'}
                          stroke={isHov ? '#6f8f88' : 'rgba(111,143,136,0.4)'}
                          strokeWidth={isHov ? 2 : 1} rx="3"
                          style={{ transition: 'fill 0.15s, stroke 0.15s' }}
                        />
                      )
                    })}
                  </svg>

                  {/* GitHub-style file header */}
                  <div className="flex items-center justify-between px-4 py-2 bg-[#161b22] border-b border-[#30363d] sticky top-0 z-10">
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] font-mono text-[#e6edf3] opacity-70">{doc.original_filename}</span>
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-[#388bfd]/20 text-[#58a6ff] border border-[#388bfd]/30">{langLabel}</span>
                      <span className="text-[9px] text-[#6e7681]">{lines.length} lines</span>
                    </div>
                    <button
                      onClick={() => { navigator.clipboard.writeText(content) }}
                      className="text-[10px] text-[#6e7681] hover:text-[#e6edf3] transition-colors flex items-center gap-1 px-2 py-1 rounded hover:bg-[#30363d]"
                      title="Copy raw content"
                    >
                      <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor"><path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 010 1.5h-1.5a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-1.5a.75.75 0 011.5 0v1.5A1.75 1.75 0 019.25 16h-7.5A1.75 1.75 0 010 14.25z"/><path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0114.25 11h-7.5A1.75 1.75 0 015 9.25zm1.75-.25a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-7.5a.25.25 0 00-.25-.25z"/></svg>
                      Copy
                    </button>
                  </div>

                  {/* Code body: line numbers + highlighted code */}
                  <div className="flex bg-[#0d1117]">
                    {/* Line numbers gutter */}
                    <div className="select-none text-right px-4 pt-3 pb-3 text-[#6e7681] text-[11px] font-mono leading-[1.45rem] border-r border-[#30363d] flex-shrink-0 min-w-[3.5rem]">
                      {lines.map((_, i) => (
                        <div key={i}>{i + 1}</div>
                      ))}
                    </div>
                    {/* Syntax-highlighted code */}
                    <pre
                      className="flex-1 overflow-x-auto px-4 pt-3 pb-3 text-[11px] font-mono leading-[1.45rem] m-0 text-[#e6edf3] hljs"
                      dangerouslySetInnerHTML={{ __html: highlightedHtml ?? content.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') }}
                    />
                  </div>
                </div>
              </div>
            )
          })()}


          {/* Other */}
          {!loading && !error && category === 'other' && (
            <div className="w-full h-full flex flex-col items-center justify-center gap-4 p-6 text-center">
              <div className="text-6xl opacity-30">📎</div>
              <p className="text-sm text-white/40">No preview for this file type</p>
              <a href={rawUrl} download={doc.original_filename}
                className="px-4 py-2 bg-[#6f8f88] text-white rounded-xl text-sm hover:bg-[#5a7a73] transition-colors">
                Download file
              </a>
            </div>
          )}
        </div>

        {/* ── Right: Annotation Sidecar ── */}
        {docAnnotations.length > 0 && (
          <div className="w-[320px] flex-shrink-0 border-l border-white/8 bg-[#111111] flex flex-col overflow-hidden">
            {/* Sidecar header */}
            <div className="px-3 py-2.5 border-b border-white/6 flex items-center justify-between flex-shrink-0 bg-[#151515]">
              <span className="text-[10px] font-bold tracking-widest text-white/30 uppercase">Annotations</span>
              <span className="text-[10px] font-mono text-[#6f8f88]">{docAnnotations.length}</span>
            </div>

            {/* Timeline of annotation cards */}
            <div className="flex-1 overflow-y-auto p-2 flex flex-col gap-2">
              {docAnnotations.map((ann, i) => {
                const isHov = hoveredAnnId === ann.id
                const typeIcon = ann.type === 'text-selection' ? '✏️' : ann.type === 'region' ? '🖼️' : '💬'
                const typeLabel = ann.type === 'text-selection' ? 'Highlight' : ann.type === 'region' ? 'Region' : 'Note'
                return (
                  <div key={ann.id}
                    ref={el => { cardRefs.current[ann.id] = el }}
                    onMouseEnter={() => setHoveredAnnId(ann.id)}
                    onMouseLeave={() => setHoveredAnnId(null)}
                    onClick={() => ann.region && jumpToRegion(ann.id)}
                    className={`rounded-xl border p-2.5 transition-all flex flex-col gap-1 ${
                      ann.region ? 'cursor-pointer' : ''
                    } ${isHov
                      ? 'bg-[#6f8f88]/12 border-[#6f8f88]/35 shadow-sm'
                      : 'bg-white/4 border-white/6 hover:border-white/12'
                    }`}
                  >
                    {/* Card header row */}
                    <div className="flex items-center gap-1.5">
                      {/* Timeline dot */}
                      <div className="relative flex-shrink-0">
                        <div className={`w-1.5 h-1.5 rounded-full ${ann.type === 'region' ? 'bg-[#e53935]' : ann.type === 'text-selection' ? 'bg-[#6f8f88]' : 'bg-[#f59e0b]'}`} />
                        {i < docAnnotations.length - 1 && (
                          <div className="absolute top-2 left-1/2 -translate-x-1/2 w-px h-3 bg-white/10" />
                        )}
                      </div>
                      {/* Pill label */}
                      <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full flex items-center gap-0.5 ${
                        ann.type === 'region' ? 'bg-[#e53935]/10 text-[#e53935]' :
                        ann.type === 'text-selection' ? 'bg-[#6f8f88]/15 text-[#6f8f88]' :
                        'bg-amber-500/15 text-amber-400'
                      }`}>
                        {typeIcon} {typeLabel}
                      </span>
                      <span className="ml-auto text-[9px] text-white/25 flex-shrink-0">{timeAgo(ann.timestamp)}</span>
                    </div>

                    {/* Excerpt (for text selections) */}
                    {ann.excerpt && (
                      <p className="text-[10px] italic text-white/40 line-clamp-2 border-l-2 border-[#6f8f88]/30 pl-1.5">
                        "{ann.excerpt}"
                      </p>
                    )}

                    {/* Comment */}
                    {ann.content && (
                      <p className="text-[11px] text-white/80 font-medium line-clamp-3">
                        {ann.content}
                      </p>
                    )}

                    {/* Region coords chip */}
                    {ann.region && (
                      <div className="flex items-center gap-1 mt-0.5">
                        <span className="text-[8px] font-mono text-white/20 bg-white/5 px-1 rounded">
                          x{ann.region.x} y{ann.region.y} {ann.region.w}×{ann.region.h}
                        </span>
                        {ann.region && (
                          <span className="text-[8px] text-[#6f8f88]/60">↗ click to jump</span>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>

      {/* Annotation modal */}
      {modalConfig && (
        <AnnotationModal
          title={modalConfig.title}
          defaultText={modalConfig.defaultText}
          onConfirm={modalConfig.onConfirm}
          onCancel={() => { setModalConfig(null); setRegion(null); if (activeTool === 'annotate') setActiveTool(null) }}
        />
      )}
    </div>
  )
}

// ─── SHA-256 via Web Crypto ────────────────────────────────────────────────────
async function computeSHA256(file: File): Promise<string> {
  try {
    const buf = await file.arrayBuffer()
    const hash = await crypto.subtle.digest('SHA-256', buf)
    return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('')
  } catch {
    return 'hash-unavailable'
  }
}

interface ManifestEntry {
  filename: string
  hash: string
  uploaded: string
  folder: string
  size: number
}

// ─── Virtual content.md document ─────────────────────────────────────────────
const CONTENT_MD_ID = '__content_md__'
const CONTENT_MD_DOC: DocumentSummary = {
  id: CONTENT_MD_ID,
  original_filename: 'content.md',
  type: 'md',
  created_at: new Date().toISOString(),
  folder_id: null,
}

// ─── Main component ───────────────────────────────────────────────────────────
export function ContractWorkspace({ contractId, contractName, token, initialFiles, onClose }: Props) {
  const [contract, setContract] = useState<ContractDetail | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<string | null>(null)
  const [previewDoc, setPreviewDoc] = useState<DocumentSummary | null>(null)

  // Persisted expanded state
  const [expandedIds, setExpandedIds] = useState<Set<string>>(() => {
    try {
      const s = localStorage.getItem(`auth_expanded_${contractId}`)
      return s ? new Set(JSON.parse(s)) : new Set()
    } catch { return new Set() }
  })

  // Persisted file hashes: docId → sha256
  const [fileHashes, setFileHashes] = useState<Record<string, string>>(() => {
    try { return JSON.parse(localStorage.getItem(`auth_hashes_${contractId}`) ?? '{}') } catch { return {} }
  })

  // Persisted manifest (content.md data)
  const [manifest, setManifest] = useState<ManifestEntry[]>(() => {
    try { return JSON.parse(localStorage.getItem(`auth_manifest_${contractId}`) ?? '[]') } catch { return [] }
  })

  // Persisted forensic annotations
  const [annotations, setAnnotations] = useState<ForensicAnnotation[]>(() => {
    try { return JSON.parse(localStorage.getItem(`auth_annotations_${contractId}`) ?? '[]') } catch { return [] }
  })

  // Drag-and-drop between folders
  const [draggedDocId, setDraggedDocId] = useState<string | null>(null)
  const [dropTargetId, setDropTargetId] = useState<string | 'root' | null>(null)

  // Toast notifications
  const [toast, setToast] = useState<{ msg: string; type: 'info' | 'warn' | 'error' } | null>(null)
  const showToast = useCallback((msg: string, type: 'info' | 'warn' | 'error' = 'info') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3500)
  }, [])

  // VS Code-style inline create: undefined=off, null=at root, string=inside folder id
  const [creatingInFolderId, setCreatingInFolderId] = useState<string | null | undefined>(undefined)
  const [creatingName, setCreatingName] = useState('')
  const [creatingError, setCreatingError] = useState<string | null>(null)

  const fileInputRef = useRef<HTMLInputElement>(null)
  const inlineInputRef = useRef<HTMLInputElement>(null)

  // Persist expandedIds whenever they change
  useEffect(() => {
    localStorage.setItem(`auth_expanded_${contractId}`, JSON.stringify([...expandedIds]))
  }, [expandedIds, contractId])

  const toggleExpanded = useCallback((id: string) => {
    setExpandedIds(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }, [])

  // ── Annotations ─────────────────────────────────────────────────────────────
  const addAnnotation = useCallback((a: Omit<ForensicAnnotation, 'id' | 'timestamp'>) => {
    const full: ForensicAnnotation = { ...a, id: Math.random().toString(36).slice(2), timestamp: new Date().toISOString() }
    setAnnotations(prev => {
      const next = [...prev, full]
      localStorage.setItem(`auth_annotations_${contractId}`, JSON.stringify(next))
      return next
    })
  }, [contractId])

  // ── Drag-and-drop move ───────────────────────────────────────────────────────
  const moveDocument = useCallback(async (docId: string, targetFolderId: string | null) => {
    // Find the filename of the document being moved (from live contract tree)
    const flattenDocs = (folders: FolderNode[]): DocumentSummary[] =>
      folders.flatMap(f => [...f.documents, ...flattenDocs(f.children)])
    const allDocs = contract ? [...contract.root_documents, ...flattenDocs(contract.folders)] : []
    const movingDoc = allDocs.find(d => d.id === docId)

    try {
      await fetch(`${API_BASE_URL}/contracts/${contractId}/documents/${docId}/folder`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder_id: targetFolderId })
      })

      // Requirement 3: update manifest — remove old location entry, add new one (dedup ghost duplicates)
      if (movingDoc) {
        const fname = movingDoc.original_filename
        // Determine new folder label: we'll use targetFolderId or 'root'
        // (full folder name resolution happens on next loadContract; use id as placeholder)
        const newFolderLabel = targetFolderId ?? 'root'
        setManifest(prev => {
          // Remove ALL existing entries for this filename (prevents ghost duplicates)
          const without = prev.filter(e => e.filename !== fname)
          // Re-add with updated location
          const existing = prev.find(e => e.filename === fname)
          const updated = existing
            ? { ...existing, folder: newFolderLabel }
            : { filename: fname, hash: fileHashes[docId] ?? '', uploaded: new Date().toISOString(), folder: newFolderLabel, size: 0 }
          const next = [...without, updated]
          localStorage.setItem(`auth_manifest_${contractId}`, JSON.stringify(next))
          return next
        })
      }

      await loadContract()
    } catch { /* silent */ }
  }, [contractId, token, contract, fileHashes])

  const handleFolderDrop = useCallback(async (targetFolderId: string | null) => {
    if (!draggedDocId) return
    setDropTargetId(targetFolderId ?? 'root')
    await moveDocument(draggedDocId, targetFolderId)
    setDraggedDocId(null)
    setDropTargetId(null)
  }, [draggedDocId, moveDocument])

  // Generate GitHub-style audit manifest markdown
  const contentMdText = (() => {
    // Build docId → original_filename map from live contract tree
    const flattenDocs = (folders: FolderNode[]): DocumentSummary[] =>
      folders.flatMap(f => [...f.documents, ...flattenDocs(f.children)])
    const allDocs = contract ? [...contract.root_documents, ...flattenDocs(contract.folders)] : []
    const docIdToFilename: Record<string, string> = {}
    allDocs.forEach(d => { docIdToFilename[d.id] = d.original_filename })

    const now = new Date()
    const dateStr = now.toISOString().slice(0, 10)
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

    // ── File Inventory ──────────────────────────────────────────────────────
    const fileRows = manifest.length
      ? manifest.map(e => {
          const sizeStr = e.size >= 1024 * 1024
            ? `${(e.size / (1024 * 1024)).toFixed(1)} MB`
            : `${(e.size / 1024).toFixed(1)} KB`
          return `| \`${e.filename}\` | \`${e.hash.slice(0, 9)}…\` | \`/${e.folder}\` | ${sizeStr} |`
        }).join('\n')
      : '| — | — | — | — |'

    // ── Annotation blocks (GitHub callout style) ─────────────────────────────
    // Sorted chronologically; regions alternate IMPORTANT (first) → WARNING (subsequent)
    const sorted = [...annotations].sort((a, b) => a.timestamp.localeCompare(b.timestamp))
    let regionCount = 0

    const annBlocks = !sorted.length
      ? '_No forensic annotations yet. Use the Inspection Toolbar to flag regions or highlight text._'
      : sorted.map(a => {
          const filename = docIdToFilename[a.docId] ?? a.docId
          const shortId = a.id.slice(0, 8)
          const ts = new Date(a.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })

          let callout: string
          if (a.type === 'region') {
            callout = regionCount === 0 ? 'IMPORTANT' : 'WARNING'
            regionCount++
          } else if (a.type === 'text-selection') {
            callout = 'NOTE'
          } else {
            callout = 'IMPORTANT'
          }

          const lines: string[] = [
            `> [!${callout}]`,
            `> **Annotation ID:** \`${shortId}\`  `,
            `> **Target:** \`${filename}\`  `,
          ]

          if (a.region) {
            lines.push(`> **Region:** \`[x:${a.region.x}%, y:${a.region.y}%, w:${a.region.w}%, h:${a.region.h}%]\`  `)
          }
          if (a.excerpt) {
            lines.push(`> **Selection:** \`"${a.excerpt.slice(0, 120)}"\`  `)
          }
          if (a.content) {
            const fieldName = a.type === 'region' ? 'Label' : 'Comment'
            lines.push(`> **${fieldName}:** \`${a.content}\`  `)
          }
          lines.push(`> _Verified at ${ts}_`)

          return lines.join('\n')
        }).join('\n\n')

    return [
      `# 🛡️ Authentia Audit Manifest: ${contractName}`,
      `**Status:** \`IN_PROGRESS\` | **Last Updated:** ${dateStr} ${timeStr}`,
      ``,
      `---`,
      ``,
      `### 📂 File Inventory`,
      `| File Name | SHA-256 (Checksum) | Location | Size |`,
      `| :--- | :--- | :--- | :--- |`,
      fileRows,
      ``,
      `---`,
      ``,
      `### ✍️ Human Augmentation (Forensic Notes)`,
      ``,
      annBlocks,
      ``,
      `---`,
      `_Auto-generated by Authentia AI · Do not edit manually_`,
    ].join('\n')
  })()

  const loadContract = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/contracts/${contractId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) setContract(await res.json())
    } catch (e) {
      console.error('Failed to load contract', e)
    }
  }, [contractId, token])

  useEffect(() => { loadContract() }, [loadContract])

  // Auto-upload any files passed in on creation (from drag-drop or Upload card)
  useEffect(() => {
    if (initialFiles && initialFiles.length > 0) {
      handleFiles(initialFiles)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Focus inline input when it appears
  useEffect(() => {
    if (creatingInFolderId !== undefined) {
      setTimeout(() => inlineInputRef.current?.focus(), 50)
    }
  }, [creatingInFolderId])

  // ── Helpers ──────────────────────────────────────────────────────────────

  const getSiblingNames = (parentId: string | null): string[] => {
    if (!contract) return []
    if (parentId === null) {
      return contract.folders.map(f => f.name.toLowerCase())
    }
    const findFolder = (folders: FolderNode[]): FolderNode | null => {
      for (const f of folders) {
        if (f.id === parentId) return f
        const found = findFolder(f.children)
        if (found) return found
      }
      return null
    }
    const parent = findFolder(contract.folders)
    return parent?.children.map(f => f.name.toLowerCase()) ?? []
  }

  const startCreatingFolder = (parentId: string | null = null) => {
    setCreatingName('')
    setCreatingError(null)
    setCreatingInFolderId(parentId)
    if (parentId) setExpandedIds(prev => new Set([...prev, parentId]))
  }

  const cancelCreating = () => {
    setCreatingInFolderId(undefined)
    setCreatingName('')
    setCreatingError(null)
  }

  const handleCreateFolder = async () => {
    const name = creatingName.trim()
    if (!name) { cancelCreating(); return }

    // Client-side duplicate check
    const siblings = getSiblingNames(creatingInFolderId ?? null)
    if (siblings.includes(name.toLowerCase())) {
      setCreatingError(`"${name}" already exists here`)
      inlineInputRef.current?.select()
      return
    }

    try {
      const res = await fetch(`${API_BASE_URL}/contracts/${contractId}/folders`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, parent_id: creatingInFolderId ?? null })
      })
      if (res.ok) {
        cancelCreating()
        await loadContract()
        // Expand the parent so the new folder is visible
        if (creatingInFolderId) {
          setExpandedIds(prev => new Set([...prev, creatingInFolderId]))
        }
      } else {
        const err = await res.json().catch(() => ({}))
        setCreatingError((err as any).detail || 'Failed to create folder')
        inlineInputRef.current?.select()
      }
    } catch (e) {
      setCreatingError('Network error')
    }
  }

  const handleCreatingNameChange = (v: string) => {
    setCreatingName(v)
    if (creatingError) setCreatingError(null)
  }

  // ── Upload ────────────────────────────────────────────────────────────────

  const uploadFile = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${API_BASE_URL}/contracts/${contractId}/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    })
    return res.json()
  }

  const uploadZip = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${API_BASE_URL}/contracts/${contractId}/upload-zip`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    })
    return res.json()
  }

  const downloadZip = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/contracts/${contractId}/download-zip`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!res.ok) return
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = res.headers.get('Content-Disposition')?.match(/filename="(.+)"/)?.[1] ?? 'contract.zip'
      a.click()
      URL.revokeObjectURL(url)
    } catch { /* silent */ }
  }

  // Resolve a unique filename when a name conflict exists (same name, different hash)
  const resolveFilename = (name: string, existingNames: Set<string>): string => {
    if (!existingNames.has(name)) return name
    const dot = name.lastIndexOf('.')
    const base = dot >= 0 ? name.slice(0, dot) : name
    const ext  = dot >= 0 ? name.slice(dot) : ''
    let n = 1
    let candidate = `${base} (${n})${ext}`
    while (existingNames.has(candidate)) { n++; candidate = `${base} (${n})${ext}` }
    return candidate
  }

  const handleFiles = async (files: File[], folderLabel = 'root') => {
    if (!files.length) return
    setIsUploading(true)
    const newHashes: Record<string, string> = {}
    const newEntries: ManifestEntry[] = []

    // Snapshot of filenames already in manifest (for dedup)
    const existingByName: Record<string, string> = {}  // filename → hash
    manifest.forEach(e => { existingByName[e.filename] = e.hash })
    const existingNames = new Set(Object.keys(existingByName))

    const zips = files.filter(f => f.name.toLowerCase().endsWith('.zip'))
    const regular = files.filter(f => !f.name.toLowerCase().endsWith('.zip'))

    for (let i = 0; i < zips.length; i++) {
      setUploadProgress(`Hashing ${zips[i].name}…`)
      const hash = await computeSHA256(zips[i])
      setUploadProgress(`Extracting ZIP ${i + 1}/${zips.length}…`)
      try {
        const result = await uploadZip(zips[i])
        if (result?.documents) {
          for (const doc of result.documents) {
            newHashes[doc.id] = hash
            newEntries.push({ filename: doc.original_filename, hash, uploaded: new Date().toISOString(), folder: folderLabel, size: zips[i].size })
            existingNames.add(doc.original_filename)
          }
        }
      } catch { /* silent */ }
    }

    for (let i = 0; i < regular.length; i++) {
      const file = regular[i]
      setUploadProgress(`Hashing ${file.name}…`)
      const hash = await computeSHA256(file)

      // ── Duplicate detection ──────────────────────────────────────────────
      if (existingByName[file.name] !== undefined) {
        if (existingByName[file.name] === hash) {
          // Exact duplicate — skip
          showToast(`"${file.name}" already present — identical file skipped.`, 'warn')
          continue
        } else {
          // Same name, different content — rename
          const renamed = resolveFilename(file.name, existingNames)
          showToast(`"${file.name}" conflicts with existing file → saved as "${renamed}"`, 'info')
          // Re-create as renamed File object so the server gets the right filename
          const renamedFile = new File([file], renamed, { type: file.type })
          setUploadProgress(`Uploading ${renamed}…`)
          try {
            const formData = new FormData()
            formData.append('file', renamedFile)
            const res = await fetch(`${API_BASE_URL}/contracts/${contractId}/upload`, {
              method: 'POST',
              headers: { Authorization: `Bearer ${token}` },
              body: formData
            })
            const result = await res.json()
            if (result?.id) {
              newHashes[result.id] = hash
              newEntries.push({ filename: renamed, hash, uploaded: new Date().toISOString(), folder: folderLabel, size: file.size })
              existingNames.add(renamed)
              existingByName[renamed] = hash
            }
          } catch { /* silent */ }
          continue
        }
      }

      // ── Normal upload ────────────────────────────────────────────────────
      setUploadProgress(`Uploading ${file.name}…`)
      try {
        const result = await uploadFile(file)
        if (result?.id) {
          newHashes[result.id] = hash
          newEntries.push({ filename: file.name, hash, uploaded: new Date().toISOString(), folder: folderLabel, size: file.size })
          existingNames.add(file.name)
          existingByName[file.name] = hash
        }
      } catch { /* silent */ }
    }

    const mergedHashes = { ...fileHashes, ...newHashes }
    setFileHashes(mergedHashes)
    localStorage.setItem(`auth_hashes_${contractId}`, JSON.stringify(mergedHashes))

    // Dedup manifest: keep latest entry per (filename, folder) pair
    const seen = new Set<string>()
    const deduped = [...manifest, ...newEntries].filter(e => {
      const key = `${e.filename}::${e.folder}`
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
    setManifest(deduped)
    localStorage.setItem(`auth_manifest_${contractId}`, JSON.stringify(deduped))

    setIsUploading(false)
    setUploadProgress(null)
    await loadContract()
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    await handleFiles(Array.from(e.dataTransfer.files))
  }

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) { await handleFiles(Array.from(e.target.files)); e.target.value = '' }
  }

  return (
    <div
      className="flex-1 flex overflow-hidden relative bg-[#0a0a0a]"
      style={{ backgroundImage: 'radial-gradient(circle, #1d1d1d 1px, transparent 1px)', backgroundSize: '22px 22px' }}
      onDragEnter={e => { e.preventDefault(); e.stopPropagation(); setIsDragging(true) }}
      onDragOver={e => { e.preventDefault(); e.stopPropagation() }}
      onDragLeave={e => { e.preventDefault(); e.stopPropagation(); if (e.currentTarget === e.target) setIsDragging(false) }}
      onDrop={handleDrop}
    >
      {/* Drag overlay */}
      <AnimatePresence>
        {isDragging && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="absolute inset-0 z-50 backdrop-blur-sm bg-[#6f8f88]/20 border-2 border-dashed border-[#6f8f88] flex items-center justify-center pointer-events-none"
          >
            <p className="text-lg font-semibold text-[#6f8f88]">Drop to upload</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── VS Code sidebar: full file tree ── */}
      <div className="w-56 flex-shrink-0 border-r border-white/6 bg-[#111111] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-3 py-2.5 border-b border-white/6 flex-shrink-0">
          <button onClick={onClose} className="text-[11px] text-white/30 hover:text-white/70 transition-colors flex items-center gap-1">← back</button>
          <div className="flex items-center gap-2">
            {isUploading && <span className="text-[10px] text-[#6f8f88] animate-pulse">{uploadProgress ?? 'uploading…'}</span>}
            <button onClick={() => startCreatingFolder(null)} disabled={creatingInFolderId !== undefined} title="New Folder" className="text-white/25 hover:text-[#6f8f88] transition-colors disabled:opacity-20 text-sm leading-none">+</button>
          </div>
        </div>

        {/* Section label */}
        <div className="px-3 pt-2 pb-0.5 flex-shrink-0">
          <p className="text-[10px] font-semibold tracking-widest text-white/25 uppercase">{contractName}</p>
        </div>

        {/* Scrollable tree — also a root-level drop target */}
        <div
          className={`flex-1 overflow-y-auto py-1 ${draggedDocId && dropTargetId === 'root' ? 'bg-[#6f8f88]/8 ring-1 ring-inset ring-[#6f8f88]/30' : 'bg-transparent'}`}
          onDragOver={e => { if (draggedDocId) { e.preventDefault(); setDropTargetId('root') } }}
          onDrop={e => { e.preventDefault(); if (draggedDocId) handleFolderDrop(null) }}
        >
          {/* Inline input at root */}
          {creatingInFolderId === null && (
            <InlineCreateInput depth={0} value={creatingName} error={creatingError}
              onChange={handleCreatingNameChange} onConfirm={handleCreateFolder}
              onCancel={cancelCreating} inputRef={inlineInputRef} />
          )}

          {contract && (() => {
            const hasAnything = contract.folders.length > 0 || contract.root_documents.length > 0
            return (
              <>
                {!hasAnything && !isUploading && (
                  <div
                    className="mx-2 mt-4 mb-2 border border-dashed border-[#6f8f88]/40 rounded-lg p-4 text-center cursor-pointer hover:border-[#6f8f88]/70 hover:bg-[#6f8f88]/5 transition-colors"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <div className="text-2xl mb-1 opacity-30">📂</div>
                    <p className="text-[11px] text-white/30 leading-snug">Drop files here to<br/>begin analysis</p>
                  </div>
                )}
                <FolderTree
                  folders={contract.folders}
                  documents={contract.root_documents}
                  parentFolderId={null}
                  selectedDocId={previewDoc?.id ?? null}
                  expandedIds={expandedIds}
                  onToggle={toggleExpanded}
                  onSelectDoc={doc => setPreviewDoc(previewDoc?.id === doc.id ? null : doc)}
                  onStartCreating={startCreatingFolder}
                  creatingInFolderId={creatingInFolderId}
                  creatingName={creatingName}
                  creatingError={creatingError}
                  onCreatingNameChange={handleCreatingNameChange}
                  onCreateConfirm={handleCreateFolder}
                  onCreateCancel={cancelCreating}
                  inlineInputRef={inlineInputRef}
                  draggedDocId={draggedDocId}
                  dropTargetId={dropTargetId}
                  onDocDragStart={id => setDraggedDocId(id)}
                  onDocDragEnd={() => { setDraggedDocId(null); setDropTargetId(null) }}
                  onFolderDrop={handleFolderDrop}
                  depth={0}
                />
                {/* Virtual content.md entry — always shown at bottom of root */}
                {hasAnything && (() => {
                  const isActive = previewDoc?.id === CONTENT_MD_ID
                  return (
                    <div
                      onClick={() => setPreviewDoc(isActive ? null : CONTENT_MD_DOC)}
                      className={`flex items-center gap-1.5 py-[3px] px-3 cursor-pointer select-none transition-colors ${isActive ? 'bg-[#6f8f88]/20' : 'hover:bg-white/5'}`}
                    >
                      <span style={{ background: '#083fa1', color: '#fff' }}
                        className="inline-flex items-center justify-center w-4 h-4 rounded-[3px] text-[7px] font-bold font-mono flex-shrink-0">
                        MD
                      </span>
                      <span className={`text-[13px] truncate ${isActive ? 'text-[#6f8f88]' : 'text-white/40'}`}>
                        content.md
                      </span>
                    </div>
                  )
                })()}
              </>
            )
          })()}

          {!contract && (
            <p className="text-[12px] text-white/20 px-3 py-2">Loading…</p>
          )}
        </div>

        {/* Upload buttons */}
        <div className="border-t border-white/6 p-2 flex gap-1 flex-shrink-0">
          <input ref={fileInputRef} type="file" multiple className="hidden" onChange={handleFileInput} />
          <button onClick={() => fileInputRef.current?.click()} disabled={isUploading}
            className="flex-1 text-[11px] py-1 rounded bg-white/5 hover:bg-white/10 transition-colors text-white/40 disabled:opacity-30">
            Upload
          </button>
          <button onClick={downloadZip} disabled={isUploading}
            className="flex-1 text-[11px] py-1 rounded bg-[#6f8f88]/15 hover:bg-[#6f8f88]/25 transition-colors text-[#6f8f88] disabled:opacity-30">
            ↓ ZIP
          </button>
        </div>
      </div>

      {/* ── Preview panel (full right side) ── */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <AnimatePresence mode="wait">
          {previewDoc ? (
            <motion.div key={previewDoc.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex-1 flex flex-col overflow-hidden bg-transparent">
              <FilePreview
                doc={previewDoc}
                contractId={contractId}
                token={token}
                onClose={() => setPreviewDoc(null)}
                sha256={fileHashes[previewDoc.id]}
                virtualContent={previewDoc.id === CONTENT_MD_ID ? contentMdText : undefined}
                annotations={annotations}
                onAddAnnotation={addAnnotation}
              />
            </motion.div>
          ) : (
            <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-1 flex flex-col items-center justify-center gap-3 bg-transparent">
              {isUploading ? (
                <p className="text-sm text-[#6f8f88] animate-pulse">{uploadProgress ?? 'Uploading…'}</p>
              ) : (
                <>
                  <div
                    className="border border-dashed border-white/15 rounded-2xl p-14 flex flex-col items-center gap-3 cursor-pointer hover:border-[#6f8f88]/50 hover:bg-[#6f8f88]/5 transition-colors"
                    onClick={() => fileInputRef.current?.click()}
                    onDragOver={e => e.preventDefault()}
                    onDrop={async e => { e.preventDefault(); e.stopPropagation(); await handleFiles(Array.from(e.dataTransfer.files)) }}
                  >
                    <svg className="w-10 h-10 text-[#6f8f88]/30" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V7z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 11v6m-3-3l3-3 3 3" />
                    </svg>
                    <p className="text-sm text-white/30 select-none text-center leading-relaxed">
                      Drop files here to begin analysis<br/>
                      <span className="text-xs text-white/15">or click to browse</span>
                    </p>
                  </div>
                  <p className="text-[11px] text-white/20 select-none">
                    Select a file from the sidebar to preview
                  </p>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Toast notifications */}
      <AnimatePresence>
        {toast && <Toast msg={toast.msg} type={toast.type} />}
      </AnimatePresence>
    </div>
  )
}
