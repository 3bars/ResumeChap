import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The backend serves the built frontend from the same origin in production.
// During development we proxy /api to the FastAPI server on port 8000.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
  },
})
