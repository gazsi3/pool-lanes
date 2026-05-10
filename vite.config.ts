import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/pool-lanes/",
  server: {
    host: true,       // bind 0.0.0.0 so Docker port mapping works
    port: 5173,
    watch: {
      usePolling: true, // required for inotify-less volume mounts (WSL2/Windows)
      interval: 300,
    },
  },
  build: {
    outDir: "dist",
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
          charts: ["recharts"],
          table: ["@tanstack/react-table"],
        },
      },
    },
  },
});
