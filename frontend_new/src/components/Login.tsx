import { useState } from 'react'
import { motion } from 'framer-motion'

interface LoginProps {
  onLogin: (username: string, password: string) => Promise<void>
  onSwitchToRegister: () => void
}

export function Login({ onLogin, onSwitchToRegister }: LoginProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await onLogin(username, password)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="h-screen w-screen flex items-center justify-center bg-[#C8C8BF]">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md p-8 backdrop-blur-md bg-white/30 rounded-2xl border border-black/10 shadow-xl"
      >
        <h1 className="text-3xl font-bold text-[#1A1A1A] mb-2 text-center">
          Authentia AI
        </h1>
        <p className="text-[#2a2a2a]/70 text-center mb-8">Sign in to continue</p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-[#1A1A1A] mb-2">
              Username or Email
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-lg bg-white/50 border border-black/10 focus:outline-none focus:ring-2 focus:ring-[#6f8f88] text-[#1A1A1A] placeholder:text-[#2a2a2a]/40"
              placeholder="Enter your username or email"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-[#1A1A1A] mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-lg bg-white/50 border border-black/10 focus:outline-none focus:ring-2 focus:ring-[#6f8f88] text-[#1A1A1A] placeholder:text-[#2a2a2a]/40"
              placeholder="Enter your password"
            />
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="p-3 rounded-lg bg-red-100 border border-red-300 text-red-700 text-sm"
            >
              {error}
            </motion.div>
          )}

          <motion.button
            type="submit"
            disabled={isLoading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full py-3 bg-[#6f8f88] text-white rounded-lg font-medium hover:bg-[#5a7a73] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </motion.button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-[#2a2a2a]/70">
            Don't have an account?{' '}
            <button
              onClick={onSwitchToRegister}
              className="text-[#6f8f88] font-medium hover:underline"
            >
              Sign up
            </button>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
