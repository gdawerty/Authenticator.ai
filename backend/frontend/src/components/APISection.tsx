import React, { useState } from 'react'

interface ParseResult {
  success: boolean
  file_type?: string
  extracted_text?: string
  confidence_score?: number
  vision_tags?: string[]
  error?: string
}

const APISection: React.FC = () => {
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<ParseResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [dragActive, setDragActive] = useState(false)

  const handleFileChange = (selectedFile: File) => {
    setFile(selectedFile)
    setResult(null)
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0])
    }
  }

  const parseFile = async () => {
    if (!file) return

    setLoading(true)
    const formData = new FormData()
    formData.append('file', file)
    formData.append('enhance_ocr', 'true')
    formData.append('vision_analysis', 'true')

    try {
      const response = await fetch('http://localhost:8001/api/parse', {
        method: 'POST',
        body: formData,
      })
      
      const data = await response.json()
      setResult(data)
    } catch (error) {
      setResult({
        success: false,
        error: `Connection error: Make sure backend is running on port 8001`
      })
    } finally {
      setLoading(false)
    }
  }

  const isValidFileType = (file: File) => {
    const validTypes = [
      'application/pdf',
      'image/png',
      'image/jpeg',
      'image/jpg',
      'image/gif',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    return validTypes.includes(file.type)
  }

  return (
    <section id="api" className="py-32 minimal-gradient relative z-10">
      <div className="max-w-6xl mx-auto px-8">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div className="space-y-8">
            <div className="space-y-6">
              <h2 className="text-4xl md:text-5xl font-bold text-white">OCR & Document Analysis</h2>
              <p className="text-xl text-charcoal-300 font-light leading-relaxed">
                Extract text from images, PDFs, and documents using advanced OCR technology. Built with Tesseract and enhanced vision analysis.
              </p>
            </div>
            
            <div className="space-y-6">
              {[
                "Multi-format support (PDF, Images, DOCX)",
                "Advanced OCR with confidence scoring",
                "Vision analysis and content tagging",
                "QR code detection and decoding"
              ].map((item, index) => (
                <div key={index} className="flex items-start space-x-4">
                  <div className="w-1.5 h-1.5 bg-white rounded-full mt-3 flex-shrink-0"></div>
                  <span className="text-charcoal-300">{item}</span>
                </div>
              ))}
            </div>
            
            <a 
              href="http://localhost:8001/api/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-block bg-white text-black px-8 py-4 rounded-lg hover:bg-charcoal-100 transition-all duration-300 font-semibold hover-lift"
            >
              View API Docs
            </a>
          </div>
          
          <div className="space-y-6">
            {/* Upload Area */}
            <div
              className={`border-2 border-dashed rounded-xl p-6 text-center transition-all duration-300 ${
                dragActive
                  ? 'border-white bg-charcoal-900'
                  : file
                  ? 'border-green-500 bg-charcoal-950'
                  : 'border-charcoal-600 hover:border-charcoal-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                id="demo-file-upload"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
                accept=".pdf,.png,.jpg,.jpeg,.gif,.docx"
              />
              
              {file ? (
                <div className="space-y-3">
                  <div className="w-12 h-12 mx-auto bg-green-500 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-white font-semibold text-sm">{file.name}</p>
                    <p className="text-charcoal-400 text-xs">
                      {(file.size / 1024 / 1024).toFixed(1)} MB
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="w-12 h-12 mx-auto bg-charcoal-700 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-charcoal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-white font-semibold text-sm">Try OCR Demo</p>
                    <p className="text-charcoal-400 text-xs">Drop file or click to browse</p>
                  </div>
                </div>
              )}
              
              <label
                htmlFor="demo-file-upload"
                className="inline-block mt-3 bg-charcoal-700 text-white px-4 py-2 rounded-lg hover:bg-charcoal-600 transition-all duration-300 text-sm font-medium cursor-pointer"
              >
                Choose File
              </label>
            </div>

            <button
              onClick={parseFile}
              disabled={!file || loading || !isValidFileType(file!)}
              className="w-full bg-white text-black px-6 py-3 rounded-lg hover:bg-charcoal-100 transition-all duration-300 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin"></div>
                  <span>Processing...</span>
                </div>
              ) : (
                'Extract Text'
              )}
            </button>

            {/* Results */}
            {result && (
              <div className="bg-charcoal-900 rounded-xl p-6 border border-charcoal-800">
                {result.success ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-charcoal-400">Extracted Text</span>
                      {result.confidence_score && (
                        <span className="text-sm text-green-400">
                          {(result.confidence_score * 100).toFixed(1)}% confidence
                        </span>
                      )}
                    </div>
                    
                    {result.extracted_text ? (
                      <div className="bg-charcoal-800 rounded-lg p-3 max-h-32 overflow-y-auto">
                        <pre className="text-charcoal-200 text-sm whitespace-pre-wrap">
                          {result.extracted_text.substring(0, 200)}
                          {result.extracted_text.length > 200 && '...'}
                        </pre>
                      </div>
                    ) : (
                      <p className="text-charcoal-400 text-sm">No text detected</p>
                    )}
                    
                    {result.vision_tags && result.vision_tags.length > 0 && (
                      <div>
                        <span className="text-sm text-charcoal-400">Content Tags:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {result.vision_tags.slice(0, 3).map((tag, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 bg-charcoal-700 text-charcoal-300 rounded text-xs"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-red-400 text-sm">
                    <p>Error: {result.error}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}

export default APISection