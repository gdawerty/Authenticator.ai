import { useState, useEffect, useCallback, useRef } from 'react'
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { DocumentViewer } from './components/DocumentViewer'
import { ContentUnderstander } from './components/ContentUnderstander'
import { Login } from './components/Login'
import { Register } from './components/Register'
import { OAuthCallback } from './components/OAuthCallback'
import { LandingPage } from './components/landing'
import { LandingPage as NewLandingPage } from './frontpage'
import { ThemeToggle } from './components/ThemeToggle'
import { ContractWorkspace } from './components/ContractWorkspace'

const API_BASE_URL_CONST = 'http://localhost:8002/api/v1'

interface ContractCreated {
  id: string
  name: string
  status: string
  pinned: boolean
  created_at: string
  document_count: number
}

// Isolated component — owns its own state so typing never triggers App re-renders
function ContractPortal({ token, onCreated }: {
  token: string | null
  onCreated: (contract: ContractCreated, files?: File[]) => void
}) {
  const [mode, setMode] = useState<'default' | 'new-form'>('default')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploadDragging, setUploadDragging] = useState(false)
  const [uploadLoading, setUploadLoading] = useState(false)
  const uploadDragCounter = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const createEmpty = async () => {
    if (!name.trim() || !token) return
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE_URL_CONST}/contracts`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim() })
      })
      if (res.ok) {
        const contract = await res.json()
        setName('')
        setMode('default')
        onCreated(contract)
      }
    } catch (e) {
      console.error('Failed to create contract', e)
    } finally {
      setLoading(false)
    }
  }

  const createFromFiles = async (files: File[]) => {
    if (!files.length || !token) return
    setUploadLoading(true)
    try {
      // Name contract after the first file, stripping extension
      const rawName = files[0].name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ')
      const contractName = rawName.charAt(0).toUpperCase() + rawName.slice(1)
      const res = await fetch(`${API_BASE_URL_CONST}/contracts`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: contractName })
      })
      if (res.ok) {
        const contract = await res.json()
        onCreated(contract, files)
      }
    } catch (e) {
      console.error('Failed to create contract from files', e)
    } finally {
      setUploadLoading(false)
    }
  }

  const handleUploadDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    uploadDragCounter[1](0)
    setUploadDragging(false)
    const files = Array.from(e.dataTransfer.files)
    if (files.length) await createFromFiles(files)
  }

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      await createFromFiles(Array.from(e.target.files))
      e.target.value = ''
    }
  }

  const cardBase = "relative flex flex-col items-center justify-center gap-3 w-44 h-44 rounded-3xl backdrop-blur-md border cursor-pointer transition-all select-none"
  const cardStyle = { boxShadow: '0 25px 50px -12px rgba(0,0,0,0.15)' }

  return (
    <div className="flex items-start gap-5">
      {/* ── New Contract card ── */}
      <AnimatePresence mode="wait">
        {mode === 'new-form' ? (
          <motion.div
            key="new-form"
            initial={{ opacity: 0, scale: 0.95, width: 176 }}
            animate={{ opacity: 1, scale: 1, width: 288 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="p-5 rounded-3xl backdrop-blur-md bg-white/30 dark:bg-white/5 border border-black/10 dark:border-white/10 overflow-hidden"
            style={cardStyle}
          >
            <p className="text-xs font-semibold text-[#2a2a2a]/60 dark:text-white/50 mb-3 uppercase tracking-wide">New Contract</p>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter') createEmpty()
                if (e.key === 'Escape') { setMode('default'); setName('') }
              }}
              placeholder="Contract name..."
              autoFocus
              className="w-full px-3 py-2 text-sm bg-white/50 dark:bg-white/10 border border-black/10 dark:border-white/10 rounded-xl outline-none focus:border-[#6f8f88]/50 text-[#1A1A1A] dark:text-white placeholder-[#2a2a2a]/40 dark:placeholder-white/40 mb-3"
            />
            <div className="flex gap-2 w-full">
              <motion.button
                onClick={createEmpty}
                disabled={loading || !name.trim()}
                whileHover={{ scale: 1.02, boxShadow: '0 0 20px rgba(111,143,136,0.5)' }}
                whileTap={{ scale: 0.97 }}
                className="flex-1 py-2 text-sm bg-[#6f8f88] text-white rounded-xl disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create'}
              </motion.button>
              <button
                onClick={() => { setMode('default'); setName('') }}
                className="flex-1 py-2 text-sm bg-black/10 dark:bg-white/10 rounded-xl hover:bg-black/20 dark:hover:bg-white/20 transition-colors text-[#1A1A1A] dark:text-white"
              >
                Cancel
              </button>
            </div>
          </motion.div>
        ) : (
          <motion.button
            key="new-btn"
            onClick={() => setMode('new-form')}
            whileHover={{ scale: 1.05, y: -6, boxShadow: '0 30px 60px -12px rgba(0,0,0,0.2), 0 0 30px rgba(111,143,136,0.15)' }}
            whileTap={{ scale: 0.95 }}
            className={`${cardBase} bg-white/30 dark:bg-white/5 border-black/10 dark:border-white/10 hover:bg-white/40 dark:hover:bg-white/10 hover:border-[#6f8f88]/40`}
            style={cardStyle}
          >
            <div className="text-5xl">📁</div>
            <p className="text-[#2a2a2a] dark:text-white/80 text-sm font-medium text-center">New Contract</p>
          </motion.button>
        )}
      </AnimatePresence>

      {/* ── Upload card ── */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        className="hidden"
        onChange={handleFileInput}
        accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.zip"
      />
      <motion.div
        onClick={() => !uploadLoading && fileInputRef.current?.click()}
        onDragEnter={e => {
          e.preventDefault(); e.stopPropagation()
          uploadDragCounter[1](c => c + 1)
          setUploadDragging(true)
        }}
        onDragLeave={e => {
          e.preventDefault(); e.stopPropagation()
          uploadDragCounter[1](c => {
            const next = c - 1
            if (next <= 0) setUploadDragging(false)
            return next
          })
        }}
        onDragOver={e => { e.preventDefault(); e.stopPropagation() }}
        onDrop={handleUploadDrop}
        whileHover={!uploadLoading ? { scale: 1.05, y: -6, boxShadow: '0 30px 60px -12px rgba(0,0,0,0.2), 0 0 30px rgba(111,143,136,0.15)' } : {}}
        whileTap={!uploadLoading ? { scale: 0.95 } : {}}
        animate={uploadDragging ? { scale: 1.08, borderColor: '#6f8f88' } : {}}
        className={`${cardBase} ${
          uploadDragging
            ? 'border-dashed border-[#6f8f88] bg-[#6f8f88]/10'
            : 'border-black/10 dark:border-white/10 bg-white/30 dark:bg-white/5 hover:bg-white/40 dark:hover:bg-white/10 hover:border-[#6f8f88]/40'
        } ${uploadLoading ? 'cursor-wait' : ''}`}
        style={cardStyle}
      >
        {uploadLoading ? (
          <>
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }} className="text-5xl">⏳</motion.div>
            <p className="text-[#2a2a2a] dark:text-white/80 text-sm font-medium text-center">Creating...</p>
          </>
        ) : (
          <>
            <div className="text-5xl">{uploadDragging ? '📂' : '⬆️'}</div>
            <p className="text-[#2a2a2a] dark:text-white/80 text-sm font-medium text-center">
              {uploadDragging ? 'Drop it!' : 'Upload'}
            </p>
            <p className="text-xs text-[#2a2a2a]/40 dark:text-white/40 text-center px-2">
              Files, folders, ZIP
            </p>
          </>
        )}
      </motion.div>
    </div>
  )
}

