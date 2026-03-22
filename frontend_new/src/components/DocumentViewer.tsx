import { motion } from 'framer-motion'
import { useState, useEffect, useRef, useCallback, useMemo, memo } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'

// Configure PDF.js worker - use version from installed package
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url
).toString()

interface DocumentViewerProps {
  documentId: string
  onClose?: () => void
  activeSpanId?: string | null
  activeSpan?: any
}

interface DocumentMetadata {
  filename: string
  type: string
  created_at: string
}

// Memoized component to prevent unnecessary re-renders
export const DocumentViewer = memo(function DocumentViewer({ documentId, onClose, activeSpanId, activeSpan }: DocumentViewerProps) {
  const [metadata, setMetadata] = useState<DocumentMetadata | null>(null)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [numPages, setNumPages] = useState<number>(0)
  const [scale, setScale] = useState<number>(1.0)
  const [isLoading, setIsLoading] = useState(true)
  const [pdfLoaded, setPdfLoaded] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const pdfContainerRef = useRef<HTMLDivElement>(null)
  const hasLoadedRef = useRef(false)

  // Scroll to span when hovered (for continuous scroll view)
  useEffect(() => {
    if (activeSpan && activeSpan.page && pdfContainerRef.current) {
      const pageElement = pdfContainerRef.current.querySelector(`[data-page-number="${activeSpan.page}"]`)
      if (pageElement) {
        pageElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }
  }, [activeSpan])

  // Fetch document data - runs once on mount
  useEffect(() => {
    let isMounted = true

    const fetchDocument = async () => {
      try {
        setIsLoading(true)
        hasLoadedRef.current = false
        setPdfLoaded(false)

        const metadataResponse = await fetch(`http://localhost:8002/api/v1/convert/${documentId}`)
        if (!metadataResponse.ok) {
          throw new Error('Failed to fetch document metadata')
        }
        const metadataData = await metadataResponse.json()

        if (!isMounted) return

        setMetadata(metadataData.metadata)
        setPdfUrl(`http://localhost:8002/api/v1/pdf/${documentId}`)
        setIsLoading(false)
      } catch (err) {
        if (!isMounted) return
        setError(err instanceof Error ? err.message : 'Unknown error')
        setIsLoading(false)
      }
    }

    fetchDocument()

    return () => { isMounted = false }
  }, []) // Empty deps - only run on mount

  // Memoize callbacks to prevent unnecessary re-renders
  const onDocumentLoadSuccess = useCallback(({ numPages }: { numPages: number }) => {
    if (!hasLoadedRef.current) {
      hasLoadedRef.current = true
      setNumPages(numPages)
      setPdfLoaded(true)
    }
  }, [])

  const onDocumentLoadError = useCallback((error: Error) => {
    console.error('PDF load error:', error)
    setError(`Failed to load PDF: ${error.message}`)
  }, [])

  const springConfig = {
    type: "spring" as const,
    stiffness: 100,
    damping: 20
  }

  if (isLoading) {
    return (
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={springConfig}
        className="flex-1 flex items-center justify-center p-8"
      >
        {/* Skeleton Page Loader */}
        <div className="w-full max-w-[850px] bg-white dark:bg-gray-800 rounded-sm shadow-2xl overflow-hidden">
          <div className="p-16 space-y-4 animate-pulse">
            {/* Skeleton heading */}
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>

            <div className="pt-8 space-y-3">
              {/* Skeleton paragraphs */}
              {[...Array(8)].map((_, i) => (
                <div key={i} className="space-y-2">
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-11/12"></div>
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-10/12"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    )
  }

  if (error) {
    return (
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={springConfig}
        className="flex-1 flex items-center justify-center p-8"
      >
        <div className="text-center">
          <p className="text-red-600 text-lg mb-4">{error}</p>
          {onClose && (
            <button
              onClick={onClose}
              className="px-6 py-2 bg-[#6f8f88] text-white rounded-lg hover:bg-[#5f7f78]"
            >
              Go Back
            </button>
          )}
        </div>
      </motion.div>
    )
  }

  if (!metadata || !pdfUrl) {
    return null
  }

  return (
    <motion.div
      ref={pdfContainerRef}
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={springConfig}
      className="flex-1 overflow-y-auto p-8"
    >
      {/* Header with filename and controls */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, ...springConfig }}
        className="max-w-[850px] mx-auto mb-6"
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-semibold text-[#1A1A1A] dark:text-white">
              {metadata.filename}
            </h2>
            <p className="text-sm text-[#2a2a2a]/60 dark:text-white/60 mt-1">
              {new Date(metadata.created_at).toLocaleDateString()} · {metadata.type.toUpperCase()} · {numPages} {numPages === 1 ? 'page' : 'pages'}
            </p>
          </div>
          {onClose && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onClose}
              className="px-4 py-2 bg-white/50 dark:bg-white/10 border border-black/10 dark:border-white/10 rounded-lg hover:bg-white/80 dark:hover:bg-white/20 transition-colors dark:text-white"
            >
              ✕ Close
            </motion.button>
          )}
        </div>

        {/* Toolbar with zoom and page controls */}
        <div className="flex items-center gap-4 p-3 bg-white/50 dark:bg-white/10 backdrop-blur-sm border border-black/10 dark:border-white/10 rounded-lg">
          {/* Zoom controls */}
          <div className="flex items-center gap-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setScale(Math.max(0.5, scale - 0.1))}
              className="w-8 h-8 flex items-center justify-center rounded-md bg-white dark:bg-white/10 border border-black/10 dark:border-white/10 hover:bg-black/5 dark:hover:bg-white/20 transition-colors dark:text-white"
              title="Zoom Out"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
              </svg>
            </motion.button>
            <span className="text-sm font-medium min-w-[50px] text-center dark:text-white">{Math.round(scale * 100)}%</span>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setScale(Math.min(2.0, scale + 0.1))}
              className="w-8 h-8 flex items-center justify-center rounded-md bg-white dark:bg-white/10 border border-black/10 dark:border-white/10 hover:bg-black/5 dark:hover:bg-white/20 transition-colors dark:text-white"
              title="Zoom In"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </motion.button>
          </div>

          <div className="w-px h-6 bg-black/10 dark:bg-white/10"></div>

          {/* Page count indicator */}
          <span className="text-sm font-medium text-[#2a2a2a]/70 dark:text-white/70">
            {numPages} {numPages === 1 ? 'page' : 'pages'}
          </span>

          <div className="w-px h-6 bg-black/10 dark:bg-white/10"></div>

          {/* Download button */}
          <motion.a
            href={pdfUrl || ''}
            download={metadata.filename}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2 px-3 py-1.5 bg-white dark:bg-white/10 border border-black/10 dark:border-white/10 rounded-md hover:bg-black/5 dark:hover:bg-white/20 transition-colors text-sm font-medium dark:text-white"
            title="Download PDF"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download
          </motion.a>
        </div>
      </motion.div>

      {/* PDF Viewer Container - Scrollable multi-page view */}
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3, stiffness: 100, damping: 20, type: "spring" }}
        className="mx-auto"
      >
        {/* Live PDF rendered by react-pdf */}
        <Document
          file={pdfUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={onDocumentLoadError}
          loading={
            <div className="flex items-center justify-center w-full" style={{ minHeight: '600px' }}>
              <div className="animate-pulse text-gray-400 dark:text-gray-500 text-lg">Loading PDF...</div>
            </div>
          }
          error={
            <div className="flex items-center justify-center w-full" style={{ minHeight: '600px' }}>
              <div className="text-red-600 dark:text-red-400 text-lg">Failed to load PDF</div>
            </div>
          }
        >
          {/* Render all pages stacked vertically for scrolling */}
          {pdfLoaded && (
            <div className="flex flex-col gap-4">
              {Array.from({ length: numPages }, (_, index) => (
                <div
                  key={index + 1}
                  className="bg-white shadow-2xl"
                  data-page-number={index + 1}
                >
                  <Page
                    pageNumber={index + 1}
                    width={850 * scale}
                    renderTextLayer={false}
                    renderAnnotationLayer={false}
                  />
                </div>
              ))}
            </div>
          )}
        </Document>
      </motion.div>

      {/* Bottom spacing */}
      <div className="h-8"></div>
    </motion.div>
  )
})
