/**
 * HighlightedDocumentViewer Component
 * Displays document with color-coded highlighting and hover explanations
 * Replicates the visual style from the provided image
 */

import React, { useState, useRef, useEffect } from 'react';
import { Tooltip } from 'react-tooltip';
import { Info, Shield, AlertTriangle, X } from 'lucide-react';
import { HighlightedDocument, WordExplanation } from '../services/api';

interface HighlightedDocumentViewerProps {
  highlightedDocument: HighlightedDocument;
  title?: string;
  className?: string;
}

interface TooltipData {
  word: string;
  explanation: WordExplanation;
  position: { x: number; y: number };
}

const HighlightedDocumentViewer: React.FC<HighlightedDocumentViewerProps> = ({
  highlightedDocument,
  title = "Using ML to figure out the Context of Text",
  className = "",
}) => {
  const [activeTooltip, setActiveTooltip] = useState<TooltipData | null>(null);
  const [showLegend, setShowLegend] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  const getHighlightClass = (colorEmoji: string): string => {
    switch (colorEmoji) {
      case '🟩':
        return 'bg-green-200 hover:bg-green-300 text-green-900 border-green-300';
      case '🟨':
        return 'bg-yellow-200 hover:bg-yellow-300 text-yellow-900 border-yellow-300';
      case '🟥':
        return 'bg-red-200 hover:bg-red-300 text-red-900 border-red-300';
      default:
        return 'bg-gray-100 hover:bg-gray-200 text-gray-900 border-gray-300';
    }
  };

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 0.8) {
      return <Shield className="w-3 h-3 text-green-600" />;
    } else if (confidence >= 0.4) {
      return <Info className="w-3 h-3 text-yellow-600" />;
    } else {
      return <AlertTriangle className="w-3 h-3 text-red-600" />;
    }
  };

  const handleWordClick = (
    event: React.MouseEvent,
    word: string,
    wordIndex: number
  ) => {
    const wordKey = `word_${wordIndex}`;
    const explanation = highlightedDocument.word_explanations[wordKey];

    if (explanation) {
      const rect = event.currentTarget.getBoundingClientRect();
      setActiveTooltip({
        word,
        explanation,
        position: {
          x: rect.left + rect.width / 2,
          y: rect.top - 10,
        },
      });
    }
  };

  const closeTooltip = () => {
    setActiveTooltip(null);
  };

  // Close tooltip when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        closeTooltip();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div ref={containerRef} className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="border-b border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 text-center">{title}</h2>

        {/* Legend */}
        {showLegend && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-700">Color Legend</h3>
              <button
                onClick={() => setShowLegend(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-green-200 border border-green-300 rounded"></div>
                <span className="text-gray-700">Authentic</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-yellow-200 border border-yellow-300 rounded"></div>
                <span className="text-gray-700">Needs Review</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-red-200 border border-red-300 rounded"></div>
                <span className="text-gray-700">Suspicious</span>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Click on any highlighted word for detailed explanation
            </p>
          </div>
        )}
      </div>

      {/* Document Content */}
      <div className="p-6">
        <div className="prose prose-lg max-w-none">
          <div className="text-gray-800 leading-relaxed text-justify">
            {highlightedDocument.highlighted_words.map(([word, colorEmoji], index) => {
              const isSpace = word.trim() === '';

              if (isSpace) {
                return <span key={index}> </span>;
              }

              const wordKey = `word_${index}`;
              const explanation = highlightedDocument.word_explanations[wordKey];
              const isHighlighted = colorEmoji !== '';

              return (
                <React.Fragment key={index}>
                  {isHighlighted ? (
                    <span
                      className={`
                        inline-block px-1 py-0.5 mx-0.5 rounded border cursor-pointer
                        transition-all duration-200 ease-in-out
                        ${getHighlightClass(colorEmoji)}
                        hover:scale-105 hover:shadow-sm
                      `}
                      onClick={(e) => handleWordClick(e, word, index)}
                      title={explanation?.explanation || `Click for details about "${word}"`}
                    >
                      {word}
                    </span>
                  ) : (
                    <span className="text-gray-800">{word}</span>
                  )}
                  {/* Add space after word if needed */}
                  {index < highlightedDocument.highlighted_words.length - 1 &&
                   !highlightedDocument.highlighted_words[index + 1][0].startsWith(' ') && (
                    <span> </span>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Statistics */}
        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {highlightedDocument.highlighted_words.filter(([_, color]) => color === '🟩').length}
              </div>
              <div className="text-sm text-green-700">Authentic Words</div>
            </div>
            <div className="p-3 bg-yellow-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {highlightedDocument.highlighted_words.filter(([_, color]) => color === '🟨').length}
              </div>
              <div className="text-sm text-yellow-700">Review Needed</div>
            </div>
            <div className="p-3 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {highlightedDocument.highlighted_words.filter(([_, color]) => color === '🟥').length}
              </div>
              <div className="text-sm text-red-700">Suspicious Words</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tooltip Modal */}
      {activeTooltip && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-25">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 transform transition-all">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getConfidenceIcon(activeTooltip.explanation.confidence)}
                  <h3 className="text-lg font-semibold text-gray-900">
                    Analysis: "{activeTooltip.word}"
                  </h3>
                </div>
                <button
                  onClick={closeTooltip}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="p-4 space-y-4">
              {/* Confidence Score */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700">Confidence</span>
                  <span className="text-sm font-bold text-gray-900">
                    {(activeTooltip.explanation.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${
                      activeTooltip.explanation.confidence >= 0.8
                        ? 'bg-green-500'
                        : activeTooltip.explanation.confidence >= 0.4
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${activeTooltip.explanation.confidence * 100}%` }}
                  ></div>
                </div>
              </div>

              {/* Explanation */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Explanation</h4>
                <p className="text-sm text-gray-600 leading-relaxed">
                  {activeTooltip.explanation.explanation}
                </p>
              </div>

              {/* Contributing Layers */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">
                  Contributing Analysis Layers
                </h4>
                <div className="flex flex-wrap gap-2">
                  {activeTooltip.explanation.contributing_layers.map((layer, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                    >
                      {layer.replace('_', ' ').toUpperCase()}
                    </span>
                  ))}
                </div>
              </div>

              {/* Color Classification */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Classification</h4>
                <div className="flex items-center space-x-2">
                  <div
                    className={`w-4 h-4 rounded border ${
                      activeTooltip.explanation.highlight_color === 'green'
                        ? 'bg-green-200 border-green-300'
                        : activeTooltip.explanation.highlight_color === 'yellow'
                        ? 'bg-yellow-200 border-yellow-300'
                        : 'bg-red-200 border-red-300'
                    }`}
                  ></div>
                  <span className="text-sm text-gray-600 capitalize">
                    {activeTooltip.explanation.highlight_color === 'green'
                      ? 'Authentic'
                      : activeTooltip.explanation.highlight_color === 'yellow'
                      ? 'Needs Review'
                      : 'Suspicious'}
                  </span>
                </div>
              </div>
            </div>

            <div className="p-4 bg-gray-50 rounded-b-lg">
              <button
                onClick={closeTooltip}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Show Legend Button */}
      {!showLegend && (
        <div className="absolute top-4 right-4">
          <button
            onClick={() => setShowLegend(true)}
            className="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-600 text-sm rounded-md border"
          >
            Show Legend
          </button>
        </div>
      )}
    </div>
  );
};

export default HighlightedDocumentViewer;