/**
 * The evidence run of one feature: it starts its own site server and its own local API, each on a free port, builds each
 * client one time against that API, and takes the shots of its step lists. Run it with pnpm evidence <slug> [AT-<n> ...].
 */
import { test } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { existsSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { buildEnv, loadTests, runRound } from "./evidence";
import { startApi } from "./local-api";
import { serveDir } from "./serve";

// pnpm runs each script of the site in apps/site, so the tracker sits two folders up.
const SCRATCH = join(process.cwd(), "..", "..", ".scratch");
const OUT = join(process.cwd(), "out");
// Each client is a folder under clients/ at the repo root, with its client.toml.
const CLIENTS = join(process.cwd(), "..", "..", "clients");
// The wrapper scripts/evidence.mjs passes the slug and the ids as env values.
const SLUG = process.env.EVIDENCE_SLUG ?? "";
const IDS = (process.env.EVIDENCE_TESTS ?? "").split(/\s+/).filter(Boolean);

// Check every step list when the file loads, so a bad list stops the run before the build and before any shot.
// A client slug with no folder would fail only in its build, minutes in, so the check names the file here.
if (SLUG) {
  for (const { file, clients } of loadTests(SCRATCH, SLUG, IDS)) {
    for (const client of clients) {
      if (!existsSync(join(CLIENTS, client, "client.toml")))
        throw new Error(`${file}: unknown client "${client}", no ${join(CLIENTS, client)}`);
    }
  }
}

test(`the evidence of ${SLUG || "no feature"}`, async ({ browser }) => {
  test.skip(!SLUG, "Run it with pnpm evidence <slug>.");
  // A round takes minutes, and each test logs its own time, so the run has no time limit.
  test.setTimeout(0);
  // The server reads each file per request, so it starts before the first build, and its origin is known before the API
  // starts. Each client builds into the same out/, so one server and one API serve the whole round.
  const server = await serveDir(OUT, 0);
  // The folder of api.log and api.pid of the API of the round. The wrapper names it, so it can stop the API after a signal.
  const API_OUT = process.env.EVIDENCE_API_OUT || mkdtempSync(join(tmpdir(), "evidence-api-"));
  const api = await startApi({ origin: server.url, out: API_OUT }).catch(async (error) => {
    await server.close();
    throw error;
  });
  console.log(`site ${server.url}, API ${api.url}, API log ${join(API_OUT, "api.log")}`);
  try {
    await runRound({
      scratch: SCRATCH,
      slug: SLUG,
      ids: IDS,
      browser,
      serve: async (client) => {
        const start = Date.now();
        // pnpm build runs the prebuild step too, which copies the published weeks of the client into public/.
        // A good build stays quiet. A failed build prints its output in the error, because the guide tells the agent to give Brian the command and its error.
        try {
          execFileSync("pnpm", ["build"], {
            env: buildEnv(client, api.url),
            encoding: "utf8",
            stdio: "pipe",
          });
        } catch (error) {
          const { stdout, stderr } = error as { stdout?: string; stderr?: string };
          throw new Error(`build ${client} failed:\n${stdout ?? ""}${stderr ?? ""}`);
        }
        console.log(`build ${client}: ${((Date.now() - start) / 1000).toFixed(1)} s`);
        // The round closes the server of each client. This one server serves each client, so the finally below closes it.
        return { url: server.url, close: async () => {} };
      },
      log: (line) => console.log(line),
    });
  } finally {
    await api.stop();
    await server.close();
  }
});
