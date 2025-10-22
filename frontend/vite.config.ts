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
        target: 'http://127.0.0.1:8001', // Unified Flask backend with SQL Server
        changeOrigin: true,
        secure: false
      },
      '/auth': {
        target: 'http://127.0.0.1:8001', // Auth routes
        changeOrigin: true,
        secure: false
      },
      '/docs': {
        target: 'http://127.0.0.1:8001', // Documentation
        changeOrigin: true,
        secure: false
      },
      '/health': {
        target: 'http://127.0.0.1:8001', // Health check
        changeOrigin: true,
        secure: false
      }
    }
  }
})
