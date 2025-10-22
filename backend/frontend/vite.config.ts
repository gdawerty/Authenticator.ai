import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  css: {
    postcss: './postcss.config.js'
  },
  server: {
    proxy: {
      '/docs': {
        target: 'http://127.0.0.1:8000', // Flask backend
        changeOrigin: true,
        secure: false
      }
    }
  }
})
