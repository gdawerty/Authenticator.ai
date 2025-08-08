import React, { useState, useRef } from 'react'

interface DemoModalProps {
  onClose: () => void
}

const DemoModal: React.FC<DemoModalProps> = ({ onClose }) => {
  const [contentType, setContentType] = useState<'text' | 'image' | 'audio' | 'video'>('text')
  const [filePreview, setFilePreview] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const url = URL.createObjectURL(file)
      setFilePreview(url)
    }
  }

  const analyzeContent = () => {
    setIsAnalyzing(true)
    
    // Simulate API call
    setTimeout(() => {
      const aiProbability = Math.random() * 0.4 + 0.6
      setAnalysisResult({
        aiProbability,
        confidence: aiProbability > 0.8 ? 'High' : aiProbability > 0.6 ? 'Medium' : 'Low',
        modelVersion: 'v2.1',
        processingTime: '1.2s'
      })
      setIsAnalyzing(false)
    }, 2000)
  }

  return (
    <div 
      className="fixed inset-0 z-50 bg-charcoal-950 bg-opacity-95 flex items-center justify-center p-8"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-charcoal-900 rounded-2xl p-12 max-w-5xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-12">
          <h2 className="text-3xl font-bold text-white">Detection Demo</h2>
          <button 
            onClick={onClose}
            className="text-charcoal-400 hover:text-white text-3xl transition-colors duration-300"
          >
            &times;
          </button>
        </div>
        
        <div className="mb-12">
          <div className="flex flex-wrap gap-3">
            {(['text', 'image', 'audio', 'video'] as const).map(type => (
              <button 
                key={type}
                onClick={() => setContentType(type)}
                className={`px-6 py-3 rounded-lg transition-all duration-300 font-medium ${
                  contentType === type 
                    ? 'bg-white text-black' 
                    : 'bg-charcoal-800 text-charcoal-300 hover:bg-charcoal-700 hover:text-white'
                }`}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-12">
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white">Input Content</h3>
            
            {contentType === 'text' ? (
              <div>
                <textarea 
                  placeholder="Paste your text content here for AI detection analysis..."
                  className="w-full h-48 bg-charcoal-800 text-white p-6 rounded-lg border border-charcoal-700 focus:border-charcoal-500 focus:outline-none resize-none transition-colors duration-300"
                ></textarea>
              </div>
            ) : (
              <div>
                <div 
                  className="border-2 border-dashed border-charcoal-600 rounded-lg p-12 text-center hover:border-charcoal-400 transition-colors duration-300 cursor-pointer"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <svg className="w-16 h-16 text-charcoal-400 mx-auto mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                  </svg>
                  <p className="text-charcoal-300 text-lg mb-2">Click to upload or drag and drop</p>
                  <p className="text-sm text-charcoal-500">Supports images, audio, and video files</p>
                </div>
                <input 
                  type="file" 
                  ref={fileInputRef}
                  className="hidden" 
                  accept={contentType === 'image' ? 'image/*' : contentType === 'audio' ? 'audio/*' : 'video/*'}
                  onChange={handleFileUpload}
                />
                {filePreview && (
                  <div className="mt-6">
                    {contentType === 'image' ? (
                      <img src={filePreview} alt="Preview" className="max-w-full rounded-lg" />
                    ) : (
                      <div className="bg-charcoal-700 p-6 rounded-lg border border-charcoal-600">
                        <div className="flex items-center space-x-4">
                          <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                          </svg>
                          <div>
                            <p className="text-white font-medium">Uploaded File</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            <button 
              onClick={analyzeContent}
              className="w-full bg-white text-black py-4 rounded-lg hover:bg-charcoal-100 transition-all duration-300 font-semibold hover-lift"
            >
              Analyze Content
            </button>
          </div>

          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white">Detection Results</h3>
            <div className="bg-charcoal-800 rounded-lg p-8 h-80 flex items-center justify-center border border-charcoal-700">
              {isAnalyzing ? (
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
                  <p className="text-gray-300">Analyzing content...</p>
                </div>
              ) : analysisResult ? (
                <div className="space-y-8">
                  <div className="text-center space-y-4">
                    <div className={`text-5xl font-bold ${analysisResult.aiProbability > 0.5 ? 'text-red-400' : 'text-green-400'}`}>
                      {(analysisResult.aiProbability * 100).toFixed(1)}%
                    </div>
                    <p className="text-charcoal-300 text-lg">AI Probability</p>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-charcoal-400">Confidence Level</span>
                      <span className="text-white font-medium">{analysisResult.confidence}</span>
                    </div>
                    <div className="w-full bg-charcoal-700 rounded-full h-3">
                      <div 
                        className="h-3 rounded-full" 
                        style={{ 
                          width: `${analysisResult.aiProbability * 100}%`,
                          background: 'linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%)'
                        }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="bg-charcoal-700 rounded-lg p-6 border border-charcoal-600">
                    <h4 className="font-semibold mb-3 text-white">
                      {analysisResult.aiProbability > 0.5 ? 'Likely AI-Generated' : 'Likely Human-Created'}
                    </h4>
                    <p className="text-charcoal-300 leading-relaxed">
                      {analysisResult.aiProbability > 0.5 
                        ? 'This content shows patterns consistent with AI generation. Consider manual review for critical applications.' 
                        : 'This content appears to be human-created based on our analysis patterns.'}
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <span className="text-charcoal-400 text-sm">Processing Time</span>
                      <p className="text-white font-medium">{analysisResult.processingTime}</p>
                    </div>
                    <div className="space-y-2">
                      <span className="text-charcoal-400 text-sm">Model Version</span>
                      <p className="text-white font-medium">{analysisResult.modelVersion}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-charcoal-400 text-center">Results will appear here after analysis</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DemoModal