/**
 * Vitest config of the site side of the league package. Tests run in jsdom.
 * The package has no build step, so the tests read the TSX source as the site build does.
 */
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: { environment: "jsdom", include: ["**/*.test.{ts,tsx}"], exclude: ["node_modules/**"] },
});
