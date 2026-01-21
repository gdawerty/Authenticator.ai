import { useState } from 'react'
import { motion } from 'framer-motion'

interface RegisterProps {
  onRegister: (email: string, username: string, password: string) => Promise<void>
  onSwitchToLogin: () => void
}

export function Register({ onRegister, onSwitchToLogin }: RegisterProps) {
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    setIsLoading(true)

    try {
      await onRegister(email, username, password)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
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
        <p className="text-[#2a2a2a]/70 text-center mb-8">Create a new account</p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-[#1A1A1A] mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-lg bg-white/50 border border-black/10 focus:outline-none focus:ring-2 focus:ring-[#6f8f88] text-[#1A1A1A] placeholder:text-[#2a2a2a]/40"
              placeholder="Enter your email"
            />
          </div>

          <div>
            <label htmlFor="username" className="block text-sm font-medium text-[#1A1A1A] mb-2">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-lg bg-white/50 border border-black/10 focus:outline-none focus:ring-2 focus:ring-[#6f8f88] text-[#1A1A1A] placeholder:text-[#2a2a2a]/40"
              placeholder="Choose a username"
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
              placeholder="Create a password (min 6 characters)"
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-[#1A1A1A] mb-2">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-lg bg-white/50 border border-black/10 focus:outline-none focus:ring-2 focus:ring-[#6f8f88] text-[#1A1A1A] placeholder:text-[#2a2a2a]/40"
              placeholder="Confirm your password"
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
            {isLoading ? 'Creating account...' : 'Sign Up'}
          </motion.button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-[#2a2a2a]/70">
            Already have an account?{' '}
            <button
              onClick={onSwitchToLogin}
              className="text-[#6f8f88] font-medium hover:underline"
            >
              Sign in
            </button>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
