import React, { useState } from 'react'

interface AnalysisResult {
  highlighted_text: {
    content: string
    highlights: Array<{
      start: number
      end: number
      confidence: number
      reason: string
    }>
  }
}

interface HighlightedDocumentProps {
  analysis: AnalysisResult
}

const HighlightedDocument: React.FC<HighlightedDocumentProps> = ({ analysis }) => {
  const [hoveredHighlight, setHoveredHighlight] = useState<number | null>(null)
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 })

  const { content, highlights } = analysis.highlighted_text

  const getHighlightColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-red-200 border-b-2 border-red-500'
    if (confidence >= 0.6) return 'bg-yellow-200 border-b-2 border-yellow-500'
    return 'bg-green-200 border-b-2 border-green-500'
  }

  const handleMouseEnter = (index: number, event: React.MouseEvent) => {
    setHoveredHighlight(index)
    setTooltipPosition({ x: event.clientX, y: event.clientY })
  }

  const handleMouseLeave = () => {
    setHoveredHighlight(null)
  }

  const renderHighlightedText = () => {
    if (!highlights || highlights.length === 0) {
      return <span>{content}</span>
    }

    const sortedHighlights = [...highlights].sort((a, b) => a.start - b.start)
    const elements: React.ReactNode[] = []
    let lastIndex = 0

    sortedHighlights.forEach((highlight, index) => {
      if (highlight.start > lastIndex) {
        elements.push(
          <span key={`text-${lastIndex}`}>
            {content.slice(lastIndex, highlight.start)}
          </span>
        )
      }

      elements.push(
        <span
          key={`highlight-${index}`}
          className={`cursor-pointer transition-all duration-200 ${getHighlightColor(highlight.confidence)}`}
          onMouseEnter={(e) => handleMouseEnter(index, e)}
          onMouseLeave={handleMouseLeave}
        >
          {content.slice(highlight.start, highlight.end)}
        </span>
      )

      lastIndex = highlight.end
    })

    if (lastIndex < content.length) {
      elements.push(
        <span key={`text-${lastIndex}`}>
          {content.slice(lastIndex)}
        </span>
      )
    }

    return elements
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        Document Analysis
      </h2>

      <div className="mb-4">
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-200 border-b-2 border-red-500 rounded"></div>
            <span>High Risk</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-yellow-200 border-b-2 border-yellow-500 rounded"></div>
            <span>Medium Risk</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-200 border-b-2 border-green-500 rounded"></div>
            <span>Low Risk</span>
          </div>
        </div>
      </div>

      <div className="relative">
        <div className="bg-gray-50 p-6 rounded-lg border max-h-96 overflow-y-auto">
          <div className="text-gray-800 leading-relaxed whitespace-pre-wrap font-mono text-sm">
            {renderHighlightedText()}
          </div>
        </div>

        {hoveredHighlight !== null && (
          <div
            className="fixed z-50 bg-gray-900 text-white p-3 rounded-lg shadow-lg max-w-xs"
            style={{
              left: tooltipPosition.x + 10,
              top: tooltipPosition.y - 10,
              pointerEvents: 'none'
            }}
          >
            <div className="text-sm">
              <div className="font-semibold mb-1">
                Confidence: {Math.round(highlights[hoveredHighlight].confidence * 100)}%
              </div>
              <div>{highlights[hoveredHighlight].reason}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default HighlightedDocument