/**
 * The command pnpm evidence <slug> [AT-<n> ...]: it runs the Playwright project "evidence" for one feature.
 * Playwright takes no free args, so this wrapper passes the slug and the test ids as env values.
 */
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { runProject } from "./run-with-api.mjs";

const [slug, ...ids] = process.argv.slice(2);
if (!slug) {
  console.error("Usage: pnpm evidence <slug> [AT-<n> ...]");
  process.exit(2);
}
// The round writes api.log and api.pid of its own API into a temp folder, and the spec prints the path of the log.
const apiOut = mkdtempSync(join(tmpdir(), "evidence-api-"));
const env = { ...process.env, EVIDENCE_SLUG: slug, EVIDENCE_TESTS: ids.join(" "), EVIDENCE_API_OUT: apiOut };
runProject("evidence", env, apiOut);
