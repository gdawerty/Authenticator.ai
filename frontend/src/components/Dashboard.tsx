import React, { useState, useRef } from 'react';

// Types
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  analysis?: AnalysisResult;
  attachments?: File[];
}
interface Session {
  id: string;
  name: string;
  timestamp: Date;
  lastMessage?: string;
  messageCount: number;
}
interface LayerData {
  name: string;
  score?: number;
  status: 'pending' | 'processing' | 'completed' | 'error' | 'not_implemented' | 'skipped';
  explanation?: string;
  details?: any;
  error?: string;
}
interface AnalysisResult {
  overallScore?: number;
  riskLevel?: string;
  confidence?: number | string;
  flagged_content?: any[];
  layer1?: LayerData;
  layer2?: LayerData;
  layer3?: LayerData;
  layer4?: LayerData;
  layer5?: LayerData;
  layer6?: LayerData;
  layer7?: LayerData;
  [k: string]: any;
}

// Utilities
const fmtTime = (d: Date) => {
  const h = Math.floor((Date.now() - d.getTime()) / 3600000);
  return h < 1 ? 'Just now' : h < 24 ? `${h}h ago` : d.toLocaleDateString();
};
const riskBadge = (r?: string) => r?.toLowerCase()==='high' ? 'bg-red-100 text-red-700 border-red-400' : r?.toLowerCase()==='medium' ? 'bg-yellow-100 text-yellow-700 border-yellow-400' : 'bg-green-100 text-green-700 border-green-400';
const scoreColor = (s?: number) => s===undefined? 'text-[#2a2a2a]/50' : s>=0.8? 'text-green-600' : s>=0.6? 'text-yellow-600' : 'text-red-600';

