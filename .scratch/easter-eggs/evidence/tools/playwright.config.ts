/**
 * The Playwright config of the site evidence of easter-eggs. One worker, because each phase changes the state of one local API.
 * Run it from apps/site: pnpm exec playwright test -c ../../.scratch/easter-eggs/evidence/tools/playwright.config.ts
 */
export default {
  testDir: __dirname,
  testMatch: ["site.spec.ts", "callout.spec.ts"],
  workers: 1,
  reporter: "list",
  timeout: 0,
  use: { browserName: "chromium", navigationTimeout: 30000, actionTimeout: 20000 },
  expect: { timeout: 15000 },
};
