import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ command }) => ({
  plugins: [react()],
  base: command === "build" ? "/kelly-taylor-test/" : "/",
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
}));
