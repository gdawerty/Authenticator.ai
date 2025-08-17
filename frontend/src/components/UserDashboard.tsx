import React, { useState, useEffect } from 'react';

interface AnalysisLog {
  id: number;
  timestamp: string;
  file_name: string;
  file_type: string;
  analysis_type: string;
  authenticity_score: number;
  ai_detection_score: number;
  domain_classification: any;
  status: string;
}

interface UserStats {
  total_analyses: number;
  avg_authenticity_score: number;
  avg_ai_detection_score: number;
  most_common_domain: string;
  analysis_history: AnalysisLog[];
}

interface UserDashboardProps {
  user: any;
  onLogout: () => void;
}

const UserDashboard: React.FC<UserDashboardProps> = ({ user, onLogout }) => {
  const [logs, setLogs] = useState<AnalysisLog[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchUserLogs();
  }, [user]);

  const fetchUserLogs = async () => {
    try {
      const response = await fetch(`http://localhost:8001/user/logs/${user.id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setLogs(data.logs);
        
        // Calculate stats
        if (data.logs.length > 0) {
          const totalAnalyses = data.logs.length;
          const avgAuthenticity = data.logs.reduce((sum: number, log: AnalysisLog) => sum + log.authenticity_score, 0) / totalAnalyses;
          const avgAiDetection = data.logs.reduce((sum: number, log: AnalysisLog) => sum + log.ai_detection_score, 0) / totalAnalyses;
          
          const domains = data.logs.map((log: AnalysisLog) => log.domain_classification?.category || 'Unknown');
          const mostCommonDomain = domains.reduce((a: string, b: string, i: number, arr: string[]) =>
            arr.filter(v => v === a).length >= arr.filter(v => v === b).length ? a : b
          );

          setStats({
            total_analyses: totalAnalyses,
            avg_authenticity_score: Math.round(avgAuthenticity * 100) / 100,
            avg_ai_detection_score: Math.round(avgAiDetection * 100) / 100,
            most_common_domain: mostCommonDomain,
            analysis_history: data.logs.slice(-10)
          });
        }
      }
    } catch (error) {
      console.error('Failed to fetch user logs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString();
  };

  const getScoreColor = (score: number) => {
    if (score < 0.3) return 'text-green-400';
    if (score < 0.7) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreBg = (score: number) => {
    if (score < 0.3) return 'bg-green-500';
    if (score < 0.7) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-charcoal-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-charcoal-900 text-white">
      {/* Header */}
      <div className="bg-charcoal-800 border-b border-charcoal-700 px-6 py-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Welcome, {user.name}</h1>
            <p className="text-charcoal-300">Document Analysis Dashboard</p>
          </div>
          <button
            onClick={onLogout}
            className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg transition-colors"
          >
            Sign Out
          </button>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-charcoal-800 rounded-lg p-6 border border-charcoal-700">
              <h3 className="text-lg font-semibold mb-2">Total Analyses</h3>
              <p className="text-3xl font-bold text-blue-400">{stats.total_analyses}</p>
            </div>
            <div className="bg-charcoal-800 rounded-lg p-6 border border-charcoal-700">
              <h3 className="text-lg font-semibold mb-2">Avg Authenticity</h3>
              <p className="text-3xl font-bold text-green-400">{(stats.avg_authenticity_score * 100).toFixed(1)}%</p>
            </div>
            <div className="bg-charcoal-800 rounded-lg p-6 border border-charcoal-700">
              <h3 className="text-lg font-semibold mb-2">Avg AI Detection</h3>
              <p className="text-3xl font-bold text-orange-400">{(stats.avg_ai_detection_score * 100).toFixed(1)}%</p>
            </div>
            <div className="bg-charcoal-800 rounded-lg p-6 border border-charcoal-700">
              <h3 className="text-lg font-semibold mb-2">Most Common Domain</h3>
              <p className="text-xl font-bold text-purple-400">{stats.most_common_domain}</p>
            </div>
          </div>
        )}

        {/* Analysis History */}
        <div className="bg-charcoal-800 rounded-lg border border-charcoal-700">
          <div className="px-6 py-4 border-b border-charcoal-700">
            <h2 className="text-xl font-bold">Analysis History</h2>
            <p className="text-charcoal-300">Your recent document analyses</p>
          </div>

          {logs.length === 0 ? (
            <div className="p-8 text-center text-charcoal-400">
              <svg className="w-12 h-12 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p>No analyses yet. Upload a document to get started!</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-charcoal-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">
                      File
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">
                      Authenticity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">
                      AI Detection
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">
                      Domain
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-charcoal-700">
                  {logs.map((log) => (
                    <tr key={log.id} className="hover:bg-charcoal-700/50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-white">{log.file_name}</div>
                        <div className="text-sm text-charcoal-400">{log.file_type}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-charcoal-300">
                        {formatDate(log.timestamp)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 text-xs font-medium bg-blue-600 text-white rounded-full">
                          {log.analysis_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-16 bg-charcoal-700 rounded-full h-2 mr-2">
                            <div
                              className={`h-2 rounded-full ${getScoreBg(log.authenticity_score)}`}
                              style={{ width: `${log.authenticity_score * 100}%` }}
                            />
                          </div>
                          <span className={`text-sm font-medium ${getScoreColor(log.authenticity_score)}`}>
                            {(log.authenticity_score * 100).toFixed(1)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-16 bg-charcoal-700 rounded-full h-2 mr-2">
                            <div
                              className={`h-2 rounded-full ${getScoreBg(log.ai_detection_score)}`}
                              style={{ width: `${log.ai_detection_score * 100}%` }}
                            />
                          </div>
                          <span className={`text-sm font-medium ${getScoreColor(log.ai_detection_score)}`}>
                            {(log.ai_detection_score * 100).toFixed(1)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-charcoal-300">
                        {log.domain_classification?.category || 'Unknown'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;
