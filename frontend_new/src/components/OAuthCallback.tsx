import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'

const API_BASE_URL = 'http://localhost:8002/api/v1'

export function OAuthCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const handleOAuthCallback = async () => {
      const token = searchParams.get('token')
      const provider = searchParams.get('provider')

      if (token) {
        try {
          // Fetch user info with the token
          const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })

          if (!response.ok) {
            throw new Error('Failed to fetch user info')
          }

          const user = await response.json()

          // Store the token and user info
          localStorage.setItem('token', token)
          localStorage.setItem('user', JSON.stringify(user))
          localStorage.setItem('oauth_provider', provider || 'unknown')

          // Force a full page reload to ensure App picks up the auth state
          window.location.href = '/'
        } catch (err) {
          console.error('OAuth callback error:', err)
          setError('Authentication failed')
          setTimeout(() => {
            navigate('/login')
          }, 2000)
        }
      } else {
        setError('No authentication token received')
        setTimeout(() => {
          navigate('/login')
        }, 2000)
      }
    }

    handleOAuthCallback()
  }, [searchParams, navigate])

  return (
    <div className="h-screen w-screen flex items-center justify-center bg-[#C8C8BF]">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="text-center p-8 backdrop-blur-md bg-white/30 rounded-2xl border border-black/10 shadow-xl max-w-md"
      >
        {error ? (
          <>
            <div className="w-16 h-16 mx-auto mb-4 bg-red-500 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-[#1A1A1A] mb-2">Authentication Failed</h2>
            <p className="text-[#2a2a2a]/70">{error}</p>
            <p className="text-[#2a2a2a]/50 text-sm mt-2">Redirecting back to login...</p>
          </>
        ) : (
          <>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              className="w-16 h-16 mx-auto mb-4 border-4 border-[#6f8f88]/30 border-t-[#6f8f88] rounded-full"
            />
            <h2 className="text-2xl font-bold text-[#1A1A1A] mb-2">Completing Sign In...</h2>
            <p className="text-[#2a2a2a]/70">Please wait</p>
          </>
        )}
      </motion.div>
    </div>
  )
}
