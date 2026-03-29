import { useState, useEffect, useCallback, useRef } from 'react'
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useLocation } from 'react-router-dom'
import { DocumentViewer } from './components/DocumentViewer'
import { ContentUnderstander } from './components/ContentUnderstander'
import { Login } from './components/Login'
import { Register } from './components/Register'
import { OAuthCallback } from './components/OAuthCallback'
import { LandingPage } from './components/landing'
import { LandingPage as NewLandingPage } from './frontpage'
import { ThemeToggle } from './components/ThemeToggle'
import { ContractsGrid } from './components/ContractsGrid'
import { ContractBuilder } from './components/ContractBuilder'

const API_BASE_URL_CONST = 'http://localhost:8002/api/v1'

interface ContractCreated {
  id: string
  name: string
  status: string
  pinned: boolean
  shared: boolean
  created_at: string
  updated_at: string
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
  shared: boolean
  created_at: string
  updated_at: string
  document_count: number
}

// Defined OUTSIDE App so its type identity is stable — no remount on App re-renders

// ─── Sidebar nav components ───────────────────────────────────────────────────

function NavItem({ icon, label, active = false, onClick, shortcut }: {
  icon: React.ReactNode; label: string; active?: boolean
  onClick?: () => void; shortcut?: string
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-2.5 px-2.5 py-[7px] rounded-lg text-sm transition-colors text-left ${
        active
          ? 'bg-black/6 dark:bg-white/8 text-black dark:text-white font-medium'
          : 'text-black/55 dark:text-white/50 hover:bg-black/4 dark:hover:bg-white/6 hover:text-black dark:hover:text-white'
      }`}
    >
      <span className="flex-shrink-0 w-[18px] h-[18px] flex items-center justify-center opacity-70">{icon}</span>
      <span className="flex-1 truncate">{label}</span>
      {shortcut && (
        <kbd className="text-[10px] px-1.5 py-0.5 rounded-md bg-black/6 dark:bg-white/8 text-black/35 dark:text-white/30 font-mono flex-shrink-0">
          {shortcut}
        </kbd>
      )}
    </button>
  )
}

function IconNavItem({ icon, label, active = false, onClick }: {
  icon: React.ReactNode; label: string; active?: boolean; onClick?: () => void
}) {
  return (
    <div className="relative group">
      <button
        onClick={onClick}
        className={`w-9 h-9 flex items-center justify-center rounded-lg transition-colors ${
          active ? 'bg-black/8 dark:bg-white/10 text-black dark:text-white' : 'text-black/40 dark:text-white/35 hover:bg-black/6 dark:hover:bg-white/8 hover:text-black dark:hover:text-white'
        }`}
      >
        {icon}
      </button>
      <div className="absolute left-full ml-2.5 top-1/2 -translate-y-1/2 z-50 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-100">
        <div className="bg-[#1a1a1a] dark:bg-[#e5e5e5] text-white dark:text-black text-xs rounded-lg px-2.5 py-1.5 whitespace-nowrap shadow-xl font-medium">
          {label}
        </div>
      </div>
    </div>
  )
}

// ─── SVG icons ────────────────────────────────────────────────────────────────
const IcHome = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" className="w-[18px] h-[18px]"><path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/><path d="M9 21V12h6v9"/></svg>
const IcSearch = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" className="w-[18px] h-[18px]"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
const IcGrid = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" className="w-[18px] h-[18px]"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
const IcStar = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" className="w-[18px] h-[18px]"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
const IcPerson = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" className="w-[18px] h-[18px]"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>
const IcPeople = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" className="w-[18px] h-[18px]"><circle cx="9" cy="8" r="3.5"/><path d="M2 20c0-3.3 3.1-6 7-6s7 2.7 7 6"/><circle cx="17" cy="8" r="3"/><path d="M22 20c0-2.8-2.2-5-5-5"/></svg>
const IcDiamond = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" className="w-[18px] h-[18px]"><path d="M6 3h12l4 6-10 12L2 9z"/><path d="M2 9h20"/></svg>
const IcSidebarOpen = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" className="w-[18px] h-[18px]"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/></svg>
const IcSignOut = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" className="w-[18px] h-[18px]"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
const IcBuilder = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" className="w-[18px] h-[18px]"><circle cx="5" cy="12" r="2"/><circle cx="19" cy="5" r="2"/><circle cx="19" cy="19" r="2"/><path d="M7 12h4m4-5.5-4 4m4 6-4-4"/></svg>

// ─────────────────────────────────────────────────────────────────────────────

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
  const [contractFilter, setContractFilter] = useState<'all' | 'pinned' | 'created' | 'shared'>('all')
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const userMenuRef = useRef<HTMLDivElement>(null)
  const [activeDocumentId, setActiveDocumentId] = useState<string | null>(null)
  const [activeSpanId, setActiveSpanId] = useState<string | null>(null)
  const [activeSpan, setActiveSpan] = useState<any>(null)
  const [hasAnimatedGreeting, setHasAnimatedGreeting] = useState(false)
  const [greetingIndex] = useState(() => Math.floor(Math.random() * 55)) // Random on initial load, stable during session

  // Collapse sidebar whenever a contract is opened
  useEffect(() => {
    if (activeContractId) setIsSidebarCollapsed(true)
  }, [activeContractId])

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

    const location = useLocation()
    const isGridRoute = ['/app/allcontracts', '/app/me', '/app/shared'].includes(location.pathname)

    // Only animate on first render of the landing page (when no document or contract is active)
    const shouldAnimateGreeting = !hasAnimatedGreeting && !activeDocumentId && !activeContractId && !isGridRoute

    // ── Sidebar data ──────────────────────────────────────────────────────────
    const filteredContracts = contracts.filter(c => {
      if (contractFilter === 'pinned') return c.pinned
      return true
    })
    const recentContracts = [...contracts]
      .sort((a, b) => (b.updated_at || b.created_at).localeCompare(a.updated_at || a.created_at))
      .slice(0, 10)
    const userInitial = user?.username?.charAt(0).toUpperCase() ?? '?'

    // Close user menu on outside click
    const handleUserMenuBlur = (e: React.FocusEvent<HTMLDivElement>) => {
      if (!e.currentTarget.contains(e.relatedTarget as Node)) setUserMenuOpen(false)
    }

    return (
      <div className="h-screen w-screen flex bg-white dark:bg-black text-[#1A1A1A] dark:text-[#e5e5e5] font-sans overflow-hidden relative transition-colors duration-300">

        {/* ── Sidebar ── */}
        <motion.div
          initial={{ width: isSidebarCollapsed ? 56 : 260 }}
          animate={{ width: isSidebarCollapsed ? 56 : 260 }}
          transition={springConfig}
          className="relative flex-shrink-0 bg-white dark:bg-black border-r border-black/8 dark:border-white/8 flex flex-col z-10 overflow-hidden"
        >
          {isSidebarCollapsed ? (
            /* ── Collapsed: icon rail ── */
            <div className="flex flex-col items-center py-3 gap-1 flex-1 overflow-y-auto px-2">
              {/* Expand button */}
              <IconNavItem icon={<IcSidebarOpen />} label="Expand sidebar" onClick={() => setIsSidebarCollapsed(false)} />
              {/* Avatar */}
              <div className="relative group my-1">
                {user?.profile_picture ? (
                  <img src={user.profile_picture} alt={user.username} referrerPolicy="no-referrer"
                    className="w-8 h-8 rounded-lg object-cover cursor-pointer" onClick={() => setUserMenuOpen(v => !v)} />
                ) : (
                  <button onClick={() => setUserMenuOpen(v => !v)}
                    className="w-8 h-8 rounded-lg bg-[#6f8f88] flex items-center justify-center text-white text-sm font-bold">
                    {userInitial}
                  </button>
                )}
                <div className="absolute left-full ml-2.5 top-1/2 -translate-y-1/2 z-50 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-100">
                  <div className="bg-[#1a1a1a] dark:bg-[#e5e5e5] text-white dark:text-black text-xs rounded-lg px-2.5 py-1.5 whitespace-nowrap shadow-xl font-medium">
                    {user?.username ?? 'Account'}
                  </div>
                </div>
              </div>
              <div className="h-px w-8 bg-black/8 dark:bg-white/8 my-1" />
              <IconNavItem icon={<IcHome />} label="Home" onClick={() => navigate('/')} />
              <IconNavItem icon={<IcSearch />} label="Search" />
              <IconNavItem icon={<IcBuilder />} label="Builder" active={location.pathname === '/app/builder'} onClick={() => navigate('/app/builder')} />
              <div className="h-px w-8 bg-black/8 dark:bg-white/8 my-1" />
              <IconNavItem icon={<IcGrid />} label="All contracts" active={location.pathname === '/app/allcontracts'} onClick={() => { setContractFilter('all'); navigate('/app/allcontracts') }} />
              <IconNavItem icon={<IcStar />} label="Pinned" active={contractFilter === 'pinned'} onClick={() => { setContractFilter('pinned'); navigate('/app/allcontracts') }} />
              <IconNavItem icon={<IcPerson />} label="Created by me" active={location.pathname === '/app/me'} onClick={() => { setContractFilter('all'); navigate('/app/me') }} />
              <IconNavItem icon={<IcPeople />} label="Shared with me" active={location.pathname === '/app/shared'} onClick={() => { setContractFilter('all'); navigate('/app/shared') }} />
            </div>
          ) : (
            /* ── Expanded ── */
            <>
              {/* Header: workspace selector */}
              <div className="flex items-center gap-2 px-3 py-3 border-b border-black/6 dark:border-white/6 flex-shrink-0">
                {user?.profile_picture ? (
                  <img src={user.profile_picture} alt={user.username} referrerPolicy="no-referrer"
                    className="w-6 h-6 rounded-md object-cover flex-shrink-0" />
                ) : (
                  <div className="w-6 h-6 rounded-md bg-[#6f8f88] flex items-center justify-center text-white text-[11px] font-bold flex-shrink-0">
                    {userInitial}
                  </div>
                )}
                <span className="text-sm font-semibold text-black dark:text-white flex-1 truncate">
                  {user?.username ?? 'Authentia'}
                </span>
                <button
                  onClick={() => setIsSidebarCollapsed(true)}
                  className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-black/6 dark:hover:bg-white/8 transition-colors text-black/35 dark:text-white/35 flex-shrink-0"
                >
                  <IcSidebarOpen />
                </button>
              </div>

              {/* Nav items */}
              <div className="flex-1 overflow-y-auto px-2 py-2">
                <NavItem icon={<IcHome />} label="Home" onClick={() => navigate('/')} />
                <NavItem icon={<IcSearch />} label="Search" shortcut="⌘K" />
                <NavItem icon={<IcBuilder />} label="Builder" active={location.pathname === '/app/builder'} onClick={() => navigate('/app/builder')} />

                {/* Contracts section */}
                <p className="text-[11px] font-semibold text-black/35 dark:text-white/30 uppercase tracking-widest px-2.5 pt-5 pb-1.5">
                  Contracts
                </p>
                <NavItem icon={<IcGrid />} label="All contracts" active={location.pathname === '/app/allcontracts'} onClick={() => { setContractFilter('all'); navigate('/app/allcontracts') }} />
                <NavItem icon={<IcStar />} label="Pinned" active={contractFilter === 'pinned' && location.pathname === '/app/allcontracts'} onClick={() => { setContractFilter('pinned'); navigate('/app/allcontracts') }} />
                <NavItem icon={<IcPerson />} label="Created by me" active={location.pathname === '/app/me'} onClick={() => { setContractFilter('all'); navigate('/app/me') }} />
                <NavItem icon={<IcPeople />} label="Shared with me" active={location.pathname === '/app/shared'} onClick={() => { setContractFilter('all'); navigate('/app/shared') }} />


                {/* Recents section */}
                {recentContracts.length > 0 && (
                  <>
                    <p className="text-[11px] font-semibold text-black/35 dark:text-white/30 uppercase tracking-widest px-2.5 pt-5 pb-1.5">
                      Recents
                    </p>
                    {recentContracts.map(contract => (
                      <NavItem
                        key={contract.id}
                        icon={<IcDiamond />}
                        label={contract.name}
                        active={activeContractId === contract.id}
                        onClick={() => { setActiveContractId(contract.id); setActiveContractName(contract.name); setActiveDocumentId(null); navigate('/app') }}
                      />
                    ))}
                  </>
                )}
              </div>

              {/* Bottom: new contract + theme */}
              <div className="px-3 py-3 border-t border-black/6 dark:border-white/6 flex items-center gap-2 flex-shrink-0">
                <button
                  onClick={() => { setActiveContractId(null); setActiveContractName(''); setActiveDocumentId(null) }}
                  className="flex-1 text-sm py-1.5 rounded-lg border border-black/10 dark:border-white/10 hover:bg-black/4 dark:hover:bg-white/6 transition-colors text-black/50 dark:text-white/45 text-left px-3"
                >
                  + New contract
                </button>
                <ThemeToggle />
              </div>
            </>
          )}
        </motion.div>

        {/* ── User menu (top-right floating) ── */}
        <div
          ref={userMenuRef}
          className="absolute top-3 right-4 z-50"
          tabIndex={-1}
          onBlur={handleUserMenuBlur}
        >
          <button
            onClick={() => setUserMenuOpen(v => !v)}
            className="flex items-center justify-center"
          >
            {user?.profile_picture ? (
              <img src={user.profile_picture} alt={user.username} referrerPolicy="no-referrer"
                className="w-8 h-8 rounded-full object-cover ring-2 ring-black/8 dark:ring-white/10 hover:ring-[#6f8f88]/50 transition-all" />
            ) : (
              <div className="w-8 h-8 rounded-full bg-[#6f8f88] flex items-center justify-center text-white text-sm font-bold ring-2 ring-[#6f8f88]/20 hover:ring-[#6f8f88]/50 transition-all">
                {userInitial}
              </div>
            )}
          </button>

          <AnimatePresence>
            {userMenuOpen && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95, y: -4 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: -4 }}
                transition={{ duration: 0.12 }}
                className="absolute right-0 top-full mt-2 w-56 rounded-2xl bg-white dark:bg-[#1a1a1a] border border-black/8 dark:border-white/10 shadow-2xl overflow-hidden"
              >
                {/* User info header */}
                <div className="flex items-center gap-3 px-4 py-3 border-b border-black/6 dark:border-white/6">
                  {user?.profile_picture ? (
                    <img src={user.profile_picture} alt={user.username} referrerPolicy="no-referrer"
                      className="w-9 h-9 rounded-full object-cover flex-shrink-0" />
                  ) : (
                    <div className="w-9 h-9 rounded-full bg-[#6f8f88] flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                      {userInitial}
                    </div>
                  )}
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-black dark:text-white truncate">{user?.username}</p>
                    <p className="text-xs text-black/45 dark:text-white/40 truncate">{user?.email}</p>
                  </div>
                </div>
                {/* Sign out */}
                <button
                  onClick={() => { setUserMenuOpen(false); handleLogout() }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-black/70 dark:text-white/70 hover:bg-black/4 dark:hover:bg-white/6 transition-colors"
                >
                  <IcSignOut />
                  Sign out
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Main Workspace */}
        <div className="flex-1 flex overflow-hidden relative">
          {isGridRoute ? (
            <ContractsGrid
              key={location.pathname + contractFilter}
              title={
                location.pathname === '/app/allcontracts'
                  ? (contractFilter === 'pinned' ? 'Pinned' : 'All Contracts')
                  : location.pathname === '/app/me'
                  ? 'Created by Me'
                  : 'Shared with Me'
              }
              contracts={location.pathname === '/app/shared' ? [] : contracts}
              user={user}
              token={token}
              filter={location.pathname === '/app/allcontracts' ? (contractFilter === 'pinned' ? 'pinned' : 'all') : location.pathname === '/app/me' ? 'me' : 'shared'}
              hideNew={location.pathname === '/app/me' || location.pathname === '/app/shared' || contractFilter === 'pinned'}
              onOpenContract={(id, name) => { setActiveContractId(id); setActiveContractName(name); setActiveDocumentId(null); navigate('/app') }}
              onNewContract={() => { setActiveContractId(null); setActiveContractName(''); setActiveDocumentId(null); navigate('/app') }}
              onContractsChange={setContracts}
            />
          ) : (
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
              <ContractBuilder
                key={`contract-${activeContractId}`}
                contractId={activeContractId}
                contractName={activeContractName}
                token={token || localStorage.getItem('token') || ''}
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
          )}
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
      <Route path="/app/allcontracts" element={<MainApp />} />
      <Route path="/app/me" element={<MainApp />} />
      <Route path="/app/shared" element={<MainApp />} />
      <Route path="/app/builder" element={<ContractBuilder />} />
    </Routes>
  )
}

export default App
