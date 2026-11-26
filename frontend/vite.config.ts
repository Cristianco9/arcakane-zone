import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

const devPort = Number(process.env.FRONTEND_PORT ?? 5173);
const apiProxyTarget =
  process.env.VITE_DEV_PROXY_TARGET ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: "0.0.0.0",
    port: devPort,
    strictPort: true,
    proxy: {
      // Conserva el prefijo /api; la API versionada vive en /api/v1.
      "/api": {
        target: apiProxyTarget,
        changeOrigin: true,
        // El backend con SECURE_SSL_REDIRECT=True solo confía en proxies
        // que marcan el esquema original, igual que Nginx en producción.
        headers: { "X-Forwarded-Proto": "https" },
      },
    },
  },
  preview: {
    host: "0.0.0.0",
    port: devPort,
    strictPort: true,
  },
});
