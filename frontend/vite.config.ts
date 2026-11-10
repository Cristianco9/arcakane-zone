import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

const devPort = Number(process.env.FRONTEND_PORT ?? 8080);
const apiProxyTarget = process.env.VITE_DEV_PROXY_TARGET ?? "http://backend:8000";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: "0.0.0.0",
    port: devPort,
    strictPort: true,
    proxy: {
      // El frontend usa rutas relativas /api/... y Vite las reenvía al
      // backend por la red interna de Docker.
      "/api": {
        target: apiProxyTarget,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
  preview: {
    host: "0.0.0.0",
    port: devPort,
  },
});
