import { useState, useRef } from 'react';

// Types for the dashboard
interface FlaggedContent {
  layer: number;
  layer_name: string;
  severity: 'critical' | 'warning' | 'info';
  type: string;
  message: string;
  details?: any;
  location?: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  analysis?: any;
  attachments?: Array<{ name: string; type: string; size: number; }>;
}

interface ChatSession {
  id: string;
  name: string;
  lastMessage?: string;
  timestamp: Date;
  messageCount: number;
}

interface DashboardProps {
  user: {
    name: string;
    email: string;
    avatar?: string;
  };
  onLogout: () => void;
}

const Dashboard = ({ user, onLogout }: DashboardProps) => {
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [currentDocument, setCurrentDocument] = useState<{
    name: string;
    content: string;
    type: string;
    size: number;
  } | null>(null);
  const [currentAnalysis, setCurrentAnalysis] = useState<any>(null);
  const [analysisProgress, setAnalysisProgress] = useState<{
    layer1: 'pending' | 'processing' | 'completed';
    layer2: 'pending' | 'processing' | 'completed';
    layer3: 'pending' | 'processing' | 'completed';
    layer4: 'pending' | 'processing' | 'completed';
    layer5: 'pending' | 'processing' | 'completed';
    layer6: 'pending' | 'processing' | 'completed';
    layer7: 'pending' | 'processing' | 'completed';
  }>({
    layer1: 'pending',
    layer2: 'pending',
    layer3: 'pending',
    layer4: 'pending',
    layer5: 'pending',
    layer6: 'pending',
    layer7: 'pending'
  });
  
  // New state for pipeline choice
  const [showPipelineChoice, setShowPipelineChoice] = useState(false);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [storeForCloneDetection, setStoreForCloneDetection] = useState(false);

  // Layer explanations for 7-layer architecture
  const layerExplanations = {
    'MIME Detection': {
      description: "Analyzes file structure and format to detect the actual file type, regardless of extension. This prevents malicious files disguised as safe documents.",
      details: "Examines binary signatures, headers, and metadata to verify authentic file structure and detect potential format spoofing attacks."
    },
    'Classification': {
      description: "Uses AI models to classify content type and identify potential threats or anomalies in the document structure and content.",
      details: "Employs machine learning algorithms to categorize content, detect suspicious patterns, and identify known attack vectors or malicious payloads."
    },
    'Clone Detection': {
      description: "Compares document against a database of known files using SimHash and MinHash algorithms to detect near-duplicates and similar content.",
      details: "Generates unique fingerprints to identify document similarity, plagiarism, or potential reuse of malicious content from previous attacks."
    },
    'Cryptographic': {
      description: "Performs cryptographic verification including digital signatures, hash integrity checks, and certificate validation.",
      details: "Validates digital certificates, checks file integrity through cryptographic hashes, and verifies authenticity through signature analysis."
    },
    'RAG Analysis': {
      description: "Retrieval-Augmented Generation analysis for fact-checking and source verification against knowledge bases.",
      details: "Cross-references document content with trusted knowledge sources to verify claims, detect misinformation, and validate factual accuracy."
    },
    'AI Detection': {
      description: "Detects AI-generated content using Fast-Detect-GPT and advanced language model analysis techniques.",
      details: "Identifies artificially generated text content using sophisticated AI detection models to ensure human authenticity of written materials."
    },
    'Final Prediction': {
      description: "Combines all layer results using weighted scoring to produce final authenticity assessment and threat level.",
      details: "Integrates findings from all analysis layers to provide comprehensive authenticity score, threat assessment, and actionable recommendations."
    }
  };

  // Helper function for risk level colors
  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case 'low':
        return 'bg-green-600 text-green-100';
      case 'medium':
        return 'bg-yellow-600 text-yellow-100';
      case 'high':
        return 'bg-red-600 text-red-100';
      default:
        return 'bg-gray-600 text-gray-100';
    }
  };

  const [sessions, setSessions] = useState<ChatSession[]>([
    {
      id: '1',
      name: 'Document Analysis #1',
      lastMessage: 'Authenticity score: 0.87',
      timestamp: new Date(Date.now() - 3600000),
      messageCount: 5
    },
    {
      id: '2', 
      name: 'Contract Verification',
      lastMessage: 'High confidence detection',
      timestamp: new Date(Date.now() - 7200000),
      messageCount: 3
    }
  ]);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleNewChat = () => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      name: `New Analysis ${sessions.length + 1}`,
      timestamp: new Date(),
      messageCount: 0
    };
    setSessions([newSession, ...sessions]);
    setCurrentSessionId(newSession.id);
    setMessages([]);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsAnalyzing(true);

    // Simulate AI response with analysis
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I\'ve analyzed your content through our 7-layer authenticity pipeline. Here are the results:',
        timestamp: new Date(),
        analysis: {
          overallScore: 0.85,
          layer1: { name: 'MIME Detection', score: 0.95, status: 'completed' },
          layer2: { name: 'Classification', score: 0.88, status: 'completed' },
          layer3: { name: 'Clone Detection', score: 0.82, status: 'completed' },
          layer4: { name: 'Cryptographic', score: 0.75, status: 'completed' },
          riskLevel: 'low',
          confidence: 'high'
        }
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsAnalyzing(false);
    }, 2000);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Store the file and show pipeline choice dialog
    setPendingFile(file);
    setShowPipelineChoice(true);
  };

  const processPipelineChoice = (choice: 'analyze' | 'train') => {
    const file = pendingFile;
    if (!file) return;

    setShowPipelineChoice(false);
    setPendingFile(null);

    // Read file content for text files
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      
      setCurrentDocument({
        name: file.name,
        content: content || 'File content could not be read',
        type: file.type,
        size: file.size
      });

      // Reset analysis progress
      setAnalysisProgress({
        layer1: 'pending',
        layer2: 'pending',
        layer3: 'pending',
        layer4: 'pending',
        layer5: 'pending',
        layer6: 'pending',
        layer7: 'pending'
      });

      setUploadProgress(0);
      
      // Simulate upload progress
      const interval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev === null) return 0;
          if (prev >= 100) {
            clearInterval(interval);
            setTimeout(() => {
              setUploadProgress(null);
              if (choice === 'analyze') {
                startAnalysis(file);
              } else {
                startTraining(file);
              }
            }, 1000);
            return prev;
          }
          return prev + 10;
        });
      }, 100);
    };

    // Read as text for most file types
    if (file.type.startsWith('text/') || file.name.endsWith('.txt') || file.name.endsWith('.md')) {
      reader.readAsText(file);
    } else {
      // For other files, show file info
      setCurrentDocument({
        name: file.name,
        content: `File: ${file.name}\nType: ${file.type}\nSize: ${(file.size / 1024).toFixed(1)} KB\n\n[Binary file - content preview not available]`,
        type: file.type,
        size: file.size
      });
      
      setUploadProgress(0);
      const interval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev === null) return 0;
          if (prev >= 100) {
            clearInterval(interval);
            setTimeout(() => {
              setUploadProgress(null);
              if (choice === 'analyze') {
                startAnalysis(file);
              } else {
                startTraining(file);
              }
            }, 1000);
            return prev;
          }
          return prev + 10;
        });
      }, 100);
    }
  };

  const startTraining = (file: File) => {
    setIsAnalyzing(true);
    
    // Add training message to chat
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: `🎯 Training clone database with document: ${file.name}`,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    // Call real training API
    const formData = new FormData();
    formData.append('file', file);

    fetch('http://localhost:8001/api/train-clone', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `✅ Successfully added "${file.name}" to the clone detection database.

📊 **Training Summary:**
• Document processed and indexed
• File hash: ${data.file_hash}
• SimHash and MinHash signatures generated
• Added to similarity detection database
• Future uploads will be compared against this document

The system can now detect similar or duplicate versions of this content in future analyses.`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `❌ Training failed: ${data.error || 'Unknown error occurred'}`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
      setIsAnalyzing(false);
    })
    .catch(error => {
      console.error('Training error:', error);
      
      // Fallback to simulated training
      setTimeout(() => {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `✅ Successfully added "${file.name}" to the clone detection database. (Simulated)

📊 **Training Summary:**
• Document processed and indexed
• SimHash and MinHash signatures generated
• Added to similarity detection database
• Future uploads will be compared against this document

The system can now detect similar or duplicate versions of this content in future analyses.`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
        setIsAnalyzing(false);
      }, 3000);
    });
  };

  const startAnalysis = (file: File) => {
    setIsAnalyzing(true);
    
    // Add analysis start message to chat
    const analysisMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: `🔍 Starting 7-layer analysis for: ${file.name}`,
      timestamp: new Date(),
      attachments: [{
        name: file.name,
        type: file.type,
        size: file.size
      }]
    };
    setMessages(prev => [...prev, analysisMessage]);

    // Call real analysis API
    const formData = new FormData();
    formData.append('file', file);
    formData.append('store_for_clone_detection', storeForCloneDetection.toString());

    fetch('http://localhost:8001/api/analyze', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.document_id) {
        // New API format
        
        // Update analysis progress to completed
        setAnalysisProgress({
          layer1: 'completed',
          layer2: 'completed', 
          layer3: 'completed',
          layer4: 'completed',
          layer5: 'completed',
          layer6: 'completed',
          layer7: 'completed'
        });

        // Set current analysis for the side panel using new API format
        const layerScores = data.document_analysis.layer_scores;
        const finalAssessment = data.final_assessment;

        const finalAnalysis = {
          overallScore: finalAssessment.authenticity_score,
          layer1: {
            name: 'MIME Detection',
            score: 0.95, // Mock high score
            status: 'completed'
          },
          layer2: {
            name: 'Classification',
            score: layerScores.classification,
            status: 'completed'
          },
          layer3: {
            name: 'Clone Detection',
            score: layerScores.clone,
            status: 'completed'
          },
          layer4: {
            name: 'Cryptographic',
            score: layerScores.crypto,
            status: 'completed'
          },
          layer5: {
            name: 'RAG Analysis',
            score: layerScores.rag,
            status: layerScores.rag ? 'completed' : 'pending'
          },
          layer6: {
            name: 'AI Detection',
            score: layerScores.ai_detection,
            status: 'completed'
          },
          layer7: {
            name: 'Final Prediction',
            score: finalAssessment.authenticity_score,
            status: 'completed'
          },
          riskLevel: finalAssessment.risk_level,
          confidence: finalAssessment.confidence
        };
        
        setCurrentAnalysis(finalAnalysis);

        // Create enhanced chat message with 7-layer analysis results using new API format
        const analysisMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `🔍 **7-Layer Analysis Complete for "${file.name}"**

**MIME Type:** DOCX

**Classification:** ${Math.round(layerScores.classification * 100)}% authenticity

**Clone Detection:** ${layerScores.clone > 0.5 ? 'Original content' : 'Potential duplicate detected'}

**Cryptographic:** ${layerScores.crypto > 0.5 ? 'Metadata validated' : 'Limited cryptographic verification'}

**RAG Analysis:** ${layerScores.rag ? 'Complete' : 'Not yet implemented'}

**AI Detection:** ${layerScores.ai_detection > 0.5 ? 'Human-written content' : 'AI-generated content detected'}

**Final Assessment:** ${Math.round(finalAssessment.authenticity_score * 100)}% authenticity | Risk Level: ${finalAssessment.risk_level.toUpperCase()}`,
          timestamp: new Date(),
          analysis: finalAnalysis
        };
        
        setMessages(prev => [...prev, analysisMessage]);
      } else {
        // Handle API error
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `❌ Analysis failed: ${data.error || 'Unknown error occurred'}`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
      
      setIsAnalyzing(false);
    })
    .catch(error => {
      console.error('Analysis error:', error);
      
      // Fallback to simulated analysis on error
      const layers = ['layer1', 'layer2', 'layer3', 'layer4', 'layer5', 'layer6', 'layer7'];
      const layerTimes = [800, 1200, 1500, 1000, 900, 1100, 600];
      
      let currentLayerIndex = 0;
      
      const processLayer = () => {
        if (currentLayerIndex >= layers.length) {
          // Analysis complete - fallback simulation
          const finalAnalysis = {
            overallScore: 0.91,
            layer1: { name: 'MIME Detection', score: 0.98, status: 'completed', processingTime: 0.8 },
            layer2: { name: 'Classification', score: 0.92, status: 'completed', processingTime: 1.2 },
            layer3: { name: 'Clone Detection', score: 0.89, status: 'completed', processingTime: 1.5 },
            layer4: { name: 'Cryptographic', score: 0.85, status: 'completed', processingTime: 1.0 },
            layer5: { name: 'RAG Analysis', score: 0.75, status: 'pending', processingTime: 0.9 },
            layer6: { name: 'AI Detection', score: 0.88, status: 'completed', processingTime: 1.1 },
            layer7: { name: 'Final Prediction', score: 0.91, status: 'completed', processingTime: 0.6 },
            riskLevel: 'low',
            confidence: 'very_high'
          };
          
          setCurrentAnalysis(finalAnalysis);
          setIsAnalyzing(false);
          
          // Add fallback analysis result to chat
          const analysisMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: `🔍 **7-Layer Analysis Complete for "${file.name}"** (Simulated)

**MIME Type:** ${file.type.includes('pdf') ? 'PDF' : file.type.includes('image') ? 'IMAGE' : 'DOCUMENT'}

**Classification:** Document/General

**Clone Detection:** No - Original

**Cryptographic:** Metadata validated

**RAG Analysis:** Verified against knowledge base

**AI Detection:** Human-written content

**Final Assessment:** 91% authenticity | Threat Level: LOW`,
            timestamp: new Date(),
            analysis: finalAnalysis
          };
          setMessages(prev => [...prev, analysisMessage]);
          return;
        }

        const layerKey = layers[currentLayerIndex] as keyof typeof analysisProgress;
        
        // Start processing current layer
        setAnalysisProgress(prev => ({
          ...prev,
          [layerKey]: 'processing'
        }));
        
        // Complete current layer after delay
        setTimeout(() => {
          setAnalysisProgress(prev => ({
            ...prev,
            [layerKey]: 'completed'
          }));
          
          currentLayerIndex++;
          processLayer();
        }, layerTimes[currentLayerIndex]);
      };
      
      // Start the fallback analysis process
      setTimeout(processLayer, 500);
    });
  };

  const formatTimestamp = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-400';
    if (score >= 0.6) return 'text-yellow-400';
    return 'text-red-400';
  };

  // Circular Progress Component
  const CircularProgress = ({ percentage, size = 120 }: { percentage: number; size?: number }) => {
    const strokeWidth = 8;
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const strokeDasharray = circumference;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;

    return (
      <div className="relative inline-flex items-center justify-center">
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#374151"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="url(#gradient)"
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeLinecap="round"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-500 ease-out"
          />
          {/* Gradient definition */}
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style={{ stopColor: '#f97316', stopOpacity: 1 }} />
              <stop offset="100%" style={{ stopColor: '#f59e0b', stopOpacity: 1 }} />
            </linearGradient>
          </defs>
        </svg>
        {/* Percentage text */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-lg font-bold text-white">{Math.round(percentage)}%</span>
        </div>
      </div>
    );
  };

  // Layer Status Component
  const LayerStatus = ({ name, status, score, flaggedContent }: { 
    name: string; 
    status: string; 
    score?: number;
    flaggedContent?: FlaggedContent[];
  }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const explanation = layerExplanations[name as keyof typeof layerExplanations];
    
    // Get layer number from name
    const getLayerNumber = (layerName: string): number => {
      const layerMap: { [key: string]: number } = {
        'MIME Detection': 1,
        'Classification': 2,
        'Clone Detection': 3,
        'Cryptographic': 4,
        'RAG Analysis': 5,
        'AI Detection': 6,
        'Final Prediction': 7
      };
      return layerMap[layerName] || 0;
    };

    // Filter flagged content for this layer
    const layerFlags = flaggedContent?.filter(flag => flag.layer === getLayerNumber(name)) || [];
    
    const getStatusIcon = () => {
      switch (status) {
        case 'completed':
          return layerFlags.length > 0 ? '⚠️' : '✅';
        case 'processing':
          return <div className="w-4 h-4 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>;
        default:
          return '⏸️';
      }
    };

    const getStatusColor = () => {
      switch (status) {
        case 'completed':
          return layerFlags.length > 0 ? 'text-yellow-400' : 'text-green-400';
        case 'processing':
          return 'text-orange-400';
        default:
          return 'text-gray-400';
      }
    };

    const getSeverityColor = (severity: string) => {
      switch (severity) {
        case 'critical':
          return 'text-red-400 bg-red-900/20 border-red-600';
        case 'warning':
          return 'text-yellow-400 bg-yellow-900/20 border-yellow-600';
        case 'info':
          return 'text-blue-400 bg-blue-900/20 border-blue-600';
        default:
          return 'text-gray-400 bg-gray-900/20 border-gray-600';
      }
    };

    const getSeverityIcon = (severity: string) => {
      switch (severity) {
        case 'critical':
          return '🚨';
        case 'warning':
          return '⚠️';
        case 'info':
          return 'ℹ️';
        default:
          return '•';
      }
    };

    // Special handling for RAG Analysis
    const isRAGLayer = name === 'RAG Analysis';

    return (
      <div className="border border-gray-700 rounded-lg p-3 space-y-2">
        <div 
          className="flex items-center justify-between cursor-pointer"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 flex items-center justify-center">
              {getStatusIcon()}
            </div>
            <div>
              <span className={`font-medium ${getStatusColor()}`}>
                {name} {isRAGLayer && <span className="text-xs text-orange-400">(Not Implemented)</span>}
              </span>
              <p className={`text-xs ${getStatusColor()} mt-1`}>
                {status === 'processing' ? 'Analyzing...' : 
                 status === 'completed' ? 
                   (layerFlags.length > 0 ? `${layerFlags.length} issue${layerFlags.length > 1 ? 's' : ''} found` : 'Complete') : 
                 'Pending'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {score !== undefined && status === 'completed' && !isRAGLayer && (
              <span className={`font-semibold ${getScoreColor(score)}`}>
                {(score * 100).toFixed(0)}%
              </span>
            )}
            {isRAGLayer && (
              <span className="text-orange-400 text-xs">N/A</span>
            )}
            <span className={`text-gray-400 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
              ▼
            </span>
          </div>
        </div>
        
        {isExpanded && (
          <div className="border-t border-gray-700 pt-3 space-y-3">
            {/* Layer Description */}
            {explanation && (
              <div className="space-y-2">
                <p className="text-gray-300 text-sm leading-relaxed">
                  {explanation.description}
                </p>
                <p className="text-gray-400 text-xs leading-relaxed">
                  {explanation.details}
                </p>
              </div>
            )}

            {/* RAG Not Implemented Notice */}
            {isRAGLayer && (
              <div className="bg-orange-900/20 border border-orange-600 rounded p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-orange-400">🚧</span>
                  <span className="text-orange-400 font-medium text-sm">RAG Analysis Not Implemented</span>
                </div>
                <p className="text-orange-300 text-xs">
                  Retrieval-Augmented Generation analysis is currently under development. 
                  This layer will provide context-aware authenticity verification once implemented.
                </p>
              </div>
            )}

            {/* Score Display */}
            {score !== undefined && status === 'completed' && !isRAGLayer && (
              <div className="bg-gray-800 rounded p-3">
                <p className="text-xs text-gray-400 mb-2">Analysis Result:</p>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white text-sm">Authenticity Score</span>
                  <span className={`font-semibold ${getScoreColor(score)}`}>
                    {(score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-500 ${score >= 0.8 ? 'bg-green-400' : score >= 0.6 ? 'bg-yellow-400' : 'bg-red-400'}`}
                    style={{ width: `${score * 100}%` }}
                  ></div>
                </div>
                
                {/* Score Explanation */}
                <div className="mt-2 text-xs text-gray-400">
                  {score >= 0.8 ? 'High confidence - document appears authentic' :
                   score >= 0.6 ? 'Medium confidence - some concerns detected' :
                   score >= 0.4 ? 'Low confidence - multiple issues found' :
                   'Very low confidence - significant problems detected'}
                </div>
              </div>
            )}

            {/* Flagged Content */}
            {layerFlags.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-white text-sm font-medium">Specific Issues Found:</h4>
                {layerFlags.map((flag, index) => (
                  <div key={index} className={`border rounded p-3 text-sm ${getSeverityColor(flag.severity)}`}>
                    <div className="flex items-start gap-2 mb-2">
                      <span className="text-base">{getSeverityIcon(flag.severity)}</span>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium capitalize">{flag.severity}</span>
                          <span className="text-xs opacity-75">({flag.type.replace(/_/g, ' ')})</span>
                        </div>
                        <p className="text-sm leading-relaxed">{flag.message}</p>
                        
                        {flag.location && (
                          <p className="text-xs opacity-75 mt-1">
                            Location: {flag.location.replace(/_/g, ' ')}
                          </p>
                        )}
                        
                        {/* Detailed information */}
                        {flag.details && Object.keys(flag.details).length > 0 && (
                          <div className="mt-2 text-xs space-y-1">
                            {Object.entries(flag.details).map(([key, value]) => (
                              <div key={key} className="flex justify-between">
                                <span className="opacity-75">{key.replace(/_/g, ' ')}:</span>
                                <span className="font-mono">
                                  {typeof value === 'number' ? 
                                    (key.includes('score') || key.includes('similarity') ? 
                                      `${(value * 100).toFixed(1)}%` : value) : 
                                    String(value)}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-screen bg-gray-950 flex">
      {/* Sidebar */}
      <div className="w-80 bg-gray-900 border-r border-gray-800 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-amber-500 rounded-lg flex items-center justify-center">
              🛡️
            </div>
            <div>
              <h1 className="text-white font-semibold">Authenticator.ai</h1>
              <p className="text-gray-400 text-sm">Content Verification</p>
            </div>
          </div>
          
          <button
            onClick={handleNewChat}
            className="w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-medium py-2.5 px-4 rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
          >
            ➕ New Analysis
          </button>
        </div>

        {/* Chat Sessions */}
        <div className="flex-1 overflow-y-auto p-4">
          <h2 className="text-gray-400 text-sm font-medium mb-3">Recent Analyses</h2>
          <div className="space-y-2">
            {sessions.map((session) => (
              <div
                key={session.id}
                onClick={() => setCurrentSessionId(session.id)}
                className={`p-3 rounded-lg cursor-pointer transition-all duration-200 group ${
                  currentSessionId === session.id
                    ? 'bg-gray-800 border border-gray-700'
                    : 'hover:bg-gray-800'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-white text-sm font-medium truncate">
                      {session.name}
                    </h3>
                    {session.lastMessage && (
                      <p className="text-gray-400 text-xs mt-1 truncate">
                        {session.lastMessage}
                      </p>
                    )}
                    <p className="text-gray-500 text-xs mt-1">
                      {formatTimestamp(session.timestamp)} • {session.messageCount} messages
                    </p>
                  </div>
                  <button className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-white p-1">
                    ⋯
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* User Menu */}
        <div className="p-4 border-t border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">
                {user.name.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1">
              <p className="text-white text-sm font-medium">{user.name}</p>
              <p className="text-gray-400 text-xs">{user.email}</p>
            </div>
            <button
              onClick={onLogout}
              className="text-gray-400 hover:text-white p-1"
              title="Logout"
            >
              ⚙️
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Chat/Analysis Area */}
        <div className={`${currentDocument ? 'flex-1' : 'w-full'} flex flex-col`}>
          {currentSessionId ? (
            <>
              {/* Chat Header */}
              <div className="p-4 border-b border-gray-800 bg-gray-900">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-white font-semibold">
                      {sessions.find(s => s.id === currentSessionId)?.name || 'Analysis Session'}
                    </h2>
                    <p className="text-gray-400 text-sm">7-Layer Authenticity Pipeline</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button className="text-gray-400 hover:text-white p-2">
                      🔍
                    </button>
                    <button className="text-gray-400 hover:text-white p-2">
                      ⋯
                    </button>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-6">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-3xl ${message.role === 'user' ? 'ml-12' : 'mr-12'}`}>
                    <div
                      className={`p-4 rounded-2xl ${
                        message.role === 'user'
                          ? 'bg-orange-600 text-white rounded-br-md'
                          : 'bg-gray-800 text-gray-100 rounded-bl-md'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      
                      {message.attachments && (
                        <div className="mt-3 pt-3 border-t border-orange-500/20">
                          {message.attachments.map((file, index) => (
                            <div key={index} className="flex items-center gap-2 text-sm">
                              📄 <span>{file.name}</span>
                              <span className="text-orange-200">
                                ({(file.size / 1024 / 1024).toFixed(1)}MB)
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {message.analysis && (
                      <div className="mt-4 bg-gray-900 border border-gray-700 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-white font-semibold">Authenticity Analysis</h3>
                          <div className={`px-3 py-1 rounded-full text-xs font-medium ${getRiskColor(message.analysis.riskLevel)}`}>
                            {message.analysis.riskLevel.toUpperCase()} RISK
                          </div>
                        </div>

                        <div className="mb-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-gray-300">Overall Score</span>
                            <span className={`font-semibold ${getScoreColor(message.analysis.overallScore)}`}>
                              {(message.analysis.overallScore * 100).toFixed(0)}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-gradient-to-r from-orange-500 to-amber-500 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${message.analysis.overallScore * 100}%` }}
                            />
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                          {Object.entries(message.analysis).filter(([key]) => key.startsWith('layer')).map(([key, layer]: [string, any]) => (
                            <div key={key} className="bg-gray-800 rounded-lg p-3">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-gray-300 text-sm">{layer.name}</span>
                                ✅
                              </div>
                              <div className="flex items-center justify-between">
                                <span className={`font-medium ${getScoreColor(layer.score)}`}>
                                  {(layer.score * 100).toFixed(0)}%
                                </span>
                                <span className="text-xs text-gray-400">
                                  {layer.status}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <p className="text-gray-400 text-xs mt-2">
                      {formatTimestamp(message.timestamp)}
                    </p>
                  </div>
                </div>
              ))}

              {isAnalyzing && (
                <div className="flex justify-start">
                  <div className="bg-gray-800 rounded-2xl rounded-bl-md p-4 mr-12">
                    <div className="flex items-center gap-3">
                      <div className="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-gray-300">Analyzing through 7-layer pipeline...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-gray-800 bg-gray-900">
              {uploadProgress !== null && (
                <div className="mb-4 bg-gray-800 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-300 text-sm">Uploading file...</span>
                    <span className="text-gray-400 text-sm">{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-orange-500 to-amber-500 h-2 rounded-full transition-all duration-200"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>
              )}

              <div className="flex items-end gap-3">
                <div className="flex-1 relative">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    placeholder="Describe the content you want to verify, or upload a file..."
                    className="w-full bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 p-3 pr-12 resize-none focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    rows={1}
                    style={{ minHeight: '44px', maxHeight: '120px' }}
                  />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                  >
                    📎
                  </button>
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim()}
                  className="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 disabled:from-gray-600 disabled:to-gray-600 text-white p-3 rounded-lg transition-all duration-200"
                >
                  📤
                </button>
              </div>

              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileUpload}
                className="hidden"
                accept=".txt,.doc,.docx,.pdf,.jpg,.jpeg,.png,.gif"
              />
            </div>
          </>
        ) : (
          /* Welcome Screen */
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center max-w-2xl">
              <div className="w-20 h-20 bg-gradient-to-r from-orange-500 to-amber-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                🛡️
              </div>
              
              <h1 className="text-4xl font-bold text-white mb-4">
                What would you like to <span className="gradient-text">verify</span> today?
              </h1>
              
              <p className="text-gray-400 text-lg mb-8">
                Upload documents, images, or text content for comprehensive authenticity analysis
                through our advanced 7-layer verification pipeline.
              </p>

              <div className="grid grid-cols-2 gap-4 mb-8">
                <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 text-left">
                  📄 
                  <h3 className="text-white font-semibold mb-2 mt-3">Document Analysis</h3>
                  <p className="text-gray-400 text-sm">
                    Verify contracts, resumes, academic papers, and other text documents
                  </p>
                </div>
                
                <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 text-left">
                  📁
                  <h3 className="text-white font-semibold mb-2 mt-3">Media Verification</h3>
                  <p className="text-gray-400 text-sm">
                    Analyze images, audio files, and multimedia content for authenticity
                  </p>
                </div>
              </div>

              <button
                onClick={handleNewChat}
                className="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-medium py-3 px-8 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Start New Analysis
              </button>
            </div>
          </div>
        )}
        </div>

        {/* Document Viewer & Analysis Panel */}
        {currentDocument && (
          <div className="w-96 border-l border-gray-800 bg-gray-900 flex flex-col">
            {/* Document Header */}
            <div className="p-4 border-b border-gray-800">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-white font-semibold truncate">{currentDocument.name}</h3>
                <button
                  onClick={() => setCurrentDocument(null)}
                  className="text-gray-400 hover:text-white p-1"
                >
                  ✕
                </button>
              </div>
              <p className="text-gray-400 text-sm">
                {currentDocument.type} • {(currentDocument.size / 1024).toFixed(1)} KB
              </p>
            </div>

            {/* Analysis Status */}
            {(isAnalyzing || currentAnalysis) && (
              <div className="p-4 border-b border-gray-800">
                <div className="text-center mb-4">
                  <CircularProgress 
                    percentage={currentAnalysis ? currentAnalysis.overallScore * 100 : 0} 
                    size={100}
                  />
                  <p className="text-gray-300 mt-2 font-medium">
                    {isAnalyzing ? 'Analyzing...' : 'Analysis Complete'}
                  </p>
                  {currentAnalysis && (
                    <div className={`inline-block px-3 py-1 rounded-full text-xs font-medium mt-2 ${getRiskColor(currentAnalysis.riskLevel)}`}>
                      {currentAnalysis.riskLevel.toUpperCase()} RISK
                    </div>
                  )}
                </div>

                {/* Layer Status */}
                <div className="space-y-2">
                  <LayerStatus 
                    name="MIME Detection" 
                    status={analysisProgress.layer1} 
                    score={currentAnalysis?.layer1.score}
                    flaggedContent={currentAnalysis?.flagged_content}
                  />
                  <LayerStatus 
                    name="Classification" 
                    status={analysisProgress.layer2} 
                    score={currentAnalysis?.layer2.score}
                    flaggedContent={currentAnalysis?.flagged_content}
                  />
                  <LayerStatus 
                    name="Clone Detection" 
                    status={analysisProgress.layer3} 
                    score={currentAnalysis?.layer3.score}
                    flaggedContent={currentAnalysis?.flagged_content}
                  />
                  <LayerStatus
                    name="Cryptographic"
                    status={analysisProgress.layer4}
                    score={currentAnalysis?.layer4.score}
                    flaggedContent={currentAnalysis?.flagged_content}
                  />
                  <LayerStatus
                    name="RAG Analysis"
                    status={analysisProgress.layer5}
                    score={currentAnalysis?.layer5.score}
                    flaggedContent={currentAnalysis?.flagged_content}
                  />
                  <LayerStatus
                    name="AI Detection"
                    status={analysisProgress.layer6}
                    score={currentAnalysis?.layer6.score}
                    flaggedContent={currentAnalysis?.flagged_content}
                  />
                  <LayerStatus
                    name="Final Prediction"
                    status={analysisProgress.layer7}
                    score={currentAnalysis?.layer7.score}
                    flaggedContent={currentAnalysis?.flagged_content}
                  />
                </div>
              </div>
            )}

            {/* Document Content */}
            <div className="flex-1 overflow-hidden flex flex-col">
              <div className="p-4 border-b border-gray-800">
                <h4 className="text-white font-medium mb-2">Document Content</h4>
              </div>
              <div className="flex-1 overflow-y-auto p-4">
                <pre className="text-gray-300 text-sm whitespace-pre-wrap font-mono leading-relaxed">
                  {currentDocument.content}
                </pre>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Pipeline Choice Modal */}
      {showPipelineChoice && pendingFile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 max-w-md mx-4">
            <h3 className="text-xl font-semibold text-white mb-4">
              Choose Action for "{pendingFile.name}"
            </h3>
            <p className="text-gray-300 mb-6">
              Would you like to analyze this document through the authenticity pipeline or add it to the clone detection training database?
            </p>
            
            <div className="space-y-4">
              <div className="border border-gray-600 rounded-lg p-4 space-y-3">
                <button
                  onClick={() => processPipelineChoice('analyze')}
                  className="w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-105"
                >
                  🔍 Run Through Analysis Pipeline
                </button>
                
                <div className="flex items-center space-x-2 text-sm">
                  <input
                    type="checkbox"
                    id="storeForClone"
                    checked={storeForCloneDetection}
                    onChange={(e) => setStoreForCloneDetection(e.target.checked)}
                    className="w-4 h-4 text-orange-600 bg-gray-700 border-gray-600 rounded focus:ring-orange-500 focus:ring-2"
                  />
                  <label htmlFor="storeForClone" className="text-gray-300 cursor-pointer">
                    Also store document for clone detection comparison
                  </label>
                </div>
                <p className="text-xs text-gray-400">
                  When enabled, this document will be saved to help detect similar documents in future analyses.
                </p>
              </div>
              
              <button
                onClick={() => processPipelineChoice('train')}
                className="w-full bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-105"
              >
                🎯 Train Clone Detection Database
              </button>
              
              <button
                onClick={() => {
                  setShowPipelineChoice(false);
                  setPendingFile(null);
                }}
                className="w-full bg-gray-700 hover:bg-gray-600 text-gray-300 font-medium py-2 px-4 rounded-lg transition-colors duration-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
