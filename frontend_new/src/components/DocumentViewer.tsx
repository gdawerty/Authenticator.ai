import { motion } from 'framer-motion'
import { useState, useEffect, useRef } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'

// Configure PDF.js worker from node_modules
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

export function DocumentViewer({ documentId, onClose, activeSpanId, activeSpan }: DocumentViewerProps) {
  const [metadata, setMetadata] = useState<DocumentMetadata | null>(null)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [numPages, setNumPages] = useState<number>(0)
  const [currentPage, setCurrentPage] = useState<number>(1)
  const [scale, setScale] = useState<number>(1.0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const pdfContainerRef = useRef<HTMLDivElement>(null)

  // Scroll to span when hovered
  useEffect(() => {
    if (activeSpan && activeSpan.page && pdfContainerRef.current) {
      // Smooth scroll to the page containing the span
      const targetPage = activeSpan.page
      if (targetPage === currentPage) {
        // Already on the right page, just scroll within view
        pdfContainerRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' })
      } else {
        // Navigate to the correct page
        setCurrentPage(targetPage)
      }
    }
  }, [activeSpan, currentPage])

  useEffect(() => {
    const fetchDocument = async () => {
      try {
        setIsLoading(true)

        // Fetch metadata
        const metadataResponse = await fetch(`http://localhost:8002/api/v1/convert/${documentId}`)
        if (!metadataResponse.ok) {
          throw new Error('Failed to fetch document metadata')
        }
        const metadataData = await metadataResponse.json()
        setMetadata(metadataData.metadata)

        // Fetch the original PDF file
        const pdfUrl = `http://localhost:8002/api/v1/pdf/${documentId}`
        setPdfUrl(pdfUrl)

        setIsLoading(false)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
        setIsLoading(false)
      }
    }

    fetchDocument()
  }, [documentId])

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages)
  }

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
        <div className="w-full max-w-[850px] bg-white rounded-sm shadow-2xl overflow-hidden">
          <div className="p-16 space-y-4 animate-pulse">
            {/* Skeleton heading */}
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>

            <div className="pt-8 space-y-3">
              {/* Skeleton paragraphs */}
              {[...Array(8)].map((_, i) => (
                <div key={i} className="space-y-2">
                  <div className="h-3 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded w-11/12"></div>
                  <div className="h-3 bg-gray-200 rounded w-10/12"></div>
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
            <h2 className="text-2xl font-semibold text-[#1A1A1A]">
              {metadata.filename}
            </h2>
            <p className="text-sm text-[#2a2a2a]/60 mt-1">
              {new Date(metadata.created_at).toLocaleDateString()} · {metadata.type.toUpperCase()} · {numPages} {numPages === 1 ? 'page' : 'pages'}
            </p>
          </div>
          {onClose && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onClose}
              className="px-4 py-2 bg-white/50 border border-black/10 rounded-lg hover:bg-white/80 transition-colors"
            >
              ✕ Close
            </motion.button>
          )}
        </div>

        {/* Toolbar with zoom and page controls */}
        <div className="flex items-center gap-4 p-3 bg-white/50 backdrop-blur-sm border border-black/10 rounded-lg">
          {/* Zoom controls */}
          <div className="flex items-center gap-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setScale(Math.max(0.5, scale - 0.1))}
              className="w-8 h-8 flex items-center justify-center rounded-md bg-white border border-black/10 hover:bg-black/5 transition-colors"
              title="Zoom Out"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
              </svg>
            </motion.button>
            <span className="text-sm font-medium min-w-[50px] text-center">{Math.round(scale * 100)}%</span>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setScale(Math.min(2.0, scale + 0.1))}
              className="w-8 h-8 flex items-center justify-center rounded-md bg-white border border-black/10 hover:bg-black/5 transition-colors"
              title="Zoom In"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </motion.button>
          </div>

          <div className="w-px h-6 bg-black/10"></div>

          {/* Page navigation */}
          <div className="flex items-center gap-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage <= 1}
              className="w-8 h-8 flex items-center justify-center rounded-md bg-white border border-black/10 hover:bg-black/5 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              title="Previous Page"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </motion.button>
            <span className="text-sm font-medium min-w-[80px] text-center">
              Page {currentPage} of {numPages}
            </span>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setCurrentPage(Math.min(numPages, currentPage + 1))}
              disabled={currentPage >= numPages}
              className="w-8 h-8 flex items-center justify-center rounded-md bg-white border border-black/10 hover:bg-black/5 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              title="Next Page"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </motion.button>
          </div>

          <div className="w-px h-6 bg-black/10"></div>

          {/* Download button */}
          <motion.a
            href={pdfUrl || ''}
            download={metadata.filename}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2 px-3 py-1.5 bg-white border border-black/10 rounded-md hover:bg-black/5 transition-colors text-sm font-medium"
            title="Download PDF"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download
          </motion.a>
        </div>
      </motion.div>

      {/* PDF Viewer Container */}
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3, stiffness: 100, damping: 20, type: "spring" }}
        className="mx-auto bg-white shadow-2xl"
      >
        {/* Live PDF rendered by react-pdf */}
        <Document
          file={pdfUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={(error) => {
            console.error('PDF load error:', error)
            setError(`Failed to load PDF: ${error.message}`)
          }}
          loading={
            <div className="flex items-center justify-center w-full" style={{ minHeight: '600px' }}>
              <div className="animate-pulse text-gray-400 text-lg">Loading PDF...</div>
            </div>
          }
          error={
            <div className="flex items-center justify-center w-full" style={{ minHeight: '600px' }}>
              <div className="text-red-600 text-lg">Failed to load PDF</div>
            </div>
          }
        >
          {numPages > 0 && (
            <Page
              pageNumber={currentPage}
              width={850 * scale}
              renderTextLayer={false}
              renderAnnotationLayer={false}
            />
          )}
        </Document>
      </motion.div>

      {/* Bottom spacing */}
      <div className="h-8"></div>
    </motion.div>
  )
}
