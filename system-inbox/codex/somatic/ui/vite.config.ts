import { resolve } from "node:path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  publicDir: false,
  server: {
    port: 3000,
    proxy: {
      "/api": "http://127.0.0.1:8765",
      "/fonts": "http://127.0.0.1:8765",
      "/favicon.svg": "http://127.0.0.1:8765",
      "/manifest.webmanifest": "http://127.0.0.1:8765",
    },
  },
  esbuild: {
    keepNames: true,
  },
  build: {
    outDir: resolve(__dirname, "../somatic/bridge/static"),
    emptyOutDir: false,
    cssCodeSplit: false,
    modulePreload: false,
    sourcemap: false,
    assetsInlineLimit: 0,
    rollupOptions: {
      input: resolve(__dirname, "src/main.tsx"),
      output: {
        format: "iife",
        name: "SomaticApp",
        inlineDynamicImports: true,
        entryFileNames: "app.js",
        chunkFileNames: "app.js",
        assetFileNames: (asset) => {
          if (asset.name && asset.name.endsWith(".css")) return "styles.css";
          return "assets/[name][extname]";
        },
      },
    },
  },
});
