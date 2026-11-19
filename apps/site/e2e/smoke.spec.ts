/**
 * The smoke run of the verify skill: it builds one client against the local API, serves its export, and runs the flows.
 * Run it with pnpm smoke --out <dir> [<flow name> ...], with make -C apps/api api-evidence up first.
 */
import { test } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { join } from "node:path";
import { buildEnv, EVIDENCE_PORT } from "./evidence";
import { serveDir } from "./serve";
import { addSteps, readFlows, routeOf, runSmoke } from "./smoke";

// pnpm runs each script of the site in apps/site, so the repo root sits two folders up.
const ROOT = join(process.cwd(), "..", "..");
const FLOWS = join(ROOT, ".claude", "skills", "verify", "flows.json");
// The wrapper scripts/smoke.mjs passes each option as an env value.
const OUT = process.env.SMOKE_OUT ?? "";
const STEPS = process.env.SMOKE_STEPS ?? "";
const CLIENT = process.env.SMOKE_CLIENT || "cpc";
const NAMES: string[] = JSON.parse(process.env.SMOKE_FLOWS || "[]");

test(`the smoke run of ${CLIENT}`, async () => {
  test.skip(!OUT, "Run it with pnpm smoke --out <dir>.");
  // A run takes minutes, and the log has the time of each flow, so the run has no time limit.
  test.setTimeout(0);
  // Check the flow list, the names, and the added steps before the build, so a bad list stops the run in seconds.
  const all = readFlows(FLOWS);
  for (const name of NAMES) {
    if (!all.some((flow) => flow.name === name)) throw new Error(`${FLOWS}: no flow is named "${name}"`);
  }
  const picked = NAMES.length > 0 ? all.filter((flow) => NAMES.includes(flow.name)) : all;
  const flows = (STEPS ? addSteps(picked, STEPS) : picked).map((flow) => ({
    ...flow,
    route: routeOf(flow.route, join(ROOT, "clients", CLIENT, "published")),
  }));
  const start = Date.now();
  // pnpm build runs the prebuild step too, which copies the published weeks of the client into public/.
  try {
    execFileSync("pnpm", ["build"], { env: buildEnv(CLIENT), encoding: "utf8", stdio: "pipe" });
  } catch (error) {
    const { stdout, stderr } = error as { stdout?: string; stderr?: string };
    throw new Error(`build ${CLIENT} failed:\n${stdout ?? ""}${stderr ?? ""}`);
  }
  console.log(`build ${CLIENT}: ${((Date.now() - start) / 1000).toFixed(1)} s`);
  // The fixed port of the evidence server, because the local API allows only its origin.
  const server = await serveDir(join(process.cwd(), "out"), EVIDENCE_PORT);
  try {
    const { failures } = await runSmoke({ flows, url: server.url, out: OUT, log: (line) => console.log(line) });
    if (failures.length > 0) throw new Error(`The smoke run is red:\n${failures.join("\n")}`);
  } finally {
    await server.close();
  }
});
