/**
 * The command pnpm evidence <slug> [AT-<n> ...]: it runs the Playwright project "evidence" for one feature.
 * Playwright takes no free args, so this wrapper passes the slug and the test ids as env values.
 */
import { spawnSync } from "node:child_process";

const [slug, ...ids] = process.argv.slice(2);
if (!slug) {
  console.error("Usage: pnpm evidence <slug> [AT-<n> ...]");
  process.exit(2);
}
const env = { ...process.env, EVIDENCE_SLUG: slug, EVIDENCE_TESTS: ids.join(" ") };
const run = spawnSync("pnpm", ["exec", "playwright", "test", "--project=evidence"], { env, stdio: "inherit" });
process.exit(run.status ?? 1);
