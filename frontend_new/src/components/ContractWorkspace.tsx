import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const API_BASE_URL = 'http://localhost:8002/api/v1'

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
  onFileOpen: (documentId: string) => void
  onClose: () => void
}

function fileIcon(type: string) {
  switch (type) {
    case 'pdf': return '📄'
    case 'docx': return '📝'
    case 'image': return '🖼️'
    default: return '📎'
  }
}

function FolderTree({
  folders,
  selectedFolderId,
  onSelect,
  depth = 0
}: {
  folders: FolderNode[]
  selectedFolderId: string | null
  onSelect: (id: string | null) => void
  depth?: number
}) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  const toggle = (id: string) => {
    setExpanded(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  return (
    <div className={depth > 0 ? 'ml-3 border-l border-black/10 dark:border-white/10 pl-2' : ''}>
      {folders.map(folder => (
        <div key={folder.id}>
          <div
            className={`flex items-center gap-1.5 px-2 py-1.5 rounded-lg cursor-pointer text-sm transition-colors ${
              selectedFolderId === folder.id
                ? 'bg-[#6f8f88]/20 text-[#6f8f88]'
                : 'hover:bg-black/5 dark:hover:bg-white/5 text-[#1A1A1A] dark:text-white'
            }`}
            onClick={() => {
              onSelect(folder.id)
              if (folder.children.length > 0) toggle(folder.id)
            }}
          >
            {folder.children.length > 0 && (
              <span className="text-xs opacity-50 w-3 text-center">
                {expanded.has(folder.id) ? '▾' : '▸'}
              </span>
            )}
            {folder.children.length === 0 && <span className="w-3" />}
            <span>📁</span>
            <span className="truncate">{folder.name}</span>
            {folder.documents.length > 0 && (
              <span className="ml-auto text-xs opacity-40">{folder.documents.length}</span>
            )}
          </div>
          {folder.children.length > 0 && expanded.has(folder.id) && (
            <FolderTree
              folders={folder.children}
              selectedFolderId={selectedFolderId}
              onSelect={onSelect}
              depth={depth + 1}
            />
          )}
        </div>
      ))}
    </div>
  )
}

export function ContractWorkspace({ contractId, contractName, token, onFileOpen, onClose }: Props) {
  const [contract, setContract] = useState<ContractDetail | null>(null)
  const [selectedFolderId, setSelectedFolderId] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [isCreatingFolder, setIsCreatingFolder] = useState(false)
  const [newFolderName, setNewFolderName] = useState('')
  const [uploadProgress, setUploadProgress] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const zipInputRef = useRef<HTMLInputElement>(null)
  const newFolderInputRef = useRef<HTMLInputElement>(null)

  const loadContract = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/contracts/${contractId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setContract(data)
      }
    } catch (e) {
      console.error('Failed to load contract', e)
    }
  }, [contractId, token])

  useEffect(() => { loadContract() }, [loadContract])

  useEffect(() => {
    if (isCreatingFolder && newFolderInputRef.current) {
      newFolderInputRef.current.focus()
    }
  }, [isCreatingFolder])

  const currentFiles = (): DocumentSummary[] => {
    if (!contract) return []
    if (!selectedFolderId) return contract.root_documents
    const findFolder = (folders: FolderNode[]): FolderNode | null => {
      for (const f of folders) {
        if (f.id === selectedFolderId) return f
        const found = findFolder(f.children)
        if (found) return found
      }
      return null
    }
    return findFolder(contract.folders)?.documents ?? []
  }

  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) return
    try {
      const res = await fetch(`${API_BASE_URL}/contracts/${contractId}/folders`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newFolderName.trim(), parent_id: selectedFolderId })
      })
      if (res.ok) {
        setNewFolderName('')
        setIsCreatingFolder(false)
        await loadContract()
      }
    } catch (e) {
      console.error('Failed to create folder', e)
    }
  }

  const uploadFile = async (file: File, folderId: string | null) => {
    const formData = new FormData()
    formData.append('file', file)
    if (folderId) formData.append('folder_id', folderId)

    const res = await fetch(`${API_BASE_URL}/contracts/${contractId}/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error((err as any).detail || 'Upload failed')
    }
    return res.json()
  }

  const uploadZip = async (file: File, folderId: string | null) => {
    setUploadProgress('Extracting ZIP...')
    const formData = new FormData()
    formData.append('file', file)
    if (folderId) formData.append('folder_id', folderId)

    const res = await fetch(`${API_BASE_URL}/contracts/${contractId}/upload-zip`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error((err as any).detail || 'ZIP upload failed')
    }
    return res.json()
  }

  const handleFiles = async (files: File[]) => {
    if (files.length === 0) return
    setIsUploading(true)
    setUploadProgress(null)

    try {
      // Separate ZIPs from regular files
      const zips = files.filter(f => f.name.toLowerCase().endsWith('.zip'))
      const regular = files.filter(f => !f.name.toLowerCase().endsWith('.zip'))

      for (let i = 0; i < zips.length; i++) {
        setUploadProgress(`Extracting ZIP ${i + 1}/${zips.length}...`)
        await uploadZip(zips[i], selectedFolderId)
      }

      for (let i = 0; i < regular.length; i++) {
        setUploadProgress(`Uploading ${i + 1}/${regular.length}: ${regular[i].name}`)
        await uploadFile(regular[i], selectedFolderId)
      }

      await loadContract()
    } catch (e) {
      console.error('Upload error', e)
      alert(`Upload failed: ${e instanceof Error ? e.message : 'Unknown error'}`)
    } finally {
      setIsUploading(false)
      setUploadProgress(null)
    }
  }

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.currentTarget === e.target) setIsDragging(false)
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
    await handleFiles(files)
  }

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      await handleFiles(Array.from(e.target.files))
      e.target.value = ''
    }
  }

  const files = currentFiles()

  const getBreadcrumb = () => {
    if (!contract || !selectedFolderId) return []
    const path: FolderNode[] = []
    const find = (folders: FolderNode[], id: string): boolean => {
      for (const f of folders) {
        if (f.id === id) { path.push(f); return true }
        if (find(f.children, id)) { path.unshift(f); return true }
      }
      return false
    }
    find(contract.folders, selectedFolderId)
    return path
  }

  return (
    <div
      className="flex-1 flex flex-col overflow-hidden relative"
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Drag overlay */}
      <AnimatePresence>
        {isDragging && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-50 backdrop-blur-sm bg-[#6f8f88]/20 border-2 border-dashed border-[#6f8f88] flex items-center justify-center pointer-events-none"
          >
            <div className="text-center">
              <div className="text-6xl mb-4">📂</div>
              <p className="text-xl font-semibold text-[#6f8f88]">Drop files here</p>
              <p className="text-sm text-[#6f8f88]/70 mt-1">ZIPs will be extracted automatically</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-black/10 dark:border-white/10 bg-[#b8b8af]/30 dark:bg-[#252525]/30">
        <button
          onClick={onClose}
          className="p-1.5 hover:bg-black/10 dark:hover:bg-white/10 rounded-lg transition-colors text-[#2a2a2a] dark:text-white"
        >
          ←
        </button>
        <div>
          <h2 className="font-semibold text-[#1A1A1A] dark:text-white">{contractName}</h2>
          {contract && (
            <p className="text-xs text-[#2a2a2a]/50 dark:text-white/50">
              {(contract.folders.length + contract.root_documents.length)} items
            </p>
          )}
        </div>
        <div className="ml-auto flex items-center gap-2">
          <input ref={fileInputRef} type="file" multiple className="hidden" onChange={handleFileInput}
            accept=".pdf,.docx,.doc,.png,.jpg,.jpeg" />
          <input ref={zipInputRef} type="file" className="hidden" onChange={handleFileInput}
            accept=".zip" />
          <motion.button
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            onClick={() => setIsCreatingFolder(true)}
            className="px-3 py-1.5 text-xs bg-white/30 dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-lg hover:bg-white/50 dark:hover:bg-white/10 transition-colors text-[#1A1A1A] dark:text-white flex items-center gap-1.5"
          >
            <span>📁</span> New Folder
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="px-3 py-1.5 text-xs bg-white/30 dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-lg hover:bg-white/50 dark:hover:bg-white/10 transition-colors text-[#1A1A1A] dark:text-white flex items-center gap-1.5 disabled:opacity-50"
          >
            <span>⬆️</span> Upload Files
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            onClick={() => zipInputRef.current?.click()}
            disabled={isUploading}
            className="px-3 py-1.5 text-xs bg-[#6f8f88]/20 text-[#6f8f88] border border-[#6f8f88]/30 rounded-lg hover:bg-[#6f8f88]/30 transition-colors flex items-center gap-1.5 disabled:opacity-50"
          >
            <span>🗜️</span> Upload ZIP
          </motion.button>
        </div>
      </div>

      {/* New folder input */}
      <AnimatePresence>
        {isCreatingFolder && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden border-b border-black/10 dark:border-white/10"
          >
            <div className="px-6 py-3 bg-[#6f8f88]/5 flex items-center gap-3">
              <span>📁</span>
              <input
                ref={newFolderInputRef}
                type="text"
                value={newFolderName}
                onChange={e => setNewFolderName(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter') handleCreateFolder()
                  if (e.key === 'Escape') { setIsCreatingFolder(false); setNewFolderName('') }
                }}
                placeholder={selectedFolderId ? 'Subfolder name...' : 'Folder name...'}
                className="flex-1 bg-transparent outline-none text-sm text-[#1A1A1A] dark:text-white placeholder-[#2a2a2a]/40 dark:placeholder-white/40"
              />
              <button onClick={handleCreateFolder}
                className="text-xs px-3 py-1 bg-[#6f8f88] text-white rounded-lg hover:bg-[#5a7a73] transition-colors">
                Create
              </button>
              <button onClick={() => { setIsCreatingFolder(false); setNewFolderName('') }}
                className="text-xs px-3 py-1 bg-black/10 dark:bg-white/10 rounded-lg hover:bg-black/20 dark:hover:bg-white/20 transition-colors text-[#1A1A1A] dark:text-white">
                Cancel
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Folder tree sidebar */}
        <div className="w-56 border-r border-black/10 dark:border-white/10 overflow-y-auto p-3 bg-[#b8b8af]/20 dark:bg-[#1e1e1e]/40 flex-shrink-0">
          <p className="text-xs text-[#2a2a2a]/50 dark:text-white/50 px-2 mb-2 font-medium">FOLDERS</p>
          {/* Root option */}
          <div
            className={`flex items-center gap-1.5 px-2 py-1.5 rounded-lg cursor-pointer text-sm transition-colors mb-1 ${
              selectedFolderId === null
                ? 'bg-[#6f8f88]/20 text-[#6f8f88]'
                : 'hover:bg-black/5 dark:hover:bg-white/5 text-[#1A1A1A] dark:text-white'
            }`}
            onClick={() => setSelectedFolderId(null)}
          >
            <span>🏠</span>
            <span className="truncate font-medium">Root</span>
            {contract && contract.root_documents.length > 0 && (
              <span className="ml-auto text-xs opacity-40">{contract.root_documents.length}</span>
            )}
          </div>
          {contract && (
            <FolderTree
              folders={contract.folders}
              selectedFolderId={selectedFolderId}
              onSelect={setSelectedFolderId}
            />
          )}
        </div>

        {/* File area */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Breadcrumb */}
          <div className="flex items-center gap-1 text-xs text-[#2a2a2a]/50 dark:text-white/50 mb-4">
            <button onClick={() => setSelectedFolderId(null)}
              className="hover:text-[#6f8f88] transition-colors">{contractName}</button>
            {getBreadcrumb().map(f => (
              <span key={f.id} className="flex items-center gap-1">
                <span>/</span>
                <button onClick={() => setSelectedFolderId(f.id)}
                  className="hover:text-[#6f8f88] transition-colors">{f.name}</button>
              </span>
            ))}
          </div>

          {/* Upload progress */}
          <AnimatePresence>
            {isUploading && uploadProgress && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mb-4 px-4 py-3 bg-[#6f8f88]/10 border border-[#6f8f88]/20 rounded-xl flex items-center gap-3"
              >
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  className="text-xl"
                >⏳</motion.div>
                <p className="text-sm text-[#6f8f88]">{uploadProgress}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Files grid */}
          {files.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-center">
              <div className="text-5xl mb-4 opacity-30">📂</div>
              <p className="text-sm text-[#2a2a2a]/40 dark:text-white/40">
                {isUploading ? 'Processing...' : 'Drop files here or use the buttons above'}
              </p>
            </div>
          ) : (
            <motion.div
              className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3"
              initial="hidden"
              animate="visible"
              variants={{ visible: { transition: { staggerChildren: 0.04 } } }}
            >
              {files.map(doc => (
                <motion.div
                  key={doc.id}
                  variants={{ hidden: { opacity: 0, scale: 0.9 }, visible: { opacity: 1, scale: 1 } }}
                  whileHover={{ scale: 1.03, y: -3 }}
                  onClick={() => onFileOpen(doc.id)}
                  className="p-3 rounded-xl bg-white/30 dark:bg-white/5 border border-black/10 dark:border-white/10 cursor-pointer hover:bg-white/50 dark:hover:bg-white/10 transition-all group"
                >
                  <div className="text-3xl mb-2 text-center">{fileIcon(doc.type)}</div>
                  <p className="text-xs text-center truncate text-[#1A1A1A] dark:text-white font-medium">
                    {doc.original_filename}
                  </p>
                  <p className="text-xs text-center text-[#2a2a2a]/40 dark:text-white/40 mt-0.5 uppercase">
                    {doc.type}
                  </p>
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}
