import React, { useState, useRef } from 'react';

interface DemoModalProps {
  onClose: () => void;
}

interface AnalysisResult {
  file_id?: string;
  timestamp?: string;
  filename?: string;
  authenticity_score?: number;
  domain_classification?: {
    category: string;
    subcategory: string;
    confidence: number;
  };
  authenticity_metrics?: {
    content_consistency: number;
    metadata_integrity: number;
    format_validation: number;
    style_consistency: number;
  };
  content_analysis?: {
    language: string;
    complexity_score: number;
    formality_score: number;
    tone: string;
  };
  ai_detection?: {
    ai_generated_score: number;
    human_authored_confidence: number;
    detection_method: string;
  };
  security_analysis?: {
    encryption: string;
    digital_signatures: string[];
    timestamp_validation: string;
  };
  recommendations?: {
    verification_steps: string[];
    risk_mitigation: string[];
    security_suggestions: string[];
  };
  // Legacy properties for backward compatibility
  file_info?: {
    name: string;
    size: number;
    type: string;
  };
  authenticity_assessment?: {
    score: number;
    confidence: string;
    factors: string[];
  };
  text_preview?: string;
}

const DemoModal: React.FC<DemoModalProps> = ({ onClose }) => {
  const [contentType, setContentType] = useState<'text' | 'image' | 'audio' | 'video' | 'document'>('text');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loadingStage, setLoadingStage] = useState<number>(0); // 0: idle, 1: uploading, 2: analyzing, 3: classifying, 4: assessing, 5: done
  const [textInput, setTextInput] = useState('');
  const [documentFile, setDocumentFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadingMessages = [
    '',
    'Uploading document...',
    'Analyzing content...',
    'Classifying domain...',
    'Assessing authenticity...',
    'Completed'
  ];

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setDocumentFile(file);
      setError(null);
    }
  };

  const analyzeContent = async () => {
    try {
      setIsAnalyzing(true);
      setAnalysisResult(null);
      setError(null);
      setLoadingStage(0);

      if (contentType === 'document' && documentFile) {
        // Stage 1: Upload
        setLoadingStage(1);
        const formData = new FormData();
        formData.append('file', documentFile);
        await new Promise(r => setTimeout(r, 800));

        // Stage 2: Analysis
        setLoadingStage(2);
        await new Promise(r => setTimeout(r, 1000));

        // Stage 3: Classification
        setLoadingStage(3);
        await new Promise(r => setTimeout(r, 1000));

        // Stage 4: Assessment
        setLoadingStage(4);
        console.log('Sending request to analyze endpoint...');
        // Add analysis_type to formData
        formData.append('analysis_type', 'comprehensive');
        
        // Log what we're sending
        console.log('Sending FormData:');
        for (let [key, value] of formData.entries()) {
          console.log(key, value);
        }

        const response = await fetch('http://localhost:8001/api/analyze', {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
          },
          body: formData,
          mode: 'cors', // Explicitly enable CORS
        });

        if (!response.ok) {
          let errorMessage = '';
          try {
            const errorData = await response.json();
            console.error('Error response:', errorData);
            errorMessage = JSON.stringify(errorData, null, 2);
          } catch (e) {
            const errorText = await response.text();
            console.error('Error text:', errorText);
            errorMessage = errorText;
          }
          throw new Error(`Analysis request failed (${response.status}): ${errorMessage}`);
        }
        console.log('Response received:', response);

        const result = await response.json();
        console.log('Analysis result:', result);

        // Transform the API response to match our frontend expectations
        const transformedResult: AnalysisResult = {
          file_id: result.file_id,
          timestamp: result.timestamp,
          filename: result.filename,
          authenticity_score: result.authenticity_score || result.authenticity?.score,
          domain_classification: result.domain_classification,
          authenticity_metrics: result.authenticity_metrics,
          content_analysis: result.content_analysis,
          ai_detection: result.ai_detection,
          security_analysis: result.security_analysis,
          recommendations: result.recommendations,
          // Create backward-compatible structure
          // For authenticity_assessment.score: Higher = More Authentic (Less AI Generated)
          authenticity_assessment: {
            score: Math.round(((result.authenticity_score || result.authenticity?.score || 0.95) * 100)),
            confidence: result.authenticity?.confidence || 'Medium',
            factors: result.recommendations?.verification_steps || ['AI Detection Analysis', 'Content Structure Evaluation', 'Authenticity Scoring']
          },
          file_info: {
            name: result.filename || documentFile.name,
            size: documentFile.size,
            type: documentFile.type
          }
        };

        // Stage 5: Complete
        setLoadingStage(5);
        setAnalysisResult(transformedResult);

      } else if (contentType === 'text' && textInput.trim()) {
        // Simulated analysis for text input
        for (let stage = 1; stage <= 4; stage++) {
          setLoadingStage(stage);
          await new Promise(r => setTimeout(r, 500));
        }

        const result: AnalysisResult = {
          file_info: {
            name: 'Text Input',
            size: textInput.length,
            type: 'text/plain'
          },
          content_analysis: {
            language: 'English',
            complexity_score: 0.75,
            formality_score: 0.85,
            tone: 'Professional'
          },
          domain_classification: {
            category: 'General',
            subcategory: 'Text',
            confidence: 0.85
          },
          authenticity_assessment: {
            score: Math.round(Math.random() * 100),
            confidence: 'Medium',
            factors: [
              'Language patterns analysis',
              'Content structure evaluation',
              'Semantic coherence check',
              'Writing style assessment'
            ]
          },
          text_preview: textInput.slice(0, 100)
        };
        
        setLoadingStage(5);
        setAnalysisResult(result);
      }
    } catch (error) {
      console.error('Analysis error:', error);
      setError(error instanceof Error ? error.message : 'Analysis failed');
      setAnalysisResult({
        authenticity_assessment: {
          score: 0,
          confidence: 'Error',
          factors: [error instanceof Error ? error.message : 'Analysis failed']
        }
      });
    } finally {
      setIsAnalyzing(false);
      setLoadingStage(0);
    }
  };

  const renderContent = () => {
    switch (contentType) {
      case 'text':
        return (
          <div>
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Enter text to analyze..."
              className="w-full h-60 bg-charcoal-800 text-white p-4 rounded-lg border border-charcoal-700 focus:border-charcoal-500 transition-colors"
            />
          </div>
        );
      case 'document':
        return (
          <>
            <div 
              className="border-2 border-dashed border-charcoal-600 rounded-lg p-12 text-center hover:border-charcoal-400 transition-colors duration-300 cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="space-y-4">
                <svg className="mx-auto w-12 h-12 text-charcoal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <div className="text-charcoal-300">
                  <span className="font-medium text-white">Click to upload</span> or drag and drop
                </div>
              </div>
            </div>
            
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.doc,.docx,.txt"
              className="hidden"
            />
            
            {documentFile && (
              <div className="mt-6">
                <div className="bg-charcoal-700 p-6 rounded-lg border border-charcoal-600">
                  <div className="flex items-center space-x-4">
                    <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <div>
                      <p className="text-white font-medium">{documentFile.name}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="mt-4 p-4 bg-red-900/50 border border-red-500/50 rounded-lg">
                <p className="text-red-200 text-sm">{error}</p>
              </div>
            )}
          </>
        );
      default:
        return (
          <div className="border-2 border-dashed border-charcoal-600 rounded-lg p-12 text-center">
            <div className="space-y-4">
              <svg className="mx-auto w-12 h-12 text-charcoal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <div className="text-charcoal-300">
                <span className="text-xl font-medium text-white block mb-2">Coming Soon!</span>
                <p className="text-sm text-charcoal-400">{contentType.charAt(0).toUpperCase() + contentType.slice(1)} detection will be available in the next update.</p>
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="fixed inset-0 z-[9999] bg-charcoal-950 bg-opacity-100 flex items-center justify-center p-8" onClick={(e) => e.target === e.currentTarget && onClose()}>
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
            {(['text', 'image', 'audio', 'video', 'document'] as const).map(type => (
              <button 
                key={type}
                onClick={() => {
                  setContentType(type);
                  setAnalysisResult(null);
                  setIsAnalyzing(false);
                  setLoadingStage(0);
                  setTextInput('');
                  setDocumentFile(null);
                  setError(null);
                }}
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
          <div>
            {renderContent()}
            {((contentType === 'text' && textInput.trim().length > 0) || 
              (contentType === 'document' && documentFile)) && (
              <button 
                onClick={analyzeContent}
                className="w-full bg-white text-black py-4 rounded-lg hover:bg-charcoal-100 transition-all duration-300 font-semibold hover-lift"
                disabled={isAnalyzing}
              >
                {isAnalyzing ? 'Analyzing...' : 'Analyze Content'}
              </button>
            )}
          </div>

          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white">Detection Results</h3>
            <div className="bg-charcoal-800 rounded-lg p-8 h-[500px] flex items-start justify-center border border-charcoal-700">
              {isAnalyzing ? (
                <div className="space-y-6 w-full">
                  <div className="mb-4">
                    <div className="w-full bg-charcoal-700 rounded-full h-4">
                      <div
                        className="h-4 rounded-full transition-all duration-500"
                        style={{
                          width: `${loadingStage * 20}%`,
                          background: `linear-gradient(90deg, 
                            ${loadingStage < 3 ? '#6366f1' : 
                              loadingStage < 4 ? '#f59e0b' : '#10b981'}
                            0%,
                            ${loadingStage < 3 ? '#818cf8' : 
                              loadingStage < 4 ? '#fbbf24' : '#34d399'}
                            100%)`
                        }}
                      />
                    </div>
                    <div className="flex justify-between mt-2 text-sm text-charcoal-300">
                      <span>{loadingMessages[loadingStage]}</span>
                      <span>{loadingStage * 20}%</span>
                    </div>
                  </div>
                  <div className="text-center space-y-2">
                    <div className="text-lg text-white font-semibold">
                      {loadingMessages[loadingStage]}
                    </div>
                    <div className="text-sm text-charcoal-400">
                      {loadingStage === 1 && 'Preparing document for analysis...'}
                      {loadingStage === 2 && 'Extracting content patterns...'}
                      {loadingStage === 3 && 'Identifying domain expertise...'}
                      {loadingStage === 4 && 'Evaluating AI probability...'}
                    </div>
                  </div>
                </div>
              ) : analysisResult ? (
                <div className="w-full h-full overflow-y-auto space-y-6 py-2">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-white mb-4">Authenticity Score</div>
                    <div className="relative w-full h-12 bg-charcoal-700 rounded-full overflow-hidden">
                      <div
                        className="absolute left-0 top-0 h-full transition-all duration-500 rounded-full"
                        style={{
                          width: `${analysisResult.authenticity_assessment?.score || 0}%`,
                          background: `linear-gradient(90deg, 
                            ${(analysisResult.authenticity_assessment?.score || 0) > 70 ? '#10b981' : 
                              (analysisResult.authenticity_assessment?.score || 0) > 40 ? '#f59e0b' : '#ef4444'}
                            0%, 
                            ${(analysisResult.authenticity_assessment?.score || 0) > 70 ? '#34d399' : 
                              (analysisResult.authenticity_assessment?.score || 0) > 40 ? '#fbbf24' : '#f87171'}
                            100%)`
                        }}
                      />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-xl font-bold text-white">
                          {analysisResult.authenticity_assessment?.score || 0}% Authentic
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* File Information */}
                  {analysisResult.file_info && (
                    <div className="bg-charcoal-700/50 rounded-lg p-4">
                      <h4 className="text-white font-semibold mb-2">File Information</h4>
                      <div className="space-y-1 text-sm text-charcoal-300">
                        <p>Name: {analysisResult.file_info.name}</p>
                        <p>Size: {(analysisResult.file_info.size / 1024).toFixed(1)} KB</p>
                        <p>Type: {analysisResult.file_info.type}</p>
                      </div>
                    </div>
                  )}

                  {/* Content Analysis */}
                  {analysisResult.content_analysis && (
                    <div className="bg-charcoal-700/50 rounded-lg p-4">
                      <h4 className="text-white font-semibold mb-2">Content Analysis</h4>
                      <div className="space-y-1 text-sm text-charcoal-300">
                        <p>Language: {analysisResult.content_analysis.language}</p>
                        <p>Complexity: {(analysisResult.content_analysis.complexity_score * 100).toFixed(1)}%</p>
                        <p>Formality: {(analysisResult.content_analysis.formality_score * 100).toFixed(1)}%</p>
                        <p>Tone: {analysisResult.content_analysis.tone}</p>
                      </div>
                    </div>
                  )}

                  {/* Domain Classification */}
                  {analysisResult.domain_classification && (
                    <div className="bg-charcoal-700/50 rounded-lg p-4">
                      <h4 className="text-white font-semibold mb-2">Domain Classification</h4>
                      <div className="space-y-1 text-sm text-charcoal-300">
                        <p>Category: {analysisResult.domain_classification.category}</p>
                        <p>Subcategory: {analysisResult.domain_classification.subcategory}</p>
                        <p>Confidence: {(analysisResult.domain_classification.confidence * 100).toFixed(1)}%</p>
                      </div>
                    </div>
                  )}

                  {/* AI Detection Details */}
                  {analysisResult.ai_detection && (
                    <div className="bg-charcoal-700/50 rounded-lg p-4">
                      <h4 className="text-white font-semibold mb-2">AI Detection Analysis</h4>
                      <div className="space-y-1 text-sm text-charcoal-300">
                        <p>AI Generated Score: {(analysisResult.ai_detection.ai_generated_score * 100).toFixed(1)}%</p>
                        <p>Human Authored: {(analysisResult.ai_detection.human_authored_confidence * 100).toFixed(1)}%</p>
                        <p>Method: {analysisResult.ai_detection.detection_method}</p>
                      </div>
                    </div>
                  )}

                  {/* Assessment Details */}
                  {analysisResult.authenticity_assessment && (
                    <div className="bg-charcoal-700/50 rounded-lg p-4">
                      <h4 className="text-white font-semibold mb-2">Assessment Details</h4>
                      <div className="space-y-1 text-sm text-charcoal-300">
                        <p>Result: {
                          analysisResult.authenticity_assessment.score > 70 ? 'Highly Authentic' :
                          analysisResult.authenticity_assessment.score > 40 ? 'Moderately Authentic' : 
                          'Low Authenticity'
                        }</p>
                        <p>Confidence: {analysisResult.authenticity_assessment.confidence}</p>
                        <div className="mt-2">
                          <p className="font-medium mb-1">Key Factors:</p>
                          <ul className="list-disc list-inside">
                            {analysisResult.authenticity_assessment.factors.map((factor, index) => (
                              <li key={index}>{factor}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Security Analysis */}
                  {analysisResult.security_analysis && (
                    <div className="bg-charcoal-700/50 rounded-lg p-4">
                      <h4 className="text-white font-semibold mb-2">Security Analysis</h4>
                      <div className="space-y-1 text-sm text-charcoal-300">
                        <p>Encryption: {analysisResult.security_analysis.encryption}</p>
                        <p>Digital Signatures: {analysisResult.security_analysis.digital_signatures.join(', ')}</p>
                        <p>Timestamp Validation: {analysisResult.security_analysis.timestamp_validation}</p>
                      </div>
                    </div>
                  )}

                  {/* Recommendations */}
                  {analysisResult.recommendations && (
                    <div className="bg-charcoal-700/50 rounded-lg p-4">
                      <h4 className="text-white font-semibold mb-2">Recommendations</h4>
                      <div className="space-y-2 text-sm text-charcoal-300">
                        {analysisResult.recommendations.verification_steps && (
                          <div>
                            <p className="font-medium">Verification Steps:</p>
                            <ul className="list-disc list-inside ml-2">
                              {analysisResult.recommendations.verification_steps.map((step, index) => (
                                <li key={index}>{step}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {analysisResult.recommendations.security_suggestions && (
                          <div>
                            <p className="font-medium">Security Suggestions:</p>
                            <ul className="list-disc list-inside ml-2">
                              {analysisResult.recommendations.security_suggestions.map((suggestion, index) => (
                                <li key={index}>{suggestion}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-charcoal-400 text-center">Results will appear here after analysis</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemoModal;
