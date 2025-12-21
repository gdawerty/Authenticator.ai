import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  css: {
    postcss: './postcss.config.js'
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // Unified Flask backend
        changeOrigin: true,
        secure: false
      },
      '/auth': {
        target: 'http://127.0.0.1:8000', // Auth routes
        changeOrigin: true,
        secure: false
      },
      '/docs': {
        target: 'http://127.0.0.1:8000', // Documentation
        changeOrigin: true,
        secure: false
      },
      '/health': {
        target: 'http://127.0.0.1:8000', // Health check
        changeOrigin: true,
        secure: false
      }
    }
  }
})
