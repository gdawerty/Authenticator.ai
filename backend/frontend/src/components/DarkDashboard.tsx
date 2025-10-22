import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

interface AnalysisResult {
  final_score: number
  color_label: string
  layer_scores: {
    mime: number
    classification: number
    clone_detection: number
    cryptographic: number
    rag: number | null
    ai_detection: number
    final_prediction: number
  }
  highlighted_text: {
    content: string
    highlights: Array<{
      start: number
      end: number
      confidence: number
      reason: string
    }>
  }
  layer_explanations: {
    mime: string
    classification: string
    clone_detection: string
    cryptographic: string
    rag: string
    ai_detection: string
    final_prediction: string
  }
}

const DarkDashboard: React.FC = () => {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<string>('')

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    setUploadedFile(file.name)
    setIsAnalyzing(true)

    setTimeout(() => {
      const mockResult: AnalysisResult = {
        final_score: 0.67,
        color_label: "MEDIUM RISK",
        layer_scores: {
          mime: 0.95,
          classification: 0.36,
          clone_detection: 0.66,
          cryptographic: 0.75,
          rag: 0.60,
          ai_detection: 0.75,
          final_prediction: 0.67
        },
        highlighted_text: {
          content: "This document contains a final project proposal that demonstrates academic writing standards. However, certain sections exhibit patterns that may indicate AI-assisted generation or potential plagiarism concerns. The methodology section appears to follow template-like structures commonly found in automated content generation tools.",
          highlights: [
            {
              start: 85,
              end: 120,
              confidence: 0.85,
              reason: "High probability of AI-generated content based on linguistic patterns"
            },
            {
              start: 180,
              end: 220,
              confidence: 0.65,
              reason: "Potential similarity to existing academic sources - requires manual review"
            }
          ]
        },
        layer_explanations: {
          mime: "Document MIME type verified successfully - authentic DOCX format",
          classification: "Document classification shows inconsistent formatting patterns",
          clone_detection: "Partial content similarity detected with academic sources",
          cryptographic: "Limited cryptographic verification available for this document type",
          rag: "Content analysis against knowledge base shows moderate confidence",
          ai_detection: "Linguistic patterns suggest possible AI assistance in content generation",
          final_prediction: "Overall assessment indicates medium risk requiring human review"
        }
      }
      setAnalysisResult(mockResult)
      setIsAnalyzing(false)
    }, 2000)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    multiple: false
  })

  const layers = [
    { id: 'mime', name: 'MIME Detection', score: analysisResult?.layer_scores.mime, color: '#10B981' },
    { id: 'classification', name: 'Classification', score: analysisResult?.layer_scores.classification, color: '#EF4444' },
    { id: 'clone_detection', name: 'Clone Detection', score: analysisResult?.layer_scores.clone_detection, color: '#F59E0B' },
    { id: 'cryptographic', name: 'Cryptographic', score: analysisResult?.layer_scores.cryptographic, color: '#EF4444' },
    { id: 'rag', name: 'RAG Analysis', score: analysisResult?.layer_scores.rag, color: '#F59E0B' },
    { id: 'ai_detection', name: 'AI Detection', score: analysisResult?.layer_scores.ai_detection, color: '#F59E0B' },
    { id: 'final_prediction', name: 'Final Prediction', score: analysisResult?.layer_scores.final_prediction, color: '#F59E0B' }
  ]

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="flex h-screen">

        {/* Sidebar */}
        <div className="w-80 bg-gray-800 border-r border-gray-700 p-6">
          {/* Header */}
          <div className="flex items-center mb-8">
            <div className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center mr-3">
              <span className="text-white font-bold">🛡️</span>
            </div>
            <div>
              <div className="font-semibold text-lg">Authenticator.ai</div>
              <div className="text-sm text-gray-400">Content Verification</div>
            </div>
          </div>

          {/* New Analysis Button */}
          <div className="mb-8">
            <div
              {...getRootProps()}
              className="w-full bg-orange-500 hover:bg-orange-600 text-white py-3 px-6 rounded-lg text-center cursor-pointer transition-colors font-medium"
            >
              <input {...getInputProps()} />
              + New Analysis
            </div>
          </div>

          {/* Recent Analyses */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">
              Recent Analyses
            </h3>

            {analysisResult && (
              <div className="bg-gray-700 border border-gray-600 rounded-lg p-4 mb-3">
                <div className="font-medium text-white mb-1">New Analysis 3</div>
                <div className="text-xs text-gray-400">Just now • 0 messages</div>
              </div>
            )}

            <div className="bg-gray-750 rounded-lg p-4 mb-3">
              <div className="font-medium text-white mb-1">Document Analysis #1</div>
              <div className="text-xs text-gray-400 mb-1">Authenticity score: 0.87</div>
              <div className="text-xs text-gray-400">1h ago • 5 messages</div>
            </div>

            <div className="bg-gray-750 rounded-lg p-4">
              <div className="font-medium text-white mb-1">Contract Verification</div>
              <div className="text-xs text-gray-400 mb-1">High confidence detection</div>
              <div className="text-xs text-gray-400">2h ago • 3 messages</div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">

          {/* Header Bar */}
          <div className="bg-gray-800 border-b border-gray-700 px-8 py-4 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-white">
                {analysisResult ? 'New Analysis 3' : 'New Analysis'}
              </h2>
              <p className="text-sm text-gray-400">7-Layer Authenticity Pipeline</p>
            </div>
            {uploadedFile && (
              <div className="text-sm text-gray-400 bg-gray-700 px-3 py-1 rounded">
                📄 {uploadedFile}
              </div>
            )}
          </div>

          {/* Content Area */}
          <div className="flex-1 p-8 overflow-auto">

            {isAnalyzing && (
              <div className="bg-orange-500 rounded-lg p-6 mb-8 text-center">
                <div className="text-lg font-medium mb-2">
                  Uploaded: {uploadedFile}
                </div>
                <div className="text-sm opacity-90">
                  📄 {uploadedFile} (Processing...)
                </div>
              </div>
            )}

            {!analysisResult && !isAnalyzing && (
              <div className="text-center mt-24">
                <h1 className="text-4xl font-bold text-white mb-4">Welcome to Authenticator.ai</h1>
                <p className="text-xl text-gray-400 mb-8">Advanced Document Authentication System</p>
                <div
                  {...getRootProps()}
                  className={`border-2 border-dashed rounded-xl p-16 transition-colors ${
                    isDragActive ? 'border-orange-400 bg-gray-800' : 'border-gray-600 bg-gray-800'
                  }`}
                >
                  <input {...getInputProps()} />
                  <div className="text-center">
                    <div className="w-16 h-16 mx-auto mb-4 text-gray-400">
                      <svg className="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <p className="text-xl text-white mb-2">
                      {isDragActive ? 'Drop your document here' : 'Drag & drop a document to analyze'}
                    </p>
                    <p className="text-gray-400">Supports PDF, DOC, DOCX, and TXT files</p>
                  </div>
                </div>
              </div>
            )}

            {analysisResult && (
              <div className="space-y-8">

                {/* File Upload Confirmation */}
                <div className="bg-orange-500 rounded-lg p-6">
                  <div className="text-lg font-medium mb-2">
                    Uploaded: {uploadedFile}
                  </div>
                  <div className="text-sm opacity-90">
                    📄 {uploadedFile} (0.0MB)
                  </div>
                </div>

                {/* Analysis Complete Card */}
                <div className="bg-gray-800 rounded-xl p-8 border border-gray-700">
                  <div className="text-center mb-8">

                    {/* Circular Progress */}
                    <div className="w-32 h-32 mx-auto mb-6 relative">
                      <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 120 120">
                        <circle
                          cx="60"
                          cy="60"
                          r="50"
                          fill="none"
                          stroke="#374151"
                          strokeWidth="8"
                        />
                        <circle
                          cx="60"
                          cy="60"
                          r="50"
                          fill="none"
                          stroke="#ff6b35"
                          strokeWidth="8"
                          strokeDasharray={`${analysisResult.final_score * 314} 314`}
                          strokeLinecap="round"
                        />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-2xl font-bold text-white">
                          {Math.round(analysisResult.final_score * 100)}%
                        </span>
                      </div>
                    </div>

                    <div className="text-xl font-medium text-white mb-3">Analysis Complete</div>
                    <div className="bg-yellow-500 text-black px-4 py-2 rounded-full text-sm font-medium inline-block">
                      {analysisResult.color_label}
                    </div>
                  </div>

                  {/* Layer Results */}
                  <div className="space-y-4">
                    {layers.map((layer) => (
                      <div key={layer.id} className="bg-gray-900 rounded-lg p-4 flex items-center justify-between border border-gray-700">
                        <div className="flex items-center space-x-3">
                          <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                            <span className="text-xs text-white">✓</span>
                          </div>
                          <div>
                            <div className="font-medium text-white">{layer.name}</div>
                            <div className="text-xs text-gray-400">Complete</div>
                          </div>
                        </div>

                        <div className="text-right">
                          <div className="text-xl font-bold" style={{ color: layer.color }}>
                            {layer.score !== null ? `${Math.round(layer.score * 100)}%` : 'N/A'}
                          </div>
                          <div className="text-xs text-gray-400">▼</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Analysis Details */}
                <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                  <h3 className="text-lg font-medium text-white mb-4">
                    **7-Layer Analysis Complete for "{uploadedFile}"**
                  </h3>

                  <div className="space-y-3 text-sm leading-relaxed">
                    <div><span className="text-gray-400">**MIME Type:**</span> DOCX</div>
                    <div><span className="text-gray-400">**Classification:**</span> {Math.round((analysisResult.layer_scores.classification || 0) * 100)}% authenticity</div>
                    <div><span className="text-gray-400">**Clone Detection:**</span> Original content</div>
                    <div><span className="text-gray-400">**Cryptographic:**</span> Limited cryptographic verification</div>
                    <div><span className="text-gray-400">**RAG Analysis:**</span> {Math.round((analysisResult.layer_scores.rag || 0) * 100)}% confidence</div>
                    <div><span className="text-gray-400">**AI Detection:**</span> {Math.round((analysisResult.layer_scores.ai_detection || 0) * 100)}% human-generated</div>
                    <div><span className="text-gray-400">**Final Prediction:**</span> {Math.round((analysisResult.layer_scores.final_prediction || 0) * 100)}% overall authenticity</div>
                  </div>
                </div>

              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DarkDashboard