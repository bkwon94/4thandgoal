/**
 * The steps that the full check runs for one client folder, in order, each with the env it adds.
 * A client with the finder on also builds a second time and runs the grade-bar project, so CI runs each check that exists.
 * The client cpc also runs the trades-closed project on its own build after the Lock.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { parse } from "smol-toml";
import { REPO_ROOT } from "./client-build.mjs";

// The grade-bar project calls the analyzer API, so its export builds against the local API URL.
const LOCAL_API_URL = "http://localhost:8080";

// The time before the CPC Lock that each build of the check uses, as the input BUILD_NOW of the client build. The specs of the
// trade Topics, the Trade block strip, and the Deadline banner open pages that a build after a Lock leaves out. A fixed
// time keeps those pages in the export on every day. It is a test input, never a mock mode.
export const BUILD_NOW = "2026-11-21T09:55:00-05:00";

// The client whose export after the Lock the trades-closed project checks.
const TRADES_CLOSED_CLIENT = "cpc";

export function stepsOfClient(slug) {
  const steps = stepsOfFinder(slug);
  // The script check:trades-closed builds its own export after the Lock, so it runs last and replaces out/.
  if (slug === TRADES_CLOSED_CLIENT) steps.push({ script: "check:trades-closed" });
  return steps;
}

function stepsOfFinder(slug) {
  const toml = parse(readFileSync(join(REPO_ROOT, "clients", slug, "client.toml"), "utf8"));
  const steps = [
    { script: "build", env: { BUILD_NOW } },
    { script: "check:export" },
    { script: "check:floor" },
  ];
  if (toml.values?.analyzer?.finder !== true) return steps;
  // The floor builds without the API URL. Its analyzer-stage tests intercept only calls to hosts other
  // than localhost, so a local API URL in that export sends calls to a port that nothing answers in CI.
  // The grade-bar project needs the local URL, so it gets its own build. It runs while out/ holds that
  // build, because the next build replaces out/.
  steps.push({ script: "build", env: { BUILD_NOW, NEXT_PUBLIC_API_URL: LOCAL_API_URL } });
  steps.push({ script: "check:grade-bar-export" });
  return steps;
}