const API_BASE_URL = API_BASE_URL_CONST

interface User {
  id: string
  email: string
  username: string
  profile_picture?: string
  oauth_provider?: string
}

interface Audit {
  id: string
  name: string
  timestamp: Date
  status: 'clean' | 'warning' | 'flagged'
  documentId: string
}

interface Contract {
  id: string
  name: string
  status: string
  pinned: boolean
  created_at: string
  document_count: number
}

// Defined OUTSIDE App so its type identity is stable — no remount on App re-renders
function ContractItem({ contract, isActive, onOpen, onPin, onDelete }: {
  contract: Contract
  isActive: boolean
  onOpen: () => void
  onPin: (pinned: boolean) => void
  onDelete: () => void
}) {
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!menuOpen) return
    const handler = (e: MouseEvent) => {
      if (!menuRef.current?.contains(e.target as Node)) setMenuOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [menuOpen])

  return (
    <div className="relative group">
      <motion.div
        variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}
        whileHover={{ scale: 1.02, x: 4 }}
        onClick={onOpen}
        className={`p-3 rounded-xl backdrop-blur-sm border cursor-pointer transition-all ${
          isActive
            ? 'bg-[#6f8f88]/20 border-[#6f8f88]/30'
            : 'bg-white/30 dark:bg-white/5 border-black/10 dark:border-white/10 hover:bg-white/40 dark:hover:bg-white/10'
        }`}
      >
        <div className="flex items-start gap-2">
          <div className="flex-1 min-w-0 pr-5">
            <p className="font-medium text-sm truncate text-[#1A1A1A] dark:text-white">{contract.name}</p>
            <p className="text-xs text-[#2a2a2a]/60 dark:text-white/60 mt-0.5">
              {contract.document_count} file{contract.document_count !== 1 ? 's' : ''}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Three-dot button */}
      <button
        onClick={e => { e.stopPropagation(); setMenuOpen(v => !v) }}
        className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 p-1 rounded-md hover:bg-black/10 dark:hover:bg-white/10 transition-all text-[#2a2a2a]/60 dark:text-white/60 text-xs leading-none"
      >
        •••
      </button>

      {/* Dropdown menu */}
      {menuOpen && (
        <div
          ref={menuRef}
          className="absolute right-0 top-full mt-1 z-50 w-36 rounded-xl overflow-hidden backdrop-blur-xl bg-white/80 dark:bg-[#2a2a2a]/90 border border-black/10 dark:border-white/10 shadow-xl"
        >
          <button
            onClick={e => { e.stopPropagation(); onPin(!contract.pinned); setMenuOpen(false) }}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-[#1A1A1A] dark:text-white hover:bg-black/5 dark:hover:bg-white/10 transition-colors text-left"
          >
            <span>📌</span>
            {contract.pinned ? 'Unpin' : 'Pin'}
          </button>
          <div className="h-px bg-black/10 dark:bg-white/10" />
          <button
            onClick={e => { e.stopPropagation(); onDelete(); setMenuOpen(false) }}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors text-left"
          >
            <span>🗑️</span>
            Delete
          </button>
        </div>
      )}
    </div>
  )
}