// Layer card component with dropdown
const LayerCard: React.FC<{ layerKey: string; data?: LayerData }> = ({ layerKey, data }) => {
  const [expanded, setExpanded] = useState(false);
  const [explanation, setExplanation] = useState<string>('');
  const [loadingExplanation, setLoadingExplanation] = useState(false);

  const layerNames: Record<string, string> = {
    layer1: 'MIME Detection',
    layer2: 'Classification',
    layer3: 'Clone Detection',
    layer4: 'Cryptographic',
    layer5: 'RAG Analysis',
    layer6: 'AI Detection',
    layer7: 'Final Assessment'
  };

  const fetchExplanation = async () => {
    if (explanation) return;

    setLoadingExplanation(true);
    try {
      const layerNum = layerKey.replace('layer', '');
      const response = await fetch('/api/explanations/layer/' + layerNum, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          layer_result: data || {}
        })
      });

      if (response.ok) {
        const result = await response.json();
        setExplanation(result.explanation || result.data?.explanation || 'No explanation available');
      } else {
        const errorText = await response.text();
        console.error('Explanation error:', errorText);
        setExplanation('Explanation service unavailable - ' + errorText.substring(0, 100));
      }
    } catch (error: any) {
      console.error('Explanation fetch error:', error);
      setExplanation('Failed to load explanation: ' + error.message);
    } finally {
      setLoadingExplanation(false);
    }
  };

  const toggleExpanded = () => {
    if (!expanded && !explanation) {
      fetchExplanation();
    }
    setExpanded(!expanded);
  };

  const score = data?.score;
  const status = data?.status || 'pending';
  const statusColor = status==='completed' ? 'text-green-600' : status==='skipped' ? 'text-yellow-600' : status==='processing' ? 'text-yellow-600' : status==='error' ? 'text-red-600' : 'text-[#2a2a2a]/50';

  return (
    <div className="border border-[#6F8F88]/30 rounded-lg p-3 bg-white/40 hover:bg-white/60 transition-colors">
      <div className="flex items-center justify-between cursor-pointer" onClick={toggleExpanded}>
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span className={`text-sm font-medium ${statusColor} truncate`}>
            {data?.name || layerNames[layerKey] || layerKey}
          </span>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          {score!==undefined && (status==='completed' || status==='skipped' || status==='error') && (
            <span className={`font-semibold text-sm ${scoreColor(score)}`}>
              {(score*100).toFixed(0)}%
            </span>
          )}
          <span className={`text-[#2a2a2a]/70 transition-transform text-xs ${expanded?'rotate-180':''}`}>▾</span>
        </div>
      </div>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-[#6F8F88]/30 space-y-3">
          {/* Score bar */}
          {score!==undefined && (
            <div className="space-y-2">
              <div className="w-full bg-[#b8b8af]/50 h-2 rounded-full overflow-hidden">
                <div
                  className={`h-2 transition-all ${score>=0.8?'bg-green-500':score>=0.6?'bg-yellow-500':'bg-red-500'}`}
                  style={{width:`${Math.min(100,Math.max(0,score*100))}%`}}
                />
              </div>
              <p className="text-xs text-[#2a2a2a]/70">
                {score>=0.8?'High confidence':score>=0.6?'Moderate confidence':score>=0.4?'Low confidence':'Very low confidence'}
              </p>
            </div>
          )}

          {/* Error message */}
          {data?.error && (
            <div className="bg-red-100 border border-red-400 rounded p-2">
              <p className="text-xs text-red-700">{data.error}</p>
            </div>
          )}

          {/* Details */}
          {data?.details && typeof data.details === 'string' && (
            <div className="bg-white/50 border border-[#6F8F88]/20 rounded p-2">
              <p className="text-xs text-[#2a2a2a]">{data.details}</p>
            </div>
          )}

          {/* Groq Explanation */}
          <div className="bg-white/50 border border-[#6F8F88]/20 rounded p-3">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-semibold text-[#6F8F88]">AI Explanation</span>
              {loadingExplanation && <span className="w-3 h-3 border-2 border-[#6F8F88] border-t-transparent rounded-full animate-spin"></span>}
            </div>
            <p className="text-xs text-[#2a2a2a] whitespace-pre-wrap leading-relaxed">
              {loadingExplanation ? 'Loading explanation...' : explanation || data?.explanation || 'Click to load explanation'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

// Auth helpers
const getAuthToken = () => typeof window !== 'undefined' ? (localStorage.getItem('auth_token') || '') : '';

// Dashboard component
const Dashboard: React.FC<{ user:{name:string;email:string}; onLogout:()=>void }> = ({ user, onLogout }) => {
  // Session state
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string|null>(null);
  const [messages, setMessages] = useState<Message[]>([]);

  // Input & file state
  const [inputMessage, setInputMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement|null>(null);
  const [pendingFile, setPendingFile] = useState<File|null>(null);
  const [showPipelineChoice, setShowPipelineChoice] = useState(false);
  const [storeForCloneDetection, setStoreForCloneDetection] = useState(true);
  const [uploadProgress, setUploadProgress] = useState<number|null>(null);

  // Analysis state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentDocument, setCurrentDocument] = useState<File|null>(null);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResult|null>(null);

  // Helpers
  const createSession = () => {
    const id = Date.now().toString();
    const s: Session = { id, name: 'New Analysis', timestamp: new Date(), messageCount: 0 };
    setSessions(prev => [s, ...prev]);
    setCurrentSessionId(id);
    setMessages([]);
  };
  const updateSessionMeta = (last: string) => {
    if(!currentSessionId) return;
    setSessions(prev => prev.map(s => s.id===currentSessionId? { ...s, lastMessage:last, messageCount: messages.length+1 }: s));
  };

  // Backend analysis
  const runBackendAnalysis = async (file: File) => {
    setIsAnalyzing(true);
    setCurrentAnalysis(null);

    try {
      const form = new FormData();
      form.append('file', file);
      if (storeForCloneDetection) form.append('store_for_clone_detection','true');

      const token = getAuthToken();
      const headers: any = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
        headers['X-Auth-Token'] = token;
      }

      const response = await fetch('/api/analyze', {
        method:'POST',
        body:form,
        headers
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Analysis failed: ${errorText}`);
      }

      const data = await response.json();
      console.log('Backend response:', data);

      if (data?.status === 'success' && data?.analysis) {
        const analysis = data.analysis;
        console.log('Layer results:', analysis.layer_results);

        // Map backend response to layer structure
        const layerMap: AnalysisResult = {
          overallScore: analysis.final_prediction?.authenticity_score ?? analysis.summary?.authenticity_score ?? 0,
          riskLevel: analysis.final_prediction?.threat_level || analysis.summary?.threat_level || 'low',
          confidence: analysis.final_prediction?.confidence ?? analysis.summary?.confidence,
          flagged_content: analysis.flagged_content || []
        };

        // Map layer_results to layer1-7
        const layerResults = analysis.layer_results || {};

        layerMap.layer1 = {
          name: 'MIME Detection',
          score: layerResults['1']?.score || layerResults['1']?.mime_type ? 0.95 : undefined,
          status: layerResults['1']?.status || 'completed',
          details: layerResults['1']?.details || `File type: ${layerResults['1']?.mime_type || 'Unknown'}`,
          explanation: layerResults['1']?.explanation
        };

        layerMap.layer2 = {
          name: 'Classification',
          score: layerResults['2']?.score,
          status: layerResults['2']?.status || 'completed',
          details: layerResults['2']?.details || `Category: ${layerResults['2']?.category || 'Unknown'}`,
          explanation: layerResults['2']?.explanation
        };

        layerMap.layer3 = {
          name: 'Clone Detection',
          score: layerResults['3']?.score,
          status: layerResults['3']?.status || 'completed',
          details: layerResults['3']?.details || (layerResults['3']?.is_clone ? 'Clone detected' : 'No clone detected'),
          explanation: layerResults['3']?.explanation
        };

        layerMap.layer4 = {
          name: 'Cryptographic',
          score: layerResults['4']?.score,
          status: layerResults['4']?.status || (layerResults['4']?.error ? 'error' : 'completed'),
          details: layerResults['4']?.details,
          error: layerResults['4']?.error,
          explanation: layerResults['4']?.explanation
        };

        layerMap.layer5 = {
          name: 'RAG Analysis',
          score: layerResults['5']?.score,
          status: layerResults['5']?.status || 'not_implemented',
          details: layerResults['5']?.details || 'RAG analysis will be implemented in future updates',
          explanation: layerResults['5']?.explanation
        };

        // Layer 6: AI Detection - calculate human score from ai_probability
        const aiProb = layerResults['6']?.ai_probability ?? 0;
        const humanProb = 1 - aiProb;

        layerMap.layer6 = {
          name: 'AI Detection',
          score: humanProb, // Human probability (inverse of AI probability)
          status: layerResults['6']?.status || 'completed',
          details: typeof layerResults['6']?.details === 'object'
            ? `${(humanProb*100).toFixed(1)}% human, ${(aiProb*100).toFixed(1)}% AI`
            : layerResults['6']?.details || `Human: ${(humanProb*100).toFixed(1)}%, AI: ${(aiProb*100).toFixed(1)}%`,
          explanation: layerResults['6']?.explanation
        };

        layerMap.layer7 = {
          name: 'Final Assessment',
          score: layerMap.overallScore,
          status: 'completed',
          details: `Risk: ${(layerMap.riskLevel || 'low').toUpperCase()}`,
          explanation: analysis.final_prediction?.explanation
        };

        console.log('Mapped layer data:', layerMap);
        setCurrentAnalysis(layerMap);

        // Create assistant message with analysis
        const analysisMessage: Message = {
          id:(Date.now()+1).toString(),
          role:'assistant',
          content: `Analysis complete for ${file.name}`,
          timestamp: new Date(),
          analysis: layerMap
        };
        setMessages(prev => [...prev, analysisMessage]);
        updateSessionMeta(`Analysis: ${file.name}`);
      } else {
        throw new Error('Unexpected response format');
      }

      setIsAnalyzing(false);
    } catch(err:any){
      console.error('Analysis failed:', err);
      setIsAnalyzing(false);
      setCurrentAnalysis(null);
      const fail: Message = {
        id:Date.now().toString(),
        role:'assistant',
        content:`Analysis failed: ${err.message||'Unknown error'}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, fail]);
      updateSessionMeta('Analysis failed');
    }
  };

  // Clone training
  const runBackendCloneTraining = async (file: File) => {
    try {
      const form = new FormData();
      form.append('file', file);

      const token = getAuthToken();
      const headers: any = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
        headers['X-Auth-Token'] = token;
      }

      const response = await fetch('/api/train-clone', {
        method:'POST',
        body:form,
        headers
      });

      if (!response.ok) {
        throw new Error('Training request failed');
      }

      const data = await response.json();
      const msg = data?.status==='success' || data?.success ? `Clone training stored for "${file.name}"` : `Training response: ${JSON.stringify(data).slice(0,120)}`;
      const m: Message = { id:Date.now().toString(), role:'assistant', content: msg, timestamp:new Date() };
      setMessages(prev => [...prev, m]);
      updateSessionMeta(msg.slice(0,60));
    } catch(err:any){
      const m: Message = { id:Date.now().toString(), role:'assistant', content:`Clone training failed: ${err.message}`, timestamp:new Date() };
      setMessages(prev => [...prev, m]);
      updateSessionMeta('Clone training failed');
    }
  };

  // File upload - ALWAYS show modal
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if(!file) return;
    setPendingFile(file);
    setShowPipelineChoice(true);
    // Reset file input
    e.target.value = '';
  };

  const processPipelineChoice = async (action:'analyze'|'train') => {
    if(!pendingFile) return;
    const file = pendingFile;
    setShowPipelineChoice(false);
    setPendingFile(null);
    if(!currentSessionId) createSession();

    // Simulate upload progress
    setUploadProgress(0);
    const start = performance.now();
    const simulate = () => {
      setUploadProgress(p => {
        if(p===null) return 0;
        const elapsed = performance.now()-start;
        const pct = Math.min(100, Math.round(elapsed/20));
        return pct;
      });
      if(performance.now()-start < 1800 && uploadProgress !== 100) requestAnimationFrame(simulate);
      else setUploadProgress(null);
    };
    requestAnimationFrame(simulate);

    setCurrentDocument(file);
    const userMsg: Message = {
      id:Date.now().toString(),
      role:'user',
      content: action==='analyze'?`Analyze document: ${file.name}`:`Add document to clone training: ${file.name}`,
      timestamp:new Date(),
      attachments:[file]
    };
    setMessages(prev => [...prev, userMsg]);
    updateSessionMeta(userMsg.content.slice(0,60));

    if(action==='analyze') await runBackendAnalysis(file);
    else await runBackendCloneTraining(file);
  };

  // Chat send
  const handleSendMessage = () => {
    if(!inputMessage.trim()) return;
    if(!currentSessionId) createSession();
    const msg: Message = { id:Date.now().toString(), role:'user', content: inputMessage.trim(), timestamp: new Date() };
    setMessages(prev => [...prev, msg]);
    updateSessionMeta(msg.content.slice(0,60));
    setInputMessage('');
  };

  const handleNewChat = () => {
    createSession();
    setCurrentDocument(null);
    setCurrentAnalysis(null);
    setUploadProgress(null);
  };

  return (
    <div className="h-screen w-screen bg-[#C8C8BF] flex overflow-hidden">
      {/* Sidebar */}
      <div className="w-72 bg-[#b8b8af] border-r border-[#6F8F88]/30 flex flex-col flex-shrink-0">
        <div className="p-4 border-b border-[#6F8F88]/30">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-amber-500 rounded-lg flex items-center justify-center">🛡️</div>
            <div>
              <h1 className="text-[#2a2a2a] font-semibold text-sm">Authenticator.ai</h1>
              <p className="text-[#2a2a2a]/70 text-xs">Authenticity Pipeline</p>
            </div>
          </div>
          <button onClick={handleNewChat} className="w-full bg-[#6F8F88] hover:shadow-lg hover:shadow-[#6F8F88]/50 text-white text-sm font-medium py-2 px-3 rounded-lg transition-all">➕ New Analysis</button>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {sessions.map(s => (
            <div key={s.id} onClick={()=>setCurrentSessionId(s.id)} className={`p-2 rounded-md cursor-pointer text-xs ${currentSessionId===s.id?'bg-[#6F8F88]/20 border border-[#6F8F88]/40':'hover:bg-[#6F8F88]/10'}`}>
              <p className="text-[#2a2a2a] font-medium truncate">{s.name}</p>
              {s.lastMessage && <p className="text-[#2a2a2a]/70 truncate">{s.lastMessage}</p>}
              <p className="text-[#2a2a2a]/50 text-[10px] mt-1">{fmtTime(s.timestamp)} • {s.messageCount} msg</p>
            </div>
          ))}
        </div>
        <div className="p-4 border-t border-[#6F8F88]/30 flex items-center gap-3">
          <div className="w-8 h-8 bg-[#6F8F88] rounded-full flex items-center justify-center text-white text-sm font-medium">{user.name.charAt(0).toUpperCase()}</div>
          <div className="flex-1 min-w-0">
            <p className="text-[#2a2a2a] text-xs font-medium truncate">{user.name}</p>
            <p className="text-[#2a2a2a]/70 text-[10px] truncate">{user.email}</p>
          </div>
          <button onClick={onLogout} className="text-[#2a2a2a]/70 hover:text-[#2a2a2a] text-xs">Logout</button>
        </div>
      </div>

      {/* Main area */}
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {currentSessionId ? (
          <>
            {isAnalyzing && <div className="p-2 bg-[#b8b8af] border-b border-[#6F8F88]/30 text-xs text-[#6F8F88] font-medium flex items-center gap-2 flex-shrink-0"><span className="w-3 h-3 border-2 border-[#6F8F88] border-t-transparent rounded-full animate-spin"/>Running pipeline...</div>}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map(m => (
                <div key={m.id} className={`flex ${m.role==='user'?'justify-end':'justify-start'}`}>
                  <div className={`max-w-3xl w-full ${m.role==='user'?'ml-10':'mr-10'}`}>
                    <div className={`p-3 rounded-xl text-sm whitespace-pre-wrap ${m.role==='user'?'bg-[#6F8F88] text-white rounded-br-md':'bg-white/50 border border-[#6F8F88]/20 text-[#2a2a2a] rounded-bl-md'}`}>{m.content}</div>
                    {m.attachments && <div className="mt-2 text-xs text-[#2a2a2a]/70 flex flex-wrap gap-2">{m.attachments.map((f,i)=>(<span key={i} className="px-2 py-1 bg-white/40 border border-[#6F8F88]/20 rounded">📄 {f.name}</span>))}</div>}
                    {m.analysis && (
                      <div className="mt-3 bg-white/40 border border-[#6F8F88]/30 rounded-lg p-4 space-y-4">
                        {/* Overall score */}
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-semibold text-[#2a2a2a]">Overall Authenticity Score</span>
                            <span className={`font-bold text-lg ${scoreColor(m.analysis.overallScore)}`}>
                              {((m.analysis.overallScore||0)*100).toFixed(0)}%
                            </span>
                          </div>
                          <div className="w-full bg-[#b8b8af]/50 rounded-full h-3 overflow-hidden">
                            <div className="bg-[#6F8F88] h-3 transition-all" style={{width:`${(m.analysis.overallScore||0)*100}%`}}/>
                          </div>
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-xs text-[#2a2a2a]/70">Confidence: {typeof m.analysis.confidence === 'number' ? (m.analysis.confidence*100).toFixed(0) : m.analysis.confidence}%</span>
                            <div className={`px-2 py-1 rounded-full text-xs font-medium border ${riskBadge(m.analysis.riskLevel)}`}>
                              {m.analysis.riskLevel?.toUpperCase()} RISK
                            </div>
                          </div>
                        </div>

                        {/* Layer cards grid - responsive */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                          {['layer1','layer2','layer3','layer4','layer5','layer6','layer7'].map(k => (
                            <LayerCard
                              key={k}
                              layerKey={k}
                              data={m.analysis![k] as LayerData}
                            />
                          ))}
                        </div>
                      </div>
                    )}
                    <p className="text-[#2a2a2a]/50 text-[10px] mt-1">{fmtTime(m.timestamp)}</p>
                  </div>
                </div>
              ))}
              {isAnalyzing && <div className="flex justify-start"><div className="bg-white/50 border border-[#6F8F88]/20 rounded-xl p-3 text-xs flex items-center gap-2 text-[#2a2a2a]"><span className="w-4 h-4 border-2 border-[#6F8F88] border-t-transparent rounded-full animate-spin"/>Running multi-layer pipeline...</div></div>}
            </div>
            <div className="p-3 border-t border-[#6F8F88]/30 bg-[#b8b8af] flex-shrink-0">
              {uploadProgress!==null && (
                <div className="mb-3">
                  <div className="flex items-center justify-between text-xs mb-1"><span className="text-[#2a2a2a]">Uploading...</span><span className="text-[#2a2a2a]/70">{uploadProgress}%</span></div>
                  <div className="w-full bg-[#C8C8BF] rounded-full h-2"><div className="bg-[#6F8F88] h-2 rounded-full transition-all" style={{width:`${uploadProgress}%`}}/></div>
                </div>
              )}
              <div className="flex items-end gap-2">
                <div className="flex-1 relative">
                  <textarea value={inputMessage} onChange={e=>setInputMessage(e.target.value)} onKeyDown={e=>{ if(e.key==='Enter'&&!e.shiftKey){ e.preventDefault(); handleSendMessage(); } }} placeholder="Describe content or upload a file..." className="w-full bg-white/50 border border-[#6F8F88]/30 rounded-lg text-[#2a2a2a] placeholder-[#2a2a2a]/40 p-2 pr-10 resize-none focus:outline-none focus:ring-2 focus:ring-[#6F8F88]/20" rows={1} />
                  <button onClick={()=>fileInputRef.current?.click()} className="absolute right-2 top-1/2 -translate-y-1/2 text-[#2a2a2a]/70 hover:text-[#2a2a2a]">📎</button>
                </div>
                <button onClick={handleSendMessage} disabled={!inputMessage.trim()} className="bg-[#6F8F88] disabled:bg-[#6F8F88]/30 text-white px-4 py-2 rounded-lg text-sm hover:shadow-lg hover:shadow-[#6F8F88]/50 transition-all">Send</button>
              </div>
              <input ref={fileInputRef} type="file" onChange={handleFileUpload} className="hidden" accept=".txt,.doc,.docx,.pdf,.jpg,.jpeg,.png,.gif" />
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center px-8">
            <div className="text-center max-w-xl">
              <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-amber-500 rounded-xl flex items-center justify-center mx-auto mb-5">🛡️</div>
              <h1 className="text-3xl font-bold text-[#2a2a2a] mb-4">Verify documents & media authenticity</h1>
              <p className="text-[#2a2a2a]/70 text-sm mb-6">Upload a file to run the multi-layer verification pipeline or build the clone detection knowledge base.</p>
              <button onClick={handleNewChat} className="bg-[#6F8F88] hover:shadow-lg hover:shadow-[#6F8F88]/50 text-white font-medium py-2 px-6 rounded-lg text-sm transition-all">Start</button>
            </div>
          </div>
        )}
      </div>

      {/* Side analysis panel - responsive, only shows on larger screens with current document */}
      {currentDocument && (
        <div className="hidden xl:flex w-80 border-l border-[#6F8F88]/30 bg-[#b8b8af] flex-col min-h-0 flex-shrink-0">
          <div className="p-3 border-b border-[#6F8F88]/30 flex items-center justify-between">
            <h3 className="text-[#2a2a2a] text-xs font-semibold truncate">{currentDocument.name}</h3>
            <button onClick={()=>setCurrentDocument(null)} className="text-[#2a2a2a]/70 hover:text-[#2a2a2a] text-xs">✕</button>
          </div>
          {(isAnalyzing || currentAnalysis) && (
            <div className="p-3 space-y-3 overflow-y-auto">
              <div className="text-center">
                <p className="text-[#2a2a2a] text-xs font-medium">{isAnalyzing?'Analyzing...':'Analysis Complete'}</p>
                {currentAnalysis && <div className={`inline-block px-2 py-1 mt-2 rounded-full text-[10px] font-medium border ${riskBadge(currentAnalysis.riskLevel)}`}>{currentAnalysis.riskLevel?.toUpperCase()} RISK</div>}
              </div>
              <div className="space-y-2">
                {['layer1','layer2','layer3','layer4','layer5','layer6','layer7'].map(k => (
                  <LayerCard key={k} layerKey={k} data={currentAnalysis?.[k] as LayerData} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modal - ALWAYS appears on file upload */}
      {showPipelineChoice && pendingFile && (
        <div className="fixed inset-0 bg-[#2a2a2a]/70 flex items-center justify-center z-50 p-4">
          <div className="bg-[#C8C8BF] border-2 border-[#6F8F88]/30 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-[#2a2a2a] font-semibold mb-3 text-base">Choose action for "{pendingFile.name}"</h3>
            <p className="text-[#2a2a2a]/70 text-sm mb-4">Analyze through authenticity pipeline or store for clone detection training.</p>
            <div className="space-y-3">
              <div className="border border-[#6F8F88]/30 rounded p-3 space-y-2 bg-white/30">
                <button onClick={()=>processPipelineChoice('analyze')} className="w-full bg-[#6F8F88] hover:shadow-lg hover:shadow-[#6F8F88]/50 text-white font-medium py-2.5 rounded text-sm transition-all">🔍 Run Analysis Pipeline</button>
                <label className="flex items-center gap-2 text-xs text-[#2a2a2a]">
                  <input type="checkbox" checked={storeForCloneDetection} onChange={e=>setStoreForCloneDetection(e.target.checked)} className="w-4 h-4"/>
                  Also store for clone detection comparisons
                </label>
              </div>
              <button onClick={()=>processPipelineChoice('train')} className="w-full bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white font-medium py-2.5 rounded text-sm transition-all hover:shadow-lg">🎯 Train Clone Detection Database</button>
              <button onClick={()=>{setShowPipelineChoice(false); setPendingFile(null);}} className="w-full bg-white/50 hover:bg-white/70 border border-[#6F8F88]/20 text-[#2a2a2a] py-2.5 rounded text-sm transition-all">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
