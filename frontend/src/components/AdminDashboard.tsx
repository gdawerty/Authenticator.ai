import React, { useState, useEffect } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  provider: string;
  created_at: string;
  last_login: string | null;
}

interface AnalysisLog {
  id: number;
  user_id: string;
  timestamp: string;
  file_name: string;
  file_type: string;
  analysis_type: string;
  authenticity_score: number;
  ai_detection_score: number;
  domain_classification: any;
  status: string;
}

interface AdminDashboardProps {
  user: any;
  onLogout: () => void;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ user, onLogout }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [logs, setLogs] = useState<AnalysisLog[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'logs'>('overview');
  const [isLoading, setIsLoading] = useState(true);
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      const token = localStorage.getItem('authToken');
      
      // Fetch users
      const usersResponse = await fetch('http://localhost:8000/admin/users', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      // Fetch logs
      const logsResponse = await fetch('http://localhost:8000/admin/logs', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (usersResponse.ok) {
        const usersData = await usersResponse.json();
        setUsers(usersData.users);
        
        // Calculate analytics
        const totalUsers = usersData.users.length;
        const adminUsers = usersData.users.filter((u: User) => u.role === 'admin').length;
        const googleUsers = usersData.users.filter((u: User) => u.provider === 'google').length;
        const microsoftUsers = usersData.users.filter((u: User) => u.provider === 'microsoft').length;
        const localUsers = usersData.users.filter((u: User) => u.provider === 'local').length;
        
        setAnalytics({
          totalUsers,
          adminUsers,
          regularUsers: totalUsers - adminUsers,
          oauthBreakdown: {
            google: googleUsers,
            microsoft: microsoftUsers,
            local: localUsers
          }
        });
      }

      if (logsResponse.ok) {
        const logsData = await logsResponse.json();
        setLogs(logsData.logs);
      }
    } catch (error) {
      console.error('Failed to fetch admin data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString();
  };

  const getScoreColor = (score: number) => {
    if (score < 0.3) return 'text-green-400';
    if (score < 0.7) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getUserNameById = (userId: string) => {
    const foundUser = users.find(u => u.id === userId);
    return foundUser ? foundUser.name : 'Unknown User';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-charcoal-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading admin dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-charcoal-900 text-white">
      {/* Header */}
      <div className="bg-charcoal-800 border-b border-charcoal-700 px-6 py-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Admin Dashboard</h1>
            <p className="text-charcoal-300">System Administration & Monitoring</p>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-charcoal-300">Logged in as: {user.name}</span>
            <button
              onClick={onLogout}
              className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg transition-colors"
            >
              Sign Out
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-charcoal-800 border-b border-charcoal-700">
        <div className="container mx-auto px-6">
          <div className="flex space-x-8">
            {['overview', 'users', 'logs'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`py-4 px-2 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-white text-white'
                    : 'border-transparent text-charcoal-300 hover:text-white hover:border-charcoal-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && analytics && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-charcoal-800 rounded-lg p-6 border border-charcoal-700">
                <h3 className="text-lg font-semibold mb-2">Total Users</h3>
                <p className="text-3xl font-bold text-blue-400">{analytics.totalUsers}</p>
              </div>
              <div className="bg-charcoal-800 rounded-lg p-6 border border-charcoal-700">
                <h3 className="text-lg font-semibold mb-2">Admin Users</h3>
                <p className="text-3xl font-bold text-purple-400">{analytics.adminUsers}</p>
              </div>
              <div className="bg-charcoal-800 rounded-lg p-6 border border-charcoal-700">
                <h3 className="text-lg font-semibold mb-2">Regular Users</h3>
                <p className="text-3xl font-bold text-green-400">{analytics.regularUsers}</p>
              </div>
              <div className="bg-charcoal-800 rounded-lg p-6 border border-charcoal-700">
                <h3 className="text-lg font-semibold mb-2">Total Analyses</h3>
                <p className="text-3xl font-bold text-orange-400">{logs.length}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-charcoal-800 rounded-lg p-6 border border-charcoal-700">
                <h3 className="text-lg font-semibold mb-4">OAuth Provider Breakdown</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span>Google</span>
                    <span className="font-bold text-blue-400">{analytics.oauthBreakdown.google}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Microsoft</span>
                    <span className="font-bold text-green-400">{analytics.oauthBreakdown.microsoft}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Local</span>
                    <span className="font-bold text-purple-400">{analytics.oauthBreakdown.local}</span>
                  </div>
                </div>
              </div>

              <div className="bg-charcoal-800 rounded-lg p-6 border border-charcoal-700">
                <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
                <div className="space-y-2">
                  {logs.slice(-5).reverse().map((log) => (
                    <div key={log.id} className="text-sm text-charcoal-300">
                      <span className="text-white">{getUserNameById(log.user_id)}</span> analyzed{' '}
                      <span className="text-blue-400">{log.file_name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="bg-charcoal-800 rounded-lg border border-charcoal-700">
            <div className="px-6 py-4 border-b border-charcoal-700">
              <h2 className="text-xl font-bold">User Management</h2>
              <p className="text-charcoal-300">All registered users</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-charcoal-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">Role</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">Provider</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">Created</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">Last Login</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-charcoal-700">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-charcoal-700/50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-white">{user.name}</div>
                        <div className="text-sm text-charcoal-400">{user.email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          user.role === 'admin' ? 'bg-purple-600 text-white' : 'bg-blue-600 text-white'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-charcoal-300">
                        {user.provider}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-charcoal-300">
                        {formatDate(user.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-charcoal-300">
                        {formatDate(user.last_login)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && (
          <div className="bg-charcoal-800 rounded-lg border border-charcoal-700">
            <div className="px-6 py-4 border-b border-charcoal-700">
              <h2 className="text-xl font-bold">Analysis Logs</h2>
              <p className="text-charcoal-300">All document analyses across the platform</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-charcoal-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">File</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">Authenticity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-charcoal-300 uppercase tracking-wider">AI Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-charcoal-700">
                  {logs.map((log) => (
                    <tr key={log.id} className="hover:bg-charcoal-700/50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                        {getUserNameById(log.user_id)}
                      </td>
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
                        <span className={`text-sm font-medium ${getScoreColor(log.authenticity_score)}`}>
                          {(log.authenticity_score * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-sm font-medium ${getScoreColor(log.ai_detection_score)}`}>
                          {(log.ai_detection_score * 100).toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
