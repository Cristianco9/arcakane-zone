import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    css: false,
    restoreMocks: true,
  },
  server: {
    host: "0.0.0.0",
    port: Number(process.env.FRONTEND_PORT ?? 8080),
    proxy: {
      "/api": {
        target: process.env.VITE_DEV_PROXY_TARGET ?? "http://backend:8000",
        changeOrigin: true,
      },
    },
  },
});
