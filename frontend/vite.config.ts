
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
 
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Toda peticion que empiece con /api se redirige al gateway
      '/api': {
        target: 'http://localhost:80',   // <- gateway Nginx de Docker
        changeOrigin: true,
        
        // Si el gateway espera /api/predict, deja esto comentado
        // rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
