import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

interface ContentUnderstander Props {
  documentId: string
}

interface DocumentSpan {
  id: string
  span_type: string
  text: string
  page: number | null
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

export function ContentUnderstander({ documentId }: ContentUnderstander Props) {
  const [spans, setSpans] = useState<DocumentSpan[]>([])
  const [context, setContext] = useState<DocumentContext | null>(null)
  const [isLoadingSpans, setIsLoadingSpans] = useState(true)
  const [isLoadingContext, setIsLoadingContext] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'content' | 'context'>('content')

  useEffect(() => {
    const fetchSpans = async () => {
      try {
        setIsLoadingSpans(true)
        const response = await fetch(`http://localhost:8002/api/v1/documents/${documentId}/spans`)

        if (!response.ok) {
          throw new Error('Failed to fetch document spans')
        }

        const data = await response.json()
        setSpans(data.spans || [])
        setIsLoadingSpans(false)
      } catch (err) {
        console.error('Error fetching spans:', err)
        setError(err instanceof Error ? err.message : 'Unknown error')
        setIsLoadingSpans(false)
      }
    }

    fetchSpans()
  }, [documentId])

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
      setActiveTab('context')
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
      className="w-96 flex flex-col bg-white/50 backdrop-blur-md border-l border-black/10 shadow-lg overflow-hidden"
    >
      {/* Header */}
      <div className="p-4 border-b border-black/10 bg-white/30">
        <h3 className="text-lg font-semibold text-[#1A1A1A]">Content Understander</h3>
        <p className="text-xs text-[#2a2a2a]/60 mt-1">AI-powered document analysis</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-black/10 bg-white/20">
        <button
          onClick={() => setActiveTab('content')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'content'
              ? 'text-[#6f8f88] border-b-2 border-[#6f8f88] bg-white/40'
              : 'text-[#2a2a2a]/60 hover:text-[#2a2a2a] hover:bg-white/20'
          }`}
        >
          Extracted Content
        </button>
        <button
          onClick={() => setActiveTab('context')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors relative ${
            activeTab === 'context'
              ? 'text-[#6f8f88] border-b-2 border-[#6f8f88] bg-white/40'
              : 'text-[#2a2a2a]/60 hover:text-[#2a2a2a] hover:bg-white/20'
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
                <div className="animate-pulse text-[#2a2a2a]/60">Loading content...</div>
              </div>
            ) : spans.length === 0 ? (
              <div className="text-center py-12 text-[#2a2a2a]/60 text-sm">
                No content extracted
              </div>
            ) : (
              spans.map((span, index) => (
                <motion.div
                  key={span.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05, ...springConfig }}
                  className="p-3 bg-white/60 rounded-lg border border-black/5 hover:bg-white/80 transition-colors"
                >
                  <div className="flex items-start justify-between mb-1">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded ${
                      span.span_type === 'title' ? 'bg-purple-100 text-purple-700' :
                      span.span_type === 'heading' ? 'bg-blue-100 text-blue-700' :
                      span.span_type === 'table' ? 'bg-green-100 text-green-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {span.span_type}
                    </span>
                    {span.page && (
                      <span className="text-xs text-[#2a2a2a]/40">pg. {span.page}</span>
                    )}
                  </div>
                  <p className="text-sm text-[#1A1A1A] leading-relaxed whitespace-pre-wrap">
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
                <p className="text-sm text-[#2a2a2a]/60 mb-4">
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
                  <p className="text-xs text-red-600 mt-2">{error}</p>
                )}
              </div>
            )}

            {isLoadingContext && (
              <div className="flex flex-col items-center justify-center py-12 space-y-3">
                <div className="w-8 h-8 border-3 border-[#6f8f88] border-t-transparent rounded-full animate-spin"></div>
                <p className="text-sm text-[#2a2a2a]/60">Analyzing with AI...</p>
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
                  <h4 className="text-sm font-semibold text-[#1A1A1A] mb-3">Page Narratives</h4>
                  <div className="space-y-3">
                    {context.page_narratives.map((narrative, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1, ...springConfig }}
                        className="p-3 bg-gradient-to-br from-blue-50 to-white rounded-lg border border-blue-100"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-semibold text-blue-700">
                            Page {narrative.page_number}
                          </span>
                          <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-600 rounded">
                            {narrative.page_type}
                          </span>
                        </div>
                        <p className="text-xs font-medium text-[#1A1A1A] mb-1">
                          {narrative.key_takeaway}
                        </p>
                        <p className="text-xs text-[#2a2a2a]/70 leading-relaxed">
                          {narrative.narrative_summary}
                        </p>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Primary Actors */}
                {context.context_entities.primary_actors.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-[#1A1A1A] mb-2">Primary Actors</h4>
                    <div className="flex flex-wrap gap-2">
                      {context.context_entities.primary_actors.map((actor, index) => (
                        <motion.span
                          key={index}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: index * 0.05 }}
                          className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium"
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
                    <h4 className="text-sm font-semibold text-[#1A1A1A] mb-2">Critical Dates</h4>
                    <div className="space-y-2">
                      {context.context_entities.critical_dates.map((date, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="p-2 bg-amber-50 rounded border border-amber-200"
                        >
                          <p className="text-xs font-medium text-amber-900">
                            {date.source_text}
                          </p>
                          <p className="text-xs text-amber-700">{date.description}</p>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Financial Values */}
                {context.context_entities.financial_values.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-[#1A1A1A] mb-2">Financial Values</h4>
                    <div className="space-y-2">
                      {context.context_entities.financial_values.map((value, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="p-2 bg-green-50 rounded border border-green-200"
                        >
                          <p className="text-xs font-bold text-green-900">
                            ${value.amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </p>
                          <p className="text-xs text-green-700">{value.description}</p>
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
                  className="w-full px-4 py-2 bg-white/60 border border-black/10 rounded-lg hover:bg-white/80 transition-colors text-sm font-medium text-[#2a2a2a] disabled:opacity-50"
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
}
