/**
 * The steps that the full check runs for one client folder, in order, each with the env it adds.
 * A client with the finder on also runs the grade-bar project, so CI runs each check that exists.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { parse } from "smol-toml";
import { REPO_ROOT } from "./client-build.mjs";

// The grade-bar project calls the analyzer API, so the finder export builds against the local API URL.
const LOCAL_API_URL = "http://localhost:8080";

export function stepsOfClient(slug) {
  const toml = parse(readFileSync(join(REPO_ROOT, "clients", slug, "client.toml"), "utf8"));
  const steps = [{ script: "build" }, { script: "check:export" }, { script: "check:floor" }];
  if (toml.values?.analyzer?.finder !== true) return steps;
  steps[0].env = { NEXT_PUBLIC_API_URL: LOCAL_API_URL };
  // The grade-bar project runs while out/ holds this client, because the next build replaces out/.
  steps.push({ script: "check:grade-bar-export" });
  return steps;
}
