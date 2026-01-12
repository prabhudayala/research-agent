import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        host: true,
        port: 3000,
        proxy: {
            '/research': {
                target: 'http://research-agent:8000', // Matches K8s service name
                changeOrigin: true,
            }
        }
    }
})
