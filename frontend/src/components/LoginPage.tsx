import React, { useState } from 'react';

interface LoginPageProps {
  onLogin: (user: any) => void;
  onBack?: () => void;
}

const LoginPage = ({ onLogin, onBack }: LoginPageProps) => {
  const [isSignup, setIsSignup] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    confirmPassword: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    if (error) setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      if (isSignup && formData.password !== formData.confirmPassword) {
        setError('Passwords do not match');
        setIsLoading(false);
        return;
      }

      const endpoint = isSignup ? '/auth/signup' : '/auth/login';
      const payload = isSignup 
        ? { email: formData.email, password: formData.password, name: formData.name }
        : { email: formData.email, password: formData.password };

      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      console.log('Login response:', data);

      if (response.ok) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        onLogin(data.user);
      } else {
        setError(data.error || 'Authentication failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOAuthLogin = (provider: string) => {
    window.location.href = `http://localhost:8000/auth/oauth/${provider}`;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#C8C8BF] px-6 py-20">
      <div className="w-full max-w-md">
        {/* Back Button */}
        {onBack && (
          <button
            onClick={onBack}
            className="mb-6 text-[#2a2a2a]/70 hover:text-[#2a2a2a] transition-colors duration-200 flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            <span>Back to Home</span>
          </button>
        )}

        <div className="bg-[#C8C8BF] border-2 border-[#6F8F88]/30 p-8 rounded-2xl shadow-2xl">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-[#6F8F88] rounded-2xl mx-auto mb-4 flex items-center justify-center shadow-lg">
            <span className="text-2xl font-bold text-white">🔒</span>
          </div>
          <h1 className="text-3xl font-bold text-[#2a2a2a] mb-2">
            {isSignup ? 'Create Account' : 'Welcome Back'}
          </h1>
          <p className="text-[#2a2a2a]/70">
            {isSignup ? 'Join Authentia AI' : 'Sign in to your account'}
          </p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {isSignup && (
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-[#2a2a2a] mb-2">
                Full Name
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className="w-full px-4 py-3 bg-white/50 border border-[#6F8F88]/30 rounded-lg text-[#2a2a2a] placeholder-[#2a2a2a]/40 focus:outline-none focus:border-[#6F8F88] focus:ring-2 focus:ring-[#6F8F88]/20"
                placeholder="Enter your full name"
                required={isSignup}
              />
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-[#2a2a2a] mb-2">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className="w-full px-4 py-3 bg-white/50 border border-[#6F8F88]/30 rounded-lg text-[#2a2a2a] placeholder-[#2a2a2a]/40 focus:outline-none focus:border-[#6F8F88] focus:ring-2 focus:ring-[#6F8F88]/20"
              placeholder="Enter your email"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-[#2a2a2a] mb-2">
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              className="w-full px-4 py-3 bg-white/50 border border-[#6F8F88]/30 rounded-lg text-[#2a2a2a] placeholder-[#2a2a2a]/40 focus:outline-none focus:border-[#6F8F88] focus:ring-2 focus:ring-[#6F8F88]/20"
              placeholder="Enter your password"
              required
            />
          </div>

          {isSignup && (
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-[#2a2a2a] mb-2">
                Confirm Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className="w-full px-4 py-3 bg-white/50 border border-[#6F8F88]/30 rounded-lg text-[#2a2a2a] placeholder-[#2a2a2a]/40 focus:outline-none focus:border-[#6F8F88] focus:ring-2 focus:ring-[#6F8F88]/20"
                placeholder="Confirm your password"
                required={isSignup}
              />
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-[#6F8F88] text-white py-3 px-4 rounded-lg font-medium hover:shadow-lg hover:shadow-[#6F8F88]/50 focus:outline-none focus:ring-2 focus:ring-[#6F8F88] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                {isSignup ? 'Creating Account...' : 'Signing In...'}
              </div>
            ) : (
              isSignup ? 'Create Account' : 'Sign In'
            )}
          </button>
        </form>

        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[#6F8F88]/30"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-[#C8C8BF] text-[#2a2a2a]/70">Or continue with</span>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-3">
            <button
              onClick={() => handleOAuthLogin('google')}
              className="w-full inline-flex justify-center py-2 px-4 border border-[#6F8F88]/30 rounded-lg bg-white/30 text-sm font-medium text-[#2a2a2a] hover:bg-white/50 transition-colors"
            >
              <span className="mr-2">🔍</span>
              Google
            </button>
            <button
              onClick={() => handleOAuthLogin('github')}
              className="w-full inline-flex justify-center py-2 px-4 border border-[#6F8F88]/30 rounded-lg bg-white/30 text-sm font-medium text-[#2a2a2a] hover:bg-white/50 transition-colors"
            >
              <span className="mr-2">⚡</span>
              GitHub
            </button>
            <button
              onClick={() => handleOAuthLogin('microsoft')}
              className="w-full inline-flex justify-center py-2 px-4 border border-[#6F8F88]/30 rounded-lg bg-white/30 text-sm font-medium text-[#2a2a2a] hover:bg-white/50 transition-colors"
            >
              <span className="mr-2">🔷</span>
              Microsoft
            </button>
            <button
              onClick={() => handleOAuthLogin('discord')}
              className="w-full inline-flex justify-center py-2 px-4 border border-[#6F8F88]/30 rounded-lg bg-white/30 text-sm font-medium text-[#2a2a2a] hover:bg-white/50 transition-colors"
            >
              <span className="mr-2">🎮</span>
              Discord
            </button>
          </div>
        </div>

        <div className="mt-6 text-center">
          <button
            onClick={() => setIsSignup(!isSignup)}
            className="text-[#6F8F88] hover:text-[#6F8F88]/80 font-medium transition-colors"
          >
            {isSignup ? 'Already have an account? Sign in' : "Don't have an account? Sign up"}
          </button>
        </div>

        <div className="mt-8 pt-6 border-t border-[#6F8F88]/30">
          <div className="text-center">
            <h3 className="text-[#2a2a2a] font-semibold mb-4">🚀 Try Our Features</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="p-3 bg-white/30 rounded-lg border border-[#6F8F88]/20">
                <div className="text-[#6F8F88] font-medium">📄 Document Analysis</div>
                <div className="text-[#2a2a2a]/70 mt-1">AI-powered authenticity detection</div>
              </div>
              <div className="p-3 bg-white/30 rounded-lg border border-[#6F8F88]/20">
                <div className="text-[#6F8F88] font-medium">🔍 Clone Detection</div>
                <div className="text-[#2a2a2a]/70 mt-1">Advanced content verification</div>
              </div>
              <div className="p-3 bg-white/30 rounded-lg border border-[#6F8F88]/20">
                <div className="text-[#6F8F88] font-medium">🔐 Cryptographic</div>
                <div className="text-[#2a2a2a]/70 mt-1">Secure validation methods</div>
              </div>
              <div className="p-3 bg-white/30 rounded-lg border border-[#6F8F88]/20">
                <div className="text-[#6F8F88] font-medium">⚡ Real-time</div>
                <div className="text-[#2a2a2a]/70 mt-1">Instant analysis results</div>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
