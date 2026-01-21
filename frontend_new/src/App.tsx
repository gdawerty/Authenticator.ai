import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { DocumentViewer } from './components/DocumentViewer'
import { ContentUnderstander } from './components/ContentUnderstander'
import { Login } from './components/Login'
import { Register } from './components/Register'

const API_BASE_URL = 'http://localhost:8002/api/v1'

interface User {
  id: string
  email: string
  username: string
}

interface Audit {
  id: string
  name: string
  timestamp: Date
  status: 'clean' | 'warning' | 'flagged'
  documentId: string
}

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showRegister, setShowRegister] = useState(false)
  const [audits, setAudits] = useState<Audit[]>([])
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [activeDocumentId, setActiveDocumentId] = useState<string | null>(null)
  const [activeSpanId, setActiveSpanId] = useState<string | null>(null)
  const [activeSpan, setActiveSpan] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

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
      }
    } catch (error) {
      console.error('Failed to load audits:', error)
    }
  }

  // Check if user is already logged in on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    if (storedToken && storedUser) {
      setToken(storedToken)
      const userData = JSON.parse(storedUser)
      setUser(userData)
      setIsAuthenticated(true)
      // Load audits when user is logged in
      loadAudits(storedToken)
    }
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
    // Load audits after login
    loadAudits(data.access_token)
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
    setToken(null)
    setUser(null)
    setIsAuthenticated(false)
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // Show login/register if not authenticated
  if (!isAuthenticated) {
    return showRegister ? (
      <Register
        onRegister={handleRegister}
        onSwitchToLogin={() => setShowRegister(false)}
      />
    ) : (
      <Login
        onLogin={handleLogin}
        onSwitchToRegister={() => setShowRegister(true)}
      />
    )
  }

  const handleSpanHover = (spanId: string | null, span?: any) => {
    setActiveSpanId(spanId)
    setActiveSpan(span || null)
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good Morning!'
    if (hour < 18) return 'Good Afternoon!'
    return 'Good Evening!'
  }

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.currentTarget === e.target) {
      setIsDragging(false)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      await uploadDocument(files[0])
    }
  }

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await uploadDocument(e.target.files[0])
    }
  }

  const uploadDocument = async (file: File) => {
    setIsProcessing(true)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${API_BASE_URL}/upload/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const data = await response.json()

      // Save audit to database
      try {
        const auditResponse = await fetch(`${API_BASE_URL}/audits`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            name: file.name,
            document_id: data.id,
            status: 'clean'
          })
        })

        if (auditResponse.ok) {
          const auditData = await auditResponse.json()
          const newAudit: Audit = {
            id: auditData.id,
            name: auditData.name,
            timestamp: new Date(auditData.created_at),
            status: auditData.status as 'clean' | 'warning' | 'flagged',
            documentId: auditData.document_id || ''
          }
          setAudits([newAudit, ...audits])
        }
      } catch (error) {
        console.error('Failed to save audit:', error)
        // Still show the audit locally even if save fails
        const newAudit: Audit = {
          id: Date.now().toString(),
          name: file.name,
          timestamp: new Date(),
          status: 'clean',
          documentId: data.id
        }
        setAudits([newAudit, ...audits])
      }

      setActiveDocumentId(data.id)

    } catch (error) {
      console.error('Upload error:', error)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      alert(`Failed to upload document: ${errorMessage}`)
    } finally {
      setIsProcessing(false)
    }
  }

  const openAudit = (audit: Audit) => {
    setActiveDocumentId(audit.documentId)
  }

  const closeDocument = () => {
    setActiveDocumentId(null)
  }

  const springConfig = {
    type: "spring" as const,
    stiffness: 100,
    damping: 20
  }

  return (
    <div
      className="h-screen w-screen flex bg-[#C8C8BF] text-[#1A1A1A] font-sans overflow-hidden relative"
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Background Blur Overlay when dragging */}
      <AnimatePresence>
        {isDragging && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 backdrop-blur-sm bg-black/20 z-40 pointer-events-none"
          />
        )}
      </AnimatePresence>

      {/* Sidebar - Management View */}
      <motion.div
        initial={{ width: isSidebarCollapsed ? 80 : 320 }}
        animate={{ width: isSidebarCollapsed ? 80 : 320 }}
        transition={springConfig}
        className="relative backdrop-blur-md bg-[#b8b8af]/90 border-r border-black/10 flex flex-col shadow-lg z-10"
      >
        {/* Header */}
        <div className="p-6 border-b border-black/10">
          <motion.div
            className="flex items-center justify-between"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {!isSidebarCollapsed && (
              <div className="flex-1">
                <motion.h2
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="text-xl font-bold text-[#6f8f88]"
                >
                  Authentia AI
                </motion.h2>
                {user && (
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-xs text-[#2a2a2a]/60 mt-1"
                  >
                    {user.username}
                  </motion.p>
                )}
              </div>
            )}
            <div className="flex items-center gap-2">
              {!isSidebarCollapsed && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleLogout}
                  className="px-3 py-1.5 text-xs bg-red-500/20 text-red-700 rounded-lg hover:bg-red-500/30 transition-colors"
                >
                  Logout
                </motion.button>
              )}
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
                className="p-2 hover:bg-black/10 rounded-lg transition-colors text-[#2a2a2a]"
              >
                {isSidebarCollapsed ? '→' : '←'}
              </motion.button>
            </div>
          </motion.div>
        </div>

        {/* Recent Audits */}
        {!isSidebarCollapsed && (
          <div className="flex-1 overflow-y-auto p-4">
            <p className="text-xs text-[#2a2a2a]/60 mb-3 px-2">RECENT AUDITS</p>
            <motion.div
              className="space-y-2"
              initial="hidden"
              animate="visible"
              variants={{
                visible: {
                  transition: {
                    staggerChildren: 0.05
                  }
                }
              }}
            >
              {audits.length === 0 ? (
                <p className="text-xs text-[#2a2a2a]/40 px-2 py-4 text-center">No audits yet</p>
              ) : (
                audits.map(audit => (
                  <motion.div
                    key={audit.id}
                    variants={{
                      hidden: { opacity: 0, y: 20 },
                      visible: { opacity: 1, y: 0 }
                    }}
                    whileHover={{ scale: 1.02, x: 4 }}
                    transition={springConfig}
                    onClick={() => openAudit(audit)}
                    className="p-4 rounded-xl backdrop-blur-sm bg-white/30 border border-black/10 cursor-pointer hover:bg-white/40 transition-all"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm truncate text-[#1A1A1A]">{audit.name}</p>
                        <p className="text-xs text-[#2a2a2a]/60 mt-1">
                          {audit.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: "spring", stiffness: 500, damping: 25 }}
                        className={`w-2 h-2 rounded-full ml-2 flex-shrink-0 ${
                          audit.status === 'clean' ? 'bg-green-500 shadow-md shadow-green-500/50' :
                          audit.status === 'warning' ? 'bg-yellow-500 shadow-md shadow-yellow-500/50' :
                          'bg-red-500 shadow-md shadow-red-500/50'
                        }`}
                      />
                    </div>
                  </motion.div>
                ))
              )}
            </motion.div>
          </div>
        )}

        {/* Platform Info */}
        <div className="p-4 border-t border-black/10">
          {!isSidebarCollapsed && (
            <p className="text-xs text-[#2a2a2a]/50">Forensic Document Engine v1.0</p>
          )}
        </div>
      </motion.div>

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden relative">
        <AnimatePresence mode="wait">
          {activeDocumentId ? (
            /* Document Viewer with Content Understander */
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
                <h1 className="text-6xl font-semibold text-[#1A1A1A] tracking-tight">
                  {getGreeting().split('').map((char, index) => (
                    <motion.span
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{
                        duration: 0.3,
                        delay: index * 0.05,
                        ease: "easeOut"
                      }}
                      className="inline-block"
                    >
                      {char === ' ' ? '\u00A0' : char}
                    </motion.span>
                  ))}
                </h1>
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.7, delay: 0.8 }}
                  className="text-[#2a2a2a]/70 text-lg"
                >
                  Drop a document to begin forensic analysis
                </motion.p>
              </div>

              {/* Circular Upload Portal */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.7, delay: 1.0, ...springConfig }}
                className="mt-16"
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={handleFileSelect}
                  className="hidden"
                  accept=".pdf,.docx,.doc,.png,.jpg,.jpeg"
                  disabled={isProcessing}
                />

                <motion.button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isProcessing}
                  whileHover={{ scale: 1.05, y: -8, boxShadow: '0 35px 60px -15px rgba(0, 0, 0, 0.25)' }}
                  whileTap={{ scale: 0.95 }}
                  animate={
                    isDragging
                      ? {
                          borderColor: ['#708090', 'rgba(112, 128, 144, 0.3)', '#708090'],
                          scale: 1.15,
                          y: -12
                        }
                      : isProcessing
                      ? {
                          rotate: 360
                        }
                      : {}
                  }
                  transition={
                    isDragging
                      ? { duration: 2, repeat: Infinity, ease: "easeInOut", type: "spring", stiffness: 100, damping: 20 }
                      : isProcessing
                      ? { duration: 2, repeat: Infinity, ease: "linear" }
                      : { type: "spring", stiffness: 300, damping: 25 }
                  }
                  className={`relative w-48 h-48 rounded-full backdrop-blur-md transition-all ${
                    isDragging
                      ? 'border-2 border-dashed border-[#708090] bg-white/50'
                      : 'border border-black/10 bg-white/30 hover:bg-white/40 hover:border-[#6f8f88]/50'
                  } ${isProcessing ? 'opacity-75 cursor-wait' : 'cursor-pointer'}`}
                  style={{
                    boxShadow: isDragging
                      ? '0 40px 80px -12px rgba(112, 128, 144, 0.5), 0 0 60px rgba(112, 128, 144, 0.3)'
                      : '0 25px 50px -12px rgba(0, 0, 0, 0.15)'
                  }}
                >
                  <div className="flex flex-col items-center justify-center h-full gap-3">
                    <motion.div
                      animate={isProcessing ? { scale: [1, 1.2, 1] } : {}}
                      transition={{ duration: 1.5, repeat: Infinity }}
                      className="text-6xl"
                    >
                      {isProcessing ? '⏳' : '📎'}
                    </motion.div>
                    <p className="text-[#2a2a2a] text-sm font-medium px-6 text-center">
                      {isProcessing ? 'Processing...' : isDragging ? 'Drop Here' : 'Upload Document'}
                    </p>
                  </div>
                </motion.button>
              </motion.div>

              {/* Supported formats hint */}
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.7, delay: 1.2 }}
                className="mt-8 text-xs text-[#2a2a2a]/50"
              >
                Supports: PDF, DOCX, DOC, PNG, JPG
              </motion.p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

export default App
