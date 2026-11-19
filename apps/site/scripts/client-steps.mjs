/**
 * The steps that the full check runs for one client folder, in order, each with the env it adds.
 * A client with the finder on also builds a second time and runs the grade-bar project, so CI runs each check that exists.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { parse } from "smol-toml";
import { REPO_ROOT } from "./client-build.mjs";

// The grade-bar project calls the analyzer API, so its export builds against the local API URL.
const LOCAL_API_URL = "http://localhost:8080";

export function stepsOfClient(slug) {
  const toml = parse(readFileSync(join(REPO_ROOT, "clients", slug, "client.toml"), "utf8"));
  const steps = [{ script: "build" }, { script: "check:export" }, { script: "check:floor" }];
  if (toml.values?.analyzer?.finder !== true) return steps;
  // The floor builds without the API URL. Its analyzer-stage tests intercept only calls to hosts other
  // than localhost, so a local API URL in that export sends calls to a port that nothing answers in CI.
  // The grade-bar project needs the local URL, so it gets its own build. It runs while out/ holds that
  // build, because the next build replaces out/.
  steps.push({ script: "build", env: { NEXT_PUBLIC_API_URL: LOCAL_API_URL } });
  steps.push({ script: "check:grade-bar-export" });
  return steps;
}
