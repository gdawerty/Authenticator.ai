import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

interface ParseResult {
  success: boolean
  file_id?: string
  original_filename?: string
  file_type?: string
  raw_text?: string
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
  // Sprint 3 Enhanced Authenticity Pipeline
  authenticity_score?: number
  pipeline_stages?: {
    intake?: { status: string; timestamp: string; details?: any }
    fingerprint?: { status: string; timestamp: string; details?: any }
    integrity?: { status: string; timestamp: string; details?: any }
    classification?: { status: string; timestamp: string; details?: any }
    verification?: { status: string; timestamp: string; details?: any }
    scoring?: { status: string; timestamp: string; details?: any }
    decisioning?: { status: string; timestamp: string; details?: any }
    learning?: { status: string; timestamp: string; details?: any }
    attestation?: { status: string; timestamp: string; details?: any }
  }
  fingerprint_analysis?: {
    text_fingerprint?: {
      shingles_count: number
      simhash: string
      clone_matches: Array<{
        file_id: string
        similarity_score: number
        match_type: string
      }>
    }
    image_fingerprint?: {
      phash: string
      dhash: string
      ahash: string
      whash: string
      clone_matches: Array<{
        file_id: string
        similarity_score: number
        hash_type: string
      }>
    }
    document_fingerprint?: {
      template_hash: string
      layout_signature: string
    }
  }
  integrity_analysis?: {
    signature_verification?: any
    watermark_detection?: any
    edit_trace_analysis?: any
    metadata_forensics?: any
  }
  clone_detection?: {
    is_clone: boolean
    confidence: number
    training_updated: boolean
    verified_original?: boolean
    matches_found: number
  }
  qr_attestation?: {
    attestation_code: string
    verification_url: string
    chain_of_custody: Array<{
      timestamp: string
      action: string
      details: string
    }>
  }
  error?: string
}

