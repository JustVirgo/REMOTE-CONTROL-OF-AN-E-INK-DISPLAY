import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'


export default defineConfig({
  plugins: [vue(), tailwindcss()],
  optimizeDeps: {
    include: ['esptool-js']
  },
  server: {
    host: '0.0.0.0',
    port: 8080,
    proxy: {
      "/api": {
        target: "http://backend:5000", //backend
        changeOrigin: true,
        secure: false
      },
      // Static files (fonts, images)
      '/static': {
        target: 'http://backend:5000', //backend
        changeOrigin: true,
        secure: false,
      },
    }
  },
  build: {
    outDir: 'dist',
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
})
