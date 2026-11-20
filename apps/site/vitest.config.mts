/**
 * Vitest config. Tests run in jsdom with the same @ alias as the app.
 * The test files under src/, the script tests under scripts/, and the tests of the site side of each package run.
 * The folders of scripts/bun-test-files.mjs run on `bun test` instead, so Vitest skips them.
 */
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";
import { configDefaults, defineConfig } from "vitest/config";
import { BUN_TEST_DIRS } from "./scripts/bun-test-files.mjs";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
  test: {
    environment: "jsdom",
    // Agents run the suite in many worktrees at once. A cap of 2 keeps each run off most of the laptop's cores. CI keeps the default.
    maxWorkers: process.env.CI ? undefined : 2,
    // The packages sit outside the app, so the run takes the repo root as its dir and names each glob from there.
    dir: "../..",
    include: [
      "apps/site/src/**/*.test.{ts,tsx}",
      "apps/site/scripts/**/*.test.mjs",
      "packages/*/site/**/*.test.{ts,tsx}",
    ],
    exclude: [...configDefaults.exclude, ...BUN_TEST_DIRS.map((dir) => `${dir}/**`)],
  },
});