function App() {
  const navigate = useNavigate()
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isAuthLoading, setIsAuthLoading] = useState(true)
  const [_audits, setAudits] = useState<Audit[]>([])
  const [contracts, setContracts] = useState<Contract[]>([])
  const [activeContractId, setActiveContractId] = useState<string | null>(null)
  const [activeContractName, setActiveContractName] = useState<string>('')
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [activeDocumentId, setActiveDocumentId] = useState<string | null>(null)
  const [activeSpanId, setActiveSpanId] = useState<string | null>(null)
  const [activeSpan, setActiveSpan] = useState<any>(null)
  const [hasAnimatedGreeting, setHasAnimatedGreeting] = useState(false)
  const [greetingIndex] = useState(() => Math.floor(Math.random() * 55)) // Random on initial load, stable during session

  // Handle greeting animation - moved to top level to avoid hooks inside nested component
  useEffect(() => {
    const shouldAnimateGreeting = !hasAnimatedGreeting && !activeDocumentId && !activeContractId && isAuthenticated && !isAuthLoading
    if (shouldAnimateGreeting) {
      const timer = setTimeout(() => {
        setHasAnimatedGreeting(true)
      }, 1500) // After all animations complete
      return () => clearTimeout(timer)
    }
  }, [hasAnimatedGreeting, activeDocumentId, activeContractId, isAuthenticated, isAuthLoading])

  // Load audits from API
  const loadAudits = async (authToken: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/audits`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      if (response.ok) {
        const auditsData = await response.json()
        const formattedAudits: Audit[] = auditsData.map((audit: any) => ({
          id: audit.id,
          name: audit.name,
          timestamp: new Date(audit.created_at),
          status: audit.status as 'clean' | 'warning' | 'flagged',
          documentId: audit.document_id || ''
        }))
        setAudits(formattedAudits)
      } else if (response.status === 401) {
        // Token is invalid or expired — clear session and redirect to login
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        setToken(null)
        setUser(null)
        setIsAuthenticated(false)
        navigate('/login')
      }
    } catch (error) {
      console.error('Failed to load audits:', error)
    }
  }

  const loadContracts = async (authToken: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/contracts`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      })
      if (response.ok) {
        const data = await response.json()
        setContracts(data)
      }
    } catch (error) {
      console.error('Failed to load contracts:', error)
    }
  }

  // Check if user is already logged in on mount only
  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    if (storedToken && storedUser) {
      setToken(storedToken)
      const userData = JSON.parse(storedUser)
      setUser(userData)
      setIsAuthenticated(true)
      // Load audits and contracts when user is logged in
      loadAudits(storedToken)
      loadContracts(storedToken)
    }
    setIsAuthLoading(false)
  }, [])

  const handleLogin = async (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    const data = await response.json()
    setToken(data.access_token)
    setUser(data.user)
    setIsAuthenticated(true)
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    // Load audits and contracts after login
    loadAudits(data.access_token)
    loadContracts(data.access_token)
    // Navigate to app
    navigate('/app')
  }

  const handleRegister = async (email: string, username: string, password: string) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, username, password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Registration failed')
    }

    // After successful registration, automatically log in
    await handleLogin(username, password)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    // Force a full page reload to ensure clean state
    window.location.href = '/login'
  }

  const pendingFilesRef = useRef<File[]>([])

  const pinContract = async (contractId: string, pinned: boolean) => {
    const tok = token || localStorage.getItem('token')
    if (!tok) return
    try {
      const res = await fetch(`${API_BASE_URL}/contracts/${contractId}/pin`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${tok}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ pinned })
      })
      if (res.ok) {
        setContracts(prev => prev.map(c => c.id === contractId ? { ...c, pinned } : c))
      }
    } catch (e) {
      console.error('Failed to pin contract', e)
    }
  }

  const deleteContractItem = async (contractId: string) => {
    const tok = token || localStorage.getItem('token')
    if (!tok) return
    try {
      const res = await fetch(`${API_BASE_URL}/contracts/${contractId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${tok}` }
      })
      if (res.ok) {
        setContracts(prev => prev.filter(c => c.id !== contractId))
        if (activeContractId === contractId) {
          setActiveContractId(null)
          setActiveContractName('')
        }
      }
    } catch (e) {
      console.error('Failed to delete contract', e)
    }
  }

  const handleContractCreated = (contract: ContractCreated, files?: File[]) => {
    pendingFilesRef.current = files ?? []
    setContracts(prev => [contract, ...prev])
    setActiveContractId(contract.id)
    setActiveContractName(contract.name)
    setActiveDocumentId(null)
    navigate('/app')
  }

  // Component wrappers for routing
  const LoginPage = () => (
    <Login
      onLogin={handleLogin}
      onSwitchToRegister={() => navigate('/register')}
    />
  )

  const RegisterPage = () => (
    <Register
      onRegister={handleRegister}
      onSwitchToLogin={() => navigate('/login')}
    />
  )

  const MainApp = () => {
    // Show nothing while checking auth status
    if (isAuthLoading) {
      return null
    }

    if (!isAuthenticated) {
      return <Navigate to="/login" replace />
    }

    // Only animate on first render of the landing page (when no document or contract is active)
    const shouldAnimateGreeting = !hasAnimatedGreeting && !activeDocumentId && !activeContractId

    return (
      <div
        className="h-screen w-screen flex bg-[#C8C8BF] dark:bg-[#1a1a1a] text-[#1A1A1A] dark:text-[#e5e5e5] font-sans overflow-hidden relative transition-colors duration-300"
      >
        {/* Sidebar - Management View */}
        <motion.div
          initial={{ width: isSidebarCollapsed ? 80 : 320 }}
          animate={{ width: isSidebarCollapsed ? 80 : 320 }}
          transition={springConfig}
          className="relative backdrop-blur-md bg-[#b8b8af]/90 dark:bg-[#252525]/90 border-r border-black/10 dark:border-white/10 flex flex-col shadow-lg z-10"
        >
          {/* Header */}
          <div className="p-4 border-b border-black/10 dark:border-white/10">
            <motion.div
              className={`flex items-center ${isSidebarCollapsed ? 'justify-center' : 'justify-between'}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {!isSidebarCollapsed && (
                <motion.h2
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="text-xl font-bold text-[#6f8f88]"
                >
                  Authentia AI
                </motion.h2>
              )}
              <div className={`flex items-center ${isSidebarCollapsed ? 'flex-col gap-3' : 'flex-row gap-2'}`}>
                {!isSidebarCollapsed && <ThemeToggle />}
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
                  className="p-2 hover:bg-black/10 dark:hover:bg-white/10 rounded-lg transition-colors text-[#2a2a2a] dark:text-white"
                >
                  {isSidebarCollapsed ? '→' : '←'}
                </motion.button>
                {isSidebarCollapsed && <ThemeToggle />}
              </div>
            </motion.div>
          </div>

          {/* Contracts List */}
          {!isSidebarCollapsed && (
            <div className="flex-1 overflow-y-auto p-4">
              <div className="flex items-center justify-between mb-3 px-2">
                <p className="text-xs text-[#2a2a2a]/60 dark:text-white/60">CONTRACTS</p>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => { setActiveContractId(null); setActiveContractName(''); setActiveDocumentId(null) }}
                  className="text-xs px-2 py-1 bg-[#6f8f88]/20 text-[#6f8f88] rounded-lg hover:bg-[#6f8f88]/30 transition-colors"
                >
                  + New
                </motion.button>
              </div>
              {contracts.length === 0 ? (
                <p className="text-xs text-[#2a2a2a]/40 dark:text-white/40 px-2 py-4 text-center">No contracts yet</p>
              ) : (
                <motion.div
                  className="space-y-4"
                  initial="hidden"
                  animate="visible"
                  variants={{ visible: { transition: { staggerChildren: 0.05 } } }}
                >
                  {contracts.filter(c => c.pinned).length > 0 && (
                    <div>
                      <p className="text-xs text-[#2a2a2a]/50 dark:text-white/40 px-2 mb-2 flex items-center gap-1">
                        <span>📌</span> PINNED
                      </p>
                      <div className="space-y-2">
                        {contracts.filter(c => c.pinned).map(contract => (
                          <ContractItem
                            key={contract.id}
                            contract={contract}
                            isActive={activeContractId === contract.id}
                            onOpen={() => {
                              setActiveContractId(contract.id)
                              setActiveContractName(contract.name)
                              setActiveDocumentId(null)
                              navigate('/app')
                            }}
                            onPin={(pinned) => pinContract(contract.id, pinned)}
                            onDelete={() => deleteContractItem(contract.id)}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                  {contracts.filter(c => !c.pinned).length > 0 && (
                    <div>
                      {contracts.filter(c => c.pinned).length > 0 && (
                        <p className="text-xs text-[#2a2a2a]/50 dark:text-white/40 px-2 mb-2">CONTRACTS</p>
                      )}
                      <div className="space-y-2">
                        {contracts.filter(c => !c.pinned).map(contract => (
                          <ContractItem
                            key={contract.id}
                            contract={contract}
                            isActive={activeContractId === contract.id}
                            onOpen={() => {
                              setActiveContractId(contract.id)
                              setActiveContractName(contract.name)
                              setActiveDocumentId(null)
                              navigate('/app')
                            }}
                            onPin={(pinned) => pinContract(contract.id, pinned)}
                            onDelete={() => deleteContractItem(contract.id)}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </div>
          )}

          {/* User Info & Actions - Bottom */}
          <div className="p-4 border-t border-black/10 dark:border-white/10">
            {!isSidebarCollapsed && (
              <div className="space-y-3">
                {/* User Info */}
                {user && (
                  <div className="flex items-center gap-3">
                    {user.profile_picture ? (
                      <img
                        src={user.profile_picture}
                        alt={user.username}
                        className="w-8 h-8 rounded-full object-cover"
                        referrerPolicy="no-referrer"
                      />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-[#6f8f88] flex items-center justify-center text-white text-sm font-medium">
                        {user.username?.charAt(0).toUpperCase()}
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-[#1A1A1A] dark:text-white truncate">{user.username}</p>
                      <p className="text-xs text-[#2a2a2a]/50 dark:text-white/50 truncate">{user.email}</p>
                    </div>
                  </div>
                )}
                {/* Action Buttons */}
                <div className="flex items-center gap-2">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => navigate('/')}
                    className="flex-1 px-3 py-2 text-xs bg-[#6f8f88]/20 text-[#6f8f88] rounded-lg hover:bg-[#6f8f88]/30 transition-colors flex items-center justify-center gap-1"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                    </svg>
                    Home
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleLogout}
                    className="flex-1 px-3 py-2 text-xs bg-red-500/20 text-red-700 dark:text-red-400 rounded-lg hover:bg-red-500/30 transition-colors"
                  >
                    Logout
                  </motion.button>
                </div>
                {/* Version */}
                <p className="text-xs text-[#2a2a2a]/40 dark:text-white/40 text-center">Forensic Document Engine v1.0</p>
              </div>
            )}
          </div>
        </motion.div>

        {/* Main Workspace */}
        <div className="flex-1 flex overflow-hidden relative">
          <AnimatePresence mode="wait">
            {activeDocumentId ? (
              <>
                <DocumentViewer
                  key={`document-viewer-${activeDocumentId}`}
                  documentId={activeDocumentId}
                  onClose={closeDocument}
                  activeSpanId={activeSpanId}
                  activeSpan={activeSpan}
                />
                <ContentUnderstander
                  key={`content-understander-${activeDocumentId}`}
                  documentId={activeDocumentId}
                  onSpanHover={handleSpanHover}
                />
              </>
            ) : activeContractId ? (
              <ContractWorkspace
                key={`contract-${activeContractId}`}
                contractId={activeContractId}
                contractName={activeContractName}
                token={token || localStorage.getItem('token') || ''}
                initialFiles={pendingFilesRef.current}
                onFileOpen={(docId) => setActiveDocumentId(docId)}
                onClose={() => {
                  setActiveContractId(null)
                  setActiveContractName('')
                }}
              />
            ) : (
              /* Landing State - Upload Portal */
              <motion.div
                key="landing"
                initial={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95, y: -20 }}
                transition={{ type: "spring", stiffness: 100, damping: 20 }}
                className="w-full h-full flex flex-col items-center justify-center px-8"
              >
                {/* Greeting */}
                <div className="text-center max-w-3xl w-full space-y-6">
                  {(() => {
                    const greeting = getGreeting()
                    const wordCount = greeting.split(' ').length
                    const fontSize = wordCount >= 5 ? 'text-5xl' : 'text-6xl'
                    return (
                      <h1 className={`${fontSize} font-semibold text-[#1A1A1A] dark:text-white tracking-tight`}>
                        {greeting.split(' ').map((word, index) => (
                          <motion.span
                            key={index}
                            initial={shouldAnimateGreeting ? { opacity: 0, y: 10 } : false}
                            animate={{ opacity: 1, y: 0 }}
                            transition={shouldAnimateGreeting ? { duration: 0.4, delay: index * 0.1, ease: "easeOut" } : { duration: 0 }}
                            className="inline-block mr-[0.3em]"
                          >
                            {word}
                          </motion.span>
                        ))}
                      </h1>
                    )
                  })()}
                  <motion.p
                    initial={shouldAnimateGreeting ? { opacity: 0 } : false}
                    animate={{ opacity: 1 }}
                    transition={shouldAnimateGreeting ? { duration: 0.7, delay: 0.8 } : { duration: 0 }}
                    className="text-[#2a2a2a]/70 dark:text-white/70 text-lg"
                  >
                    Create a contract to begin your audit
                  </motion.p>
                </div>

                {/* Create Contract Portal */}
                <motion.div
                  initial={shouldAnimateGreeting ? { opacity: 0, scale: 0.8 } : false}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={shouldAnimateGreeting ? { duration: 0.7, delay: 1.0, ...springConfig } : { duration: 0 }}
                  className="mt-16"
                >
                  <ContractPortal
                    token={token}
                    onCreated={handleContractCreated}
                  />
                </motion.div>

                <motion.p
                  initial={shouldAnimateGreeting ? { opacity: 0 } : false}
                  animate={{ opacity: 1 }}
                  transition={shouldAnimateGreeting ? { duration: 0.7, delay: 1.2 } : { duration: 0 }}
                  className="mt-8 text-xs text-[#2a2a2a]/50 dark:text-white/50"
                >
                  Supports folders, ZIP archives, PDF, DOCX, images
                </motion.p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    )
  }

  const handleSpanHover = useCallback((spanId: string | null, span?: any) => {
    setActiveSpanId(spanId)
    setActiveSpan(span || null)
  }, [])

  const getGreeting = () => {
    const firstName = user?.username?.split(' ')[0] || user?.username || ''

    // 50+ varied greetings
    const greetings = [
      'Hey there', 'Hello', 'Hi', 'Howdy', 'Welcome back',
      'Good to see you', 'Aloha', 'Great to have you', 'Nice to see you', 'Welcome',
      'What\'s up', 'Yo', 'Hey', 'Hiya', 'Greetings',
      'Ahoy', 'Salutations', 'Well hello there',
      'There you are', 'Hey hey', 'Hi there', 'Hello there',
      'Good day', 'Lovely to see you', 'Great to see you back',
      'Welcome aboard', 'Hey friend', 'Hello friend', 'Hi friend',
      'What\'s good', 'Sup', 'Hey now', 'There they are',
      'The legend returns', 'Back at it', 'Good to have you back',
      'Ready to work', 'Let\'s get started', 'Time to shine',
      'Here we go', 'Let\'s do this', 'Ready when you are',
      'At your service', 'Happy to help', 'Welcome to the party',
      'Let\'s roll', 'Game time', 'Buckle up', 'Here we go again',
      'Another day another document', 'Back for more', 'Missed you',
      'Long time no see', 'Fancy seeing you here', 'Well hello',
      'Top of the day', 'Nice of you to drop by', 'Hey superstar',
    ]

    // Use the stable greeting index (random on page load, stable during session)
    const greeting = greetings[greetingIndex % greetings.length]

    return firstName ? `${greeting}, ${firstName}!` : `${greeting}!`
  }

  const closeDocument = useCallback(() => {
    setActiveDocumentId(null)
    // Only reset greeting animation when returning to full landing (no active contract either)
    if (!activeContractId) {
      setHasAnimatedGreeting(false)
    }
  }, [activeContractId])

  const springConfig = {
    type: "spring" as const,
    stiffness: 100,
    damping: 20
  }

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/preview" element={<NewLandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/auth/success" element={<OAuthCallback />} />
      <Route path="/app" element={<MainApp />} />
    </Routes>
  )
}

export default App
