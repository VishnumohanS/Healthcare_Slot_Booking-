import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// envDir points at the project root so one shared .env serves backend and frontend.
// Only variables prefixed with VITE_ are exposed to browser code.
export default defineConfig({
  plugins: [react()],
  envDir: "..",
  server: { port: 5173, strictPort: true },
});
