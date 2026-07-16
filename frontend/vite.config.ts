import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0', // Expose outside the container
    proxy: {
      '/api': {
        // Docker: set VITE_API_TARGET=http://backend:8000
        // Local:  falls back to http://localhost:8000
        target: process.env.VITE_API_TARGET ?? 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})