const OCRDemo: React.FC = () => {
  const navigate = useNavigate()
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
    formData.append('analysis_type', 'comprehensive')
    formData.append('enable_fingerprinting', 'true')
    formData.append('enable_clone_detection', 'true')
    formData.append('enable_integrity_forensics', 'true')
    formData.append('enable_self_training', 'true')

    try {
      const response = await fetch('http://localhost:8001/api/analyze', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (data.success && data.file_id) {
        navigate(`/analysis?file_id=${data.file_id}`)
      } else {
        setResult(data)
      }
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
            Enhanced Authenticity Pipeline Demo
          </h2>
          <p className="text-xl text-charcoal-300 font-light max-w-3xl mx-auto">
            Upload documents for comprehensive authenticity analysis including fingerprinting, clone detection, integrity forensics, and self-training ML classification.
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
                {/* Authenticity Score Banner */}
                {result.authenticity_score !== undefined && (
                  <div className={`p-4 rounded-lg border ${
                    result.authenticity_score >= 80
                      ? 'bg-green-900/30 border-green-500'
                      : result.authenticity_score >= 60
                      ? 'bg-yellow-900/30 border-yellow-500'
                      : 'bg-red-900/30 border-red-500'
                  }`}>
                    <div className="flex items-center justify-between">
                      <h4 className="text-lg font-semibold text-white">Authenticity Score</h4>
                      <span className={`text-2xl font-bold ${
                        result.authenticity_score >= 80
                          ? 'text-green-400'
                          : result.authenticity_score >= 60
                          ? 'text-yellow-400'
                          : 'text-red-400'
                      }`}>
                        {result.authenticity_score.toFixed(1)}%
                      </span>
                    </div>
                    {result.clone_detection?.training_updated && (
                      <p className="text-sm text-blue-400 mt-2">
                        🧠 Clone detection database updated with this document
                      </p>
                    )}
                  </div>
                )}

                {/* Pipeline Stages Breakdown */}
                {result.pipeline_stages && (
                  <div className="border-b border-charcoal-700 pb-4">
                    <h4 className="text-lg font-semibold text-white mb-3">Pipeline Stages</h4>
                    <div className="grid grid-cols-3 gap-2 text-sm">
                      {Object.entries(result.pipeline_stages).map(([stage, data]) => (
                        <div key={stage} className={`flex items-center space-x-2 p-2 rounded ${
                          data.status === 'completed' ? 'bg-green-900/20' :
                          data.status === 'failed' ? 'bg-red-900/20' : 'bg-yellow-900/20'
                        }`}>
                          <div className={`w-2 h-2 rounded-full ${
                            data.status === 'completed' ? 'bg-green-400' :
                            data.status === 'failed' ? 'bg-red-400' : 'bg-yellow-400'
                          }`}></div>
                          <span className="text-charcoal-200 capitalize">{stage}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Clone Detection Results */}
                {result.clone_detection && (
                  <div className="border-b border-charcoal-700 pb-4">
                    <h4 className="text-lg font-semibold text-white mb-2">Clone Detection Analysis</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-charcoal-400">Clone Status:</span>
                        <span className={`ml-2 font-semibold ${
                          result.clone_detection.is_clone ? 'text-red-400' : 'text-green-400'
                        }`}>
                          {result.clone_detection.is_clone ? 'Potential Clone' : 'Original'}
                        </span>
                      </div>
                      <div>
                        <span className="text-charcoal-400">Confidence:</span>
                        <span className="text-white ml-2">{result.clone_detection.confidence.toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-charcoal-400">Matches Found:</span>
                        <span className="text-white ml-2">{result.clone_detection.matches_found}</span>
                      </div>
                      {result.clone_detection.verified_original && (
                        <div>
                          <span className="text-charcoal-400">Status:</span>
                          <span className="text-green-400 ml-2">✓ Verified Original</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Fingerprint Analysis */}
                {result.fingerprint_analysis && (
                  <div className="border-b border-charcoal-700 pb-4">
                    <h4 className="text-lg font-semibold text-white mb-2">Fingerprint Analysis</h4>

                    {result.fingerprint_analysis.text_fingerprint && (
                      <div className="mb-4">
                        <h5 className="text-md font-medium text-white mb-2">Text Fingerprint</h5>
                        <div className="bg-charcoal-800 rounded-lg p-3 space-y-2">
                          <div className="text-sm">
                            <span className="text-charcoal-400">Shingles:</span>
                            <span className="text-white ml-2">{result.fingerprint_analysis.text_fingerprint.shingles_count}</span>
                          </div>
                          <div className="text-sm">
                            <span className="text-charcoal-400">SimHash:</span>
                            <span className="text-charcoal-300 ml-2 font-mono text-xs">{result.fingerprint_analysis.text_fingerprint.simhash}</span>
                          </div>
                          {result.fingerprint_analysis.text_fingerprint.clone_matches.length > 0 && (
                            <div>
                              <span className="text-charcoal-400 text-sm">Similar Documents:</span>
                              <div className="mt-1 space-y-1">
                                {result.fingerprint_analysis.text_fingerprint.clone_matches.map((match, i) => (
                                  <div key={i} className="text-xs bg-charcoal-700 p-2 rounded">
                                    <span className="text-red-400">Match {i+1}: </span>
                                    <span className="text-white">{(match.similarity_score * 100).toFixed(1)}% similar</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {result.fingerprint_analysis.image_fingerprint && (
                      <div className="mb-4">
                        <h5 className="text-md font-medium text-white mb-2">Image Fingerprint</h5>
                        <div className="bg-charcoal-800 rounded-lg p-3 space-y-2">
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div><span className="text-charcoal-400">pHash:</span> <span className="text-charcoal-300 font-mono">{result.fingerprint_analysis.image_fingerprint.phash.slice(0, 16)}...</span></div>
                            <div><span className="text-charcoal-400">dHash:</span> <span className="text-charcoal-300 font-mono">{result.fingerprint_analysis.image_fingerprint.dhash.slice(0, 16)}...</span></div>
                            <div><span className="text-charcoal-400">aHash:</span> <span className="text-charcoal-300 font-mono">{result.fingerprint_analysis.image_fingerprint.ahash.slice(0, 16)}...</span></div>
                            <div><span className="text-charcoal-400">wHash:</span> <span className="text-charcoal-300 font-mono">{result.fingerprint_analysis.image_fingerprint.whash.slice(0, 16)}...</span></div>
                          </div>
                          {result.fingerprint_analysis.image_fingerprint.clone_matches.length > 0 && (
                            <div>
                              <span className="text-charcoal-400 text-sm">Similar Images:</span>
                              <div className="mt-1 space-y-1">
                                {result.fingerprint_analysis.image_fingerprint.clone_matches.map((match, i) => (
                                  <div key={i} className="text-xs bg-charcoal-700 p-2 rounded">
                                    <span className="text-red-400">Match {i+1}: </span>
                                    <span className="text-white">{(match.similarity_score * 100).toFixed(1)}% similar ({match.hash_type})</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}

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
                {result.raw_text && (
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-2">Extracted Text</h4>
                    <div className="bg-charcoal-800 rounded-lg p-4 max-h-48 overflow-y-auto">
                      <pre className="text-charcoal-200 text-sm whitespace-pre-wrap">
                        {result.raw_text}
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

                {/* QR Attestation & Chain of Custody */}
                {result.qr_attestation && (
                  <div className="border-b border-charcoal-700 pb-4">
                    <h4 className="text-lg font-semibold text-white mb-2">Digital Attestation</h4>
                    <div className="bg-charcoal-800 rounded-lg p-4 space-y-3">
                      <div>
                        <span className="text-charcoal-400 text-sm">Attestation Code:</span>
                        <div className="mt-1 font-mono text-xs text-green-400 bg-charcoal-900 p-2 rounded">
                          {result.qr_attestation.attestation_code}
                        </div>
                      </div>
                      <div>
                        <span className="text-charcoal-400 text-sm">Verification URL:</span>
                        <div className="mt-1">
                          <a
                            href={result.qr_attestation.verification_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:text-blue-300 text-sm underline"
                          >
                            {result.qr_attestation.verification_url}
                          </a>
                        </div>
                      </div>
                      {result.qr_attestation.chain_of_custody && result.qr_attestation.chain_of_custody.length > 0 && (
                        <div>
                          <span className="text-charcoal-400 text-sm">Audit Trail:</span>
                          <div className="mt-2 space-y-1 max-h-32 overflow-y-auto">
                            {result.qr_attestation.chain_of_custody.map((entry, i) => (
                              <div key={i} className="text-xs bg-charcoal-700 p-2 rounded flex justify-between">
                                <span className="text-charcoal-200">{entry.action}</span>
                                <span className="text-charcoal-400">{new Date(entry.timestamp).toLocaleTimeString()}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Integrity Analysis */}
                {result.integrity_analysis && (
                  <div className="border-b border-charcoal-700 pb-4">
                    <h4 className="text-lg font-semibold text-white mb-2">Integrity Forensics</h4>
                    <div className="grid grid-cols-2 gap-4">
                      {result.integrity_analysis.signature_verification && (
                        <div className="bg-charcoal-800 rounded-lg p-3">
                          <h5 className="text-sm font-medium text-white mb-1">Digital Signature</h5>
                          <p className="text-xs text-charcoal-300">
                            {result.integrity_analysis.signature_verification.valid ? '✓ Valid' : '✗ Invalid'}
                          </p>
                        </div>
                      )}
                      {result.integrity_analysis.watermark_detection && (
                        <div className="bg-charcoal-800 rounded-lg p-3">
                          <h5 className="text-sm font-medium text-white mb-1">AI Watermark</h5>
                          <p className="text-xs text-charcoal-300">
                            {result.integrity_analysis.watermark_detection.detected ? 'Detected' : 'None Found'}
                          </p>
                        </div>
                      )}
                      {result.integrity_analysis.edit_trace_analysis && (
                        <div className="bg-charcoal-800 rounded-lg p-3">
                          <h5 className="text-sm font-medium text-white mb-1">Edit Detection</h5>
                          <p className="text-xs text-charcoal-300">
                            {result.integrity_analysis.edit_trace_analysis.modifications_detected ? 'Edits Found' : 'Original'}
                          </p>
                        </div>
                      )}
                      {result.integrity_analysis.metadata_forensics && (
                        <div className="bg-charcoal-800 rounded-lg p-3">
                          <h5 className="text-sm font-medium text-white mb-1">Metadata</h5>
                          <p className="text-xs text-charcoal-300">
                            {result.integrity_analysis.metadata_forensics.anomalies_detected ? 'Anomalies Found' : 'Clean'}
                          </p>
                        </div>
                      )}
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
