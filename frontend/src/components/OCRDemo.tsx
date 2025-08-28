import React, { useState } from 'react'

interface ParseResult {
  success: boolean
  file_id?: string
  original_filename?: string
  file_type?: string
  extracted_text?: string
  confidence_score?: number
  vision_tags?: string[]
  qr_codes?: Array<{
    type: string
    data: string
    bbox: number[]
  }>
  metadata?: {
    processing_time: number
    page_count?: number
    file_size?: number
  }
  error?: string
}

const OCRDemo: React.FC = () => {
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
    formData.append('detect_qr', 'true')
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
        error: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`
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
    <section id="ocr-demo" className="py-32 bg-black relative z-10">
      <div className="max-w-6xl mx-auto px-8">
        <div className="text-center space-y-6 mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white">
            OCR & Document Parsing Demo
          </h2>
          <p className="text-xl text-charcoal-300 font-light max-w-3xl mx-auto">
            Upload images, PDFs, or DOCX files to extract text, detect QR codes, and analyze content using our advanced OCR system.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Upload Section */}
          <div className="space-y-6">
            <div
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
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
                id="file-upload"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
                accept=".pdf,.png,.jpg,.jpeg,.gif,.docx"
              />
              
              {file ? (
                <div className="space-y-4">
                  <div className="w-16 h-16 mx-auto bg-green-500 rounded-full flex items-center justify-center">
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-white font-semibold">{file.name}</p>
                    <p className="text-charcoal-400">
                      {(file.size / 1024 / 1024).toFixed(2)} MB • {file.type}
                    </p>
                    {!isValidFileType(file) && (
                      <p className="text-red-400 text-sm mt-2">
                        ⚠️ Unsupported file type. Please use PDF, PNG, JPG, GIF, or DOCX files.
                      </p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="w-16 h-16 mx-auto bg-charcoal-700 rounded-full flex items-center justify-center">
                    <svg className="w-8 h-8 text-charcoal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-white font-semibold">Drop your file here</p>
                    <p className="text-charcoal-400">or click to browse</p>
                    <p className="text-sm text-charcoal-500 mt-2">
                      Supports: PDF, PNG, JPG, GIF, DOCX (max 16MB)
                    </p>
                  </div>
                </div>
              )}
              
              <label
                htmlFor="file-upload"
                className="inline-block mt-4 bg-white text-black px-6 py-3 rounded-lg hover:bg-charcoal-100 transition-all duration-300 font-semibold cursor-pointer hover-lift"
              >
                Choose File
              </label>
            </div>

            <button
              onClick={parseFile}
              disabled={!file || loading || !isValidFileType(file!)}
              className="w-full bg-white text-black px-8 py-4 rounded-lg hover:bg-charcoal-100 transition-all duration-300 font-semibold hover-lift disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-5 h-5 border-2 border-black border-t-transparent rounded-full animate-spin"></div>
                  <span>Processing...</span>
                </div>
              ) : (
                'Parse Document'
              )}
            </button>
          </div>

          {/* Results Section */}
          <div className="space-y-6">
            <h3 className="text-2xl font-bold text-white">Results</h3>
            
            {!result ? (
              <div className="bg-charcoal-900 rounded-xl p-8 border border-charcoal-800">
                <p className="text-charcoal-400 text-center">
                  Upload a file to see OCR results here
                </p>
              </div>
            ) : result.success ? (
              <div className="bg-charcoal-900 rounded-xl p-8 border border-charcoal-800 space-y-6">
                {/* File Info */}
                <div className="border-b border-charcoal-700 pb-4">
                  <h4 className="text-lg font-semibold text-white mb-2">File Information</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-charcoal-400">Type:</span>
                      <span className="text-white ml-2">{result.file_type}</span>
                    </div>
                    <div>
                      <span className="text-charcoal-400">Confidence:</span>
                      <span className="text-white ml-2">
                        {((result.confidence_score || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                    {result.metadata?.processing_time && (
                      <div>
                        <span className="text-charcoal-400">Processing Time:</span>
                        <span className="text-white ml-2">{result.metadata.processing_time}s</span>
                      </div>
                    )}
                    {result.metadata?.page_count && (
                      <div>
                        <span className="text-charcoal-400">Pages:</span>
                        <span className="text-white ml-2">{result.metadata.page_count}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Extracted Text */}
                {result.extracted_text && (
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-2">Extracted Text</h4>
                    <div className="bg-charcoal-800 rounded-lg p-4 max-h-48 overflow-y-auto">
                      <pre className="text-charcoal-200 text-sm whitespace-pre-wrap">
                        {result.extracted_text}
                      </pre>
                    </div>
                  </div>
                )}

                {/* Vision Tags */}
                {result.vision_tags && result.vision_tags.length > 0 && (
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-2">Content Tags</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.vision_tags.map((tag, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-charcoal-700 text-charcoal-200 rounded-full text-sm"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* QR Codes */}
                {result.qr_codes && result.qr_codes.length > 0 && (
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-2">QR Codes Detected</h4>
                    <div className="space-y-2">
                      {result.qr_codes.map((qr, index) => (
                        <div key={index} className="bg-charcoal-800 rounded-lg p-3">
                          <p className="text-charcoal-200 text-sm">
                            <span className="text-charcoal-400">Type:</span> {qr.type}
                          </p>
                          <p className="text-charcoal-200 text-sm break-all">
                            <span className="text-charcoal-400">Data:</span> {qr.data}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-8">
                <h4 className="text-lg font-semibold text-red-400 mb-2">Error</h4>
                <p className="text-red-300">{result.error}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}

export default OCRDemo
