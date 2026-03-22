import { motion } from 'framer-motion'
import { useState, useEffect, memo, useRef } from 'react'

interface ContentUnderstanderProps {
  documentId: string
  onSpanHover?: (spanId: string | null, span?: DocumentSpan) => void
}

interface DocumentSpan {
  id: string
  span_type: string
  text: string
  page: number | null
  bbox: any
}

interface ContextEntity {
  primary_actors: string[]
  critical_dates: Array<{
    date: string
    source_text: string
    description: string
  }>
  financial_values: Array<{
    amount: number
    source_text: string
    description: string
  }>
}

interface PageNarrative {
  page_number: number
  page_type: string
  narrative_summary: string
  key_takeaway: string
  supporting_chunks: string[]
}

interface DocumentContext {
  document_id: string
  page_narratives: PageNarrative[]
  context_entities: ContextEntity
}

export const ContentUnderstander = memo(function ContentUnderstander({ documentId, onSpanHover }: ContentUnderstanderProps) {
  const [spans, setSpans] = useState<DocumentSpan[]>([])
  const [context, setContext] = useState<DocumentContext | null>(null)
  const [isLoadingSpans, setIsLoadingSpans] = useState(true)
  const [isLoadingContext, setIsLoadingContext] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'content' | 'context'>('content')
  const [activeSpanId, setActiveSpanId] = useState<string | null>(null)

  const handleSpanHover = (spanId: string | null, span?: DocumentSpan) => {
    setActiveSpanId(spanId)
    if (onSpanHover) {
      onSpanHover(spanId, span)
    }
  }

  // Fetch spans - runs once on mount
  useEffect(() => {
    let isMounted = true

    const fetchSpans = async () => {
      try {
        setIsLoadingSpans(true)

        const response = await fetch(`http://localhost:8002/api/v1/documents/${documentId}/spans`)

        if (!response.ok) {
          throw new Error('Failed to fetch document spans')
        }

        const data = await response.json()

        if (!isMounted) return

        setSpans(data.spans || [])
        setIsLoadingSpans(false)
      } catch (err) {
        if (!isMounted) return
        console.error('Error fetching spans:', err)
        setError(err instanceof Error ? err.message : 'Unknown error')
        setIsLoadingSpans(false)
      }
    }

    fetchSpans()

    return () => { isMounted = false }
  }, []) // Empty deps - only run on mount

  const analyzeContext = async () => {
    try {
      setIsLoadingContext(true)
      setError(null)

      const response = await fetch(`http://localhost:8002/api/v1/documents/${documentId}/analyze-context`, {
        method: 'POST'
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to analyze context')
      }

      const data = await response.json()
      setContext(data)
      setIsLoadingContext(false)
    } catch (err) {
      console.error('Error analyzing context:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
      setIsLoadingContext(false)
    }
  }

  const springConfig = {
    type: "spring" as const,
    stiffness: 100,
    damping: 20
  }

  return (
    <motion.div
      initial={{ x: 100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={springConfig}
      className="w-96 flex flex-col bg-white/50 dark:bg-[#252525]/90 backdrop-blur-md border-l border-black/10 dark:border-white/10 shadow-lg overflow-hidden"
    >
      {/* Header */}
      <div className="p-4 border-b border-black/10 dark:border-white/10 bg-white/30 dark:bg-white/5">
        <h3 className="text-lg font-semibold text-[#1A1A1A] dark:text-white">Content Understander</h3>
        <p className="text-xs text-[#2a2a2a]/60 dark:text-white/60 mt-1">AI-powered document analysis</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-black/10 dark:border-white/10 bg-white/20 dark:bg-white/5">
        <button
          onClick={() => setActiveTab('content')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'content'
              ? 'text-[#6f8f88] border-b-2 border-[#6f8f88] bg-white/40 dark:bg-white/10'
              : 'text-[#2a2a2a]/60 dark:text-white/60 hover:text-[#2a2a2a] dark:hover:text-white hover:bg-white/20 dark:hover:bg-white/10'
          }`}
        >
          Extracted Content
        </button>
        <button
          onClick={() => setActiveTab('context')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors relative ${
            activeTab === 'context'
              ? 'text-[#6f8f88] border-b-2 border-[#6f8f88] bg-white/40 dark:bg-white/10'
              : 'text-[#2a2a2a]/60 dark:text-white/60 hover:text-[#2a2a2a] dark:hover:text-white hover:bg-white/20 dark:hover:bg-white/10'
          }`}
        >
          AI Analysis
          {context && (
            <span className="absolute top-2 right-2 w-2 h-2 bg-green-500 rounded-full"></span>
          )}
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'content' && (
          <div className="p-4 space-y-3">
            {isLoadingSpans ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-pulse text-[#2a2a2a]/60 dark:text-white/60">Loading content...</div>
              </div>
            ) : spans.length === 0 ? (
              <div className="text-center py-12 text-[#2a2a2a]/60 dark:text-white/60 text-sm">
                No content extracted
              </div>
            ) : (
              spans.map((span, index) => (
                <motion.div
                  key={span.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05, ...springConfig }}
                  onMouseEnter={() => handleSpanHover(span.id, span)}
                  onMouseLeave={() => handleSpanHover(null)}
                  className={`
                    group relative p-4 rounded-xl border transition-all duration-300 cursor-pointer
                    ${activeSpanId === span.id
                      ? 'bg-white dark:bg-white/10 border-blue-500 shadow-lg translate-x-[-4px]'
                      : 'bg-white/60 dark:bg-white/5 border-gray-200 dark:border-white/10 hover:border-blue-300 dark:hover:border-blue-500/50 hover:shadow-md'
                    }
                  `}
                >
                  {/* Connector Dot (Visual Anchor) */}
                  <div className={`
                    absolute left-[-6px] top-1/2 -translate-y-1/2 w-3 h-3 rounded-full border-2 border-white transition-all duration-300
                    ${activeSpanId === span.id ? 'bg-blue-500 scale-100 opacity-100' : 'bg-transparent scale-0 opacity-0'}
                  `} />

                  <div className="flex items-start justify-between mb-2">
                    <span className={`
                      text-[10px] uppercase tracking-wider font-bold px-2 py-1 rounded-full transition-colors
                      ${activeSpanId === span.id
                        ? span.span_type === 'title' ? 'bg-purple-100 text-purple-700' :
                          span.span_type === 'heading' ? 'bg-blue-100 text-blue-700' :
                          span.span_type === 'table' ? 'bg-green-100 text-green-700' :
                          'bg-blue-100 text-blue-700'
                        : span.span_type === 'title' ? 'bg-purple-100/50 text-purple-600' :
                          span.span_type === 'heading' ? 'bg-blue-100/50 text-blue-600' :
                          span.span_type === 'table' ? 'bg-green-100/50 text-green-600' :
                          'bg-gray-100 text-gray-500 group-hover:bg-blue-50 group-hover:text-blue-600'
                      }
                    `}>
                      {span.span_type}
                    </span>
                    {span.page && (
                      <span className="text-xs text-[#2a2a2a]/40 dark:text-white/40">pg. {span.page}</span>
                    )}
                  </div>
                  <p className={`text-sm leading-relaxed whitespace-pre-wrap transition-colors ${
                    activeSpanId === span.id ? 'text-slate-800 dark:text-white font-medium' : 'text-slate-600 dark:text-white/80'
                  }`}>
                    {span.text}
                  </p>
                </motion.div>
              ))
            )}
          </div>
        )}

        {activeTab === 'context' && (
          <div className="p-4 space-y-4">
            {!context && !isLoadingContext && (
              <div className="text-center py-12 space-y-4">
                <p className="text-sm text-[#2a2a2a]/60 dark:text-white/60 mb-4">
                  Generate AI-powered context analysis
                </p>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={analyzeContext}
                  className="px-6 py-3 bg-[#6f8f88] text-white rounded-lg hover:bg-[#5f7f78] transition-colors font-medium"
                >
                  Analyze Document
                </motion.button>
                {error && (
                  <p className="text-xs text-red-600 dark:text-red-400 mt-2">{error}</p>
                )}
              </div>
            )}

            {isLoadingContext && (
              <div className="flex flex-col items-center justify-center py-12 space-y-3">
                <div className="w-8 h-8 border-3 border-[#6f8f88] border-t-transparent rounded-full animate-spin"></div>
                <p className="text-sm text-[#2a2a2a]/60 dark:text-white/60">Analyzing with AI...</p>
              </div>
            )}

            {context && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={springConfig}
                className="space-y-4"
              >
                {/* Page Narratives */}
                <div>
                  <h4 className="text-sm font-semibold text-[#1A1A1A] dark:text-white mb-3">Page Narratives</h4>
                  <div className="space-y-3">
                    {context.page_narratives.map((narrative, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1, ...springConfig }}
                        className="p-3 bg-gradient-to-br from-blue-50 to-white dark:from-blue-900/20 dark:to-white/5 rounded-lg border border-blue-100 dark:border-blue-500/30"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-semibold text-blue-700 dark:text-blue-400">
                            Page {narrative.page_number}
                          </span>
                          <span className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 rounded">
                            {narrative.page_type}
                          </span>
                        </div>
                        <p className="text-xs font-medium text-[#1A1A1A] dark:text-white mb-1">
                          {narrative.key_takeaway}
                        </p>
                        <p className="text-xs text-[#2a2a2a]/70 dark:text-white/70 leading-relaxed">
                          {narrative.narrative_summary}
                        </p>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Primary Actors */}
                {context.context_entities.primary_actors.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-[#1A1A1A] dark:text-white mb-2">Primary Actors</h4>
                    <div className="flex flex-wrap gap-2">
                      {context.context_entities.primary_actors.map((actor, index) => (
                        <motion.span
                          key={index}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: index * 0.05 }}
                          className="px-3 py-1 bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-300 rounded-full text-xs font-medium"
                        >
                          {actor}
                        </motion.span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Critical Dates */}
                {context.context_entities.critical_dates.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-[#1A1A1A] dark:text-white mb-2">Critical Dates</h4>
                    <div className="space-y-2">
                      {context.context_entities.critical_dates.map((date, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="p-2 bg-amber-50 dark:bg-amber-500/10 rounded border border-amber-200 dark:border-amber-500/30"
                        >
                          <p className="text-xs font-medium text-amber-900 dark:text-amber-300">
                            {date.source_text}
                          </p>
                          <p className="text-xs text-amber-700 dark:text-amber-400">{date.description}</p>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Financial Values */}
                {context.context_entities.financial_values.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-[#1A1A1A] dark:text-white mb-2">Financial Values</h4>
                    <div className="space-y-2">
                      {context.context_entities.financial_values.map((value, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="p-2 bg-green-50 dark:bg-green-500/10 rounded border border-green-200 dark:border-green-500/30"
                        >
                          <p className="text-xs font-bold text-green-900 dark:text-green-300">
                            ${value.amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </p>
                          <p className="text-xs text-green-700 dark:text-green-400">{value.description}</p>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Refresh Analysis Button */}
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={analyzeContext}
                  disabled={isLoadingContext}
                  className="w-full px-4 py-2 bg-white/60 dark:bg-white/10 border border-black/10 dark:border-white/10 rounded-lg hover:bg-white/80 dark:hover:bg-white/20 transition-colors text-sm font-medium text-[#2a2a2a] dark:text-white disabled:opacity-50"
                >
                  Refresh Analysis
                </motion.button>
              </motion.div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  )
})
