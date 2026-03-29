import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const API_BASE_URL = 'http://localhost:8002/api/v1'

interface Contract {
  id: string
  name: string
  status: string
  pinned: boolean
  shared: boolean
  created_at: string
  updated_at: string
  document_count: number
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function fmtDate(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

/** Deterministic pastel gradient from contract id */
function cardGradient(id: string) {
  const palettes = [
    ['#1a1a2e', '#16213e', '#0f3460'],
    ['#0d1b2a', '#1b263b', '#415a77'],
    ['#1a1a1a', '#2d2d2d', '#3a3a3a'],
    ['#0a2342', '#126872', '#26c6da'],
    ['#200122', '#6f0000', '#200122'],
    ['#0f0c29', '#302b63', '#24243e'],
    ['#141e30', '#243b55', '#2c3e50'],
    ['#1a1a2e', '#e94560', '#0f3460'],
  ]
  const idx = id.charCodeAt(0) % palettes.length
  const [a, b, c] = palettes[idx]
  return `linear-gradient(135deg, ${a} 0%, ${b} 50%, ${c} 100%)`
}

// ─── Contract Card ────────────────────────────────────────────────────────────

function ContractCard({
  contract,
  userInitial,
  userAvatar,
  onOpen,
  onPin,
  onShare,
  onDelete,
}: {
  contract: Contract
  userInitial: string
  userAvatar?: string
  onOpen: () => void
  onPin: (pinned: boolean) => void
  onShare: (shared: boolean) => void
  onDelete: () => void
}) {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.96 }}
      transition={{ duration: 0.2 }}
      className="flex flex-col rounded-2xl overflow-hidden cursor-pointer group"
      onClick={onOpen}
    >
      {/* Thumbnail */}
      <div
        className="relative aspect-video rounded-2xl overflow-hidden border border-white/8"
        style={{ background: cardGradient(contract.id) }}
      >
        {/* Document pattern overlay */}
        <div className="absolute inset-0 flex flex-col items-center justify-center p-6 gap-2 opacity-30">
          {[0.7, 0.5, 0.6, 0.4].map((w, i) => (
            <div key={i} className="h-1 rounded-full bg-white" style={{ width: `${w * 100}%` }} />
          ))}
        </div>
        {/* Contract name centred */}
        <div className="absolute inset-0 flex items-center justify-center p-4">
          <p className="text-white font-semibold text-lg text-center leading-snug drop-shadow-lg line-clamp-3">
            {contract.name}
          </p>
        </div>
        {/* Pin button top-right */}
        <button
          onClick={e => { e.stopPropagation(); onPin(!contract.pinned) }}
          className={`absolute top-3 right-3 w-9 h-9 rounded-xl flex items-center justify-center transition-all ${
            contract.pinned
              ? 'bg-white/20 text-white'
              : 'bg-black/40 text-white/50 opacity-0 group-hover:opacity-100'
          }`}
          title={contract.pinned ? 'Unpin' : 'Pin'}
        >
          {contract.pinned ? (
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M17 4a1 1 0 00-1-1H8a1 1 0 00-1 1v1h10V4zM5 7v2l2 2v4l-2 2v1h6v4h2v-4h6v-1l-2-2v-4l2-2V7H5z"/></svg>
          ) : (
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="17" x2="12" y2="22"/><path d="M5 7V5a2 2 0 012-2h10a2 2 0 012 2v2"/><path d="M5 7h14l-2 5v3H7v-3L5 7z"/></svg>
          )}
        </button>
        {/* Status badge */}
        <div className="absolute bottom-3 left-3">
          <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
            contract.status === 'complete'
              ? 'bg-green-500/20 border-green-500/40 text-green-300'
              : contract.status === 'in_progress'
              ? 'bg-blue-500/20 border-blue-500/40 text-blue-300'
              : 'bg-white/10 border-white/20 text-white/50'
          }`}>
            {contract.status}
          </span>
        </div>
      </div>

      {/* Card footer */}
      <div className="flex items-center gap-3 pt-3 px-1">
        {/* Avatar */}
        {userAvatar ? (
          <img src={userAvatar} className="w-7 h-7 rounded-full object-cover flex-shrink-0" referrerPolicy="no-referrer" />
        ) : (
          <div className="w-7 h-7 rounded-full bg-[#6f8f88] flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
            {userInitial}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-black dark:text-white truncate">{contract.name}</p>
          <p className="text-xs text-black/40 dark:text-white/40">
            Edited {fmtDate(contract.updated_at || contract.created_at)}
          </p>
        </div>
        {/* Actions */}
        <div className="flex items-center gap-1 flex-shrink-0">
          {/* Share / link icon */}
          <button
            onClick={e => { e.stopPropagation(); onShare(!contract.shared) }}
            className={`w-7 h-7 flex items-center justify-center rounded-lg transition-colors ${
              contract.shared ? 'text-[#6f8f88]' : 'text-black/30 dark:text-white/30 hover:text-black dark:hover:text-white'
            }`}
            title={contract.shared ? 'Unshare' : 'Share'}
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
              <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
              <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
            </svg>
          </button>
          {/* Three dots */}
          <div className="relative">
            <button
              onClick={e => { e.stopPropagation(); setMenuOpen(v => !v) }}
              className="w-7 h-7 flex items-center justify-center rounded-lg text-black/30 dark:text-white/30 hover:text-black dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/8 transition-colors text-sm"
            >
              •••
            </button>
            <AnimatePresence>
              {menuOpen && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: -4 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: -4 }}
                  transition={{ duration: 0.1 }}
                  className="absolute right-0 bottom-full mb-1 z-50 w-36 rounded-xl bg-white dark:bg-[#1e1e1e] border border-black/8 dark:border-white/10 shadow-xl overflow-hidden"
                  onClick={e => e.stopPropagation()}
                >
                  <button
                    onClick={() => { onPin(!contract.pinned); setMenuOpen(false) }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-black dark:text-white hover:bg-black/4 dark:hover:bg-white/8 transition-colors text-left"
                  >
                    {contract.pinned ? 'Unpin' : 'Pin'}
                  </button>
                  <button
                    onClick={() => { onShare(!contract.shared); setMenuOpen(false) }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-black dark:text-white hover:bg-black/4 dark:hover:bg-white/8 transition-colors text-left"
                  >
                    {contract.shared ? 'Unshare' : 'Share'}
                  </button>
                  <div className="h-px bg-black/6 dark:bg-white/8" />
                  <button
                    onClick={() => { onDelete(); setMenuOpen(false) }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors text-left"
                  >
                    Delete
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// ─── Main component ───────────────────────────────────────────────────────────

export function ContractsGrid({
  title,
  contracts,
  user,
  token,
  filter,
  hideNew = false,
  onOpenContract,
  onNewContract,
  onContractsChange,
}: {
  title: string
  contracts: Contract[]
  user: { username: string; email: string; profile_picture?: string } | null
  token: string | null
  filter?: 'all' | 'pinned' | 'me' | 'shared'
  hideNew?: boolean
  onOpenContract: (id: string, name: string) => void
  onNewContract: () => void
  onContractsChange: (updated: Contract[]) => void
}) {
  const [search, setSearch] = useState('')

  const displayed = useMemo(() => {
    let list = contracts
    if (filter === 'pinned') list = list.filter(c => c.pinned)
    if (filter === 'shared') list = list.filter(c => c.shared)
    if (search.trim()) {
      const q = search.toLowerCase()
      list = list.filter(c => c.name.toLowerCase().includes(q))
    }
    return list
  }, [contracts, filter, search])

  const userInitial = user?.username?.charAt(0).toUpperCase() ?? '?'

  const callApi = async (contractId: string, path: string, body: object) => {
    const tok = token || localStorage.getItem('token') || ''
    const res = await fetch(`${API_BASE_URL}/contracts/${contractId}/${path}`, {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${tok}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    if (res.ok) {
      const updated: Contract = await res.json()
      onContractsChange(contracts.map(c => c.id === contractId ? { ...c, ...updated } : c))
    }
  }

  const deleteContract = async (contractId: string) => {
    const tok = token || localStorage.getItem('token') || ''
    await fetch(`${API_BASE_URL}/contracts/${contractId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${tok}` },
    })
    onContractsChange(contracts.filter(c => c.id !== contractId))
  }

  return (
    <div className="flex-1 flex flex-col min-h-0 bg-white dark:bg-black overflow-hidden">
      {/* ── Top bar ── */}
      <div className="flex items-center gap-3 px-8 pt-8 pb-5 flex-shrink-0">
        <h1 className="text-2xl font-bold text-black dark:text-white">{title}</h1>
        <button className="text-black/30 dark:text-white/30 hover:text-black dark:hover:text-white transition-colors">
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/>
          </svg>
        </button>
      </div>

      {/* ── Search + filters ── */}
      <div className="flex items-center gap-3 px-8 pb-6 flex-shrink-0">
        <div className="relative flex-1 max-w-md">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-black/30 dark:text-white/30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
          </svg>
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search contracts..."
            className="w-full pl-9 pr-4 py-2 text-sm rounded-xl border border-black/10 dark:border-white/10 bg-black/3 dark:bg-white/5 text-black dark:text-white placeholder:text-black/30 dark:placeholder:text-white/25 outline-none focus:border-black/25 dark:focus:border-white/25 transition-colors"
          />
        </div>
        <div className="flex items-center gap-2 text-sm text-black/40 dark:text-white/35">
          <span>Last edited ↓</span>
        </div>
      </div>

      {/* ── Grid ── */}
      <div className="flex-1 overflow-y-auto px-8 pb-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {/* Create new */}
          {!hideNew && (
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onNewContract}
            className="flex flex-col cursor-pointer group"
          >
            <div className="aspect-video rounded-2xl border-2 border-dashed border-black/15 dark:border-white/15 flex items-center justify-center hover:border-black/30 dark:hover:border-white/25 hover:bg-black/2 dark:hover:bg-white/3 transition-all">
              <svg className="w-8 h-8 text-black/25 dark:text-white/25 group-hover:text-black/40 dark:group-hover:text-white/40 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4"/>
              </svg>
            </div>
            <div className="pt-3 px-1">
              <p className="text-sm font-medium text-black/60 dark:text-white/50 group-hover:text-black dark:group-hover:text-white transition-colors">Create new contract</p>
            </div>
          </motion.div>
          )}

          {/* Contract cards */}
          <AnimatePresence>
            {displayed.map(contract => (
              <ContractCard
                key={contract.id}
                contract={contract}
                userInitial={userInitial}
                userAvatar={user?.profile_picture}
                onOpen={() => onOpenContract(contract.id, contract.name)}
                onPin={pinned => callApi(contract.id, 'pin', { pinned })}
                onShare={shared => callApi(contract.id, 'share', { shared })}
                onDelete={() => deleteContract(contract.id)}
              />
            ))}
          </AnimatePresence>

          {displayed.length === 0 && search && (
            <div className="col-span-full flex flex-col items-center justify-center py-20 text-center">
              <p className="text-black/30 dark:text-white/25 text-sm">No contracts match "{search}"</p>
            </div>
          )}
          {displayed.length === 0 && !search && filter && filter !== 'all' && (
            <div className="col-span-full flex flex-col items-center justify-center py-20 text-center">
              <p className="text-black/30 dark:text-white/25 text-sm">
                {filter === 'shared' ? 'No one has shared a contract with you yet' : 'No contracts here yet'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
