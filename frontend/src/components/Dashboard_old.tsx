import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageCircle,
  Upload,
  FileText,
  Settings,
  User,
  Plus,
  Send,
  Paperclip,
  Shield,
  Clock,
  CheckCircle,
  AlertTriangle,
  X,
  Search,
  MoreHorizontal,
  Edit,
  Trash2
} from 'lucide-react';

// Types for the dashboard
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

const Dashboard: React.FC<DashboardProps> = ({ user, onLogout }) => {
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
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
        content: 'I\'ve analyzed your content through our 4-layer authenticity pipeline. Here are the results:',
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

    setUploadProgress(0);
    
    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev === null) return 0;
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => setUploadProgress(null), 1000);
          
          // Add file message
          const fileMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: `Uploaded: ${file.name}`,
            timestamp: new Date(),
            attachments: [{
              name: file.name,
              type: file.type,
              size: file.size
            }]
          };
          setMessages(prev => [...prev, fileMessage]);
          
          // Trigger automatic analysis
          setTimeout(() => {
            const analysisMessage: Message = {
              id: (Date.now() + 1).toString(),
              role: 'assistant',
              content: `I've analyzed "${file.name}" through our authenticity pipeline:`,
              timestamp: new Date(),
              analysis: {
                overallScore: 0.91,
                layer1: { name: 'MIME Detection', score: 0.98, status: 'completed' },
                layer2: { name: 'Classification', score: 0.92, status: 'completed' },
                layer3: { name: 'Clone Detection', score: 0.89, status: 'completed' },
                layer4: { name: 'Cryptographic', score: 0.85, status: 'completed' },
                riskLevel: 'low',
                confidence: 'very_high'
              }
            };
            setMessages(prev => [...prev, analysisMessage]);
          }, 1500);
          
          return prev;
        }
        return prev + 10;
      });
    }, 100);
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

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-400 bg-green-400/10';
      case 'moderate': return 'text-yellow-400 bg-yellow-400/10';
      case 'high': return 'text-red-400 bg-red-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  return (
    <div className="h-screen bg-gray-950 flex">
      {/* Sidebar */}
      <div className="w-80 bg-gray-900 border-r border-gray-800 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-amber-500 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
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
            <Plus className="w-4 h-4" />
            New Analysis
          </button>
        </div>

        {/* Chat Sessions */}
        <div className="flex-1 overflow-y-auto p-4">
          <h2 className="text-gray-400 text-sm font-medium mb-3">Recent Analyses</h2>
          <div className="space-y-2">
            {sessions.map((session) => (
              <motion.div
                key={session.id}
                onClick={() => setCurrentSessionId(session.id)}
                className={`p-3 rounded-lg cursor-pointer transition-all duration-200 group ${
                  currentSessionId === session.id
                    ? 'bg-gray-800 border border-gray-700'
                    : 'hover:bg-gray-800'
                }`}
                whileHover={{ x: 2 }}
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
                    <MoreHorizontal className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
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
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {currentSessionId ? (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b border-gray-800 bg-gray-900">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-white font-semibold">
                    {sessions.find(s => s.id === currentSessionId)?.name || 'Analysis Session'}
                  </h2>
                  <p className="text-gray-400 text-sm">4-Layer Authenticity Pipeline</p>
                </div>
                <div className="flex items-center gap-2">
                  <button className="text-gray-400 hover:text-white p-2">
                    <Search className="w-4 h-4" />
                  </button>
                  <button className="text-gray-400 hover:text-white p-2">
                    <MoreHorizontal className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
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
                                <FileText className="w-4 h-4" />
                                <span>{file.name}</span>
                                <span className="text-orange-200">
                                  ({(file.size / 1024 / 1024).toFixed(1)}MB)
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>

                      {message.analysis && (
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.3 }}
                          className="mt-4 bg-gray-900 border border-gray-700 rounded-xl p-4"
                        >
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
                                  <CheckCircle className="w-4 h-4 text-green-400" />
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
                        </motion.div>
                      )}

                      <p className="text-gray-400 text-xs mt-2">
                        {formatTimestamp(message.timestamp)}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {isAnalyzing && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="bg-gray-800 rounded-2xl rounded-bl-md p-4 mr-12">
                    <div className="flex items-center gap-3">
                      <div className="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-gray-300">Analyzing through 4-layer pipeline...</span>
                    </div>
                  </div>
                </motion.div>
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
                    <Paperclip className="w-4 h-4" />
                  </button>
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim()}
                  className="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 disabled:from-gray-600 disabled:to-gray-600 text-white p-3 rounded-lg transition-all duration-200"
                >
                  <Send className="w-4 h-4" />
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
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center max-w-2xl"
            >
              <div className="w-20 h-20 bg-gradient-to-r from-orange-500 to-amber-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Shield className="w-10 h-10 text-white" />
              </div>
              
              <h1 className="text-4xl font-bold text-white mb-4">
                What would you like to <span className="gradient-text">verify</span> today?
              </h1>
              
              <p className="text-gray-400 text-lg mb-8">
                Upload documents, images, or text content for comprehensive authenticity analysis
                through our advanced 4-layer verification pipeline.
              </p>

              <div className="grid grid-cols-2 gap-4 mb-8">
                <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 text-left">
                  <FileText className="w-8 h-8 text-orange-400 mb-3" />
                  <h3 className="text-white font-semibold mb-2">Document Analysis</h3>
                  <p className="text-gray-400 text-sm">
                    Verify contracts, resumes, academic papers, and other text documents
                  </p>
                </div>
                
                <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 text-left">
                  <Upload className="w-8 h-8 text-blue-400 mb-3" />
                  <h3 className="text-white font-semibold mb-2">Media Verification</h3>
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
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
