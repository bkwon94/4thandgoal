/**
 * The command pnpm smoke --out <dir> [--steps <file>] [--client <slug>] [--no-api] [<flow name> ...]: it runs the Playwright project "smoke".
 * Playwright takes no free args, so this wrapper passes each option as an env value. No flow name runs each flow of the list.
 */
import { resolve } from "node:path";
import { runProject } from "./run-with-api.mjs";

const usage = "Usage: pnpm smoke --out <dir> [--steps <file>] [--client <slug>] [--no-api] [<flow name> ...]";
const args = process.argv.slice(2);
const options = { out: "", steps: "", client: "cpc", noApi: false };
const names = [];
for (let index = 0; index < args.length; index += 1) {
  // --no-api takes no value: the run starts no API, and its API URL is a port with no API.
  if (args[index] === "--no-api") {
    options.noApi = true;
    continue;
  }
  const flag = args[index].match(/^--(out|steps|client)$/)?.[1];
  if (!flag) {
    names.push(args[index]);
    continue;
  }
  const value = args[(index += 1)];
  if (!value) {
    console.error(usage);
    process.exit(2);
  }
  options[flag] = value;
}
if (!options.out) {
  console.error(usage);
  process.exit(2);
}
// pnpm runs the script in apps/site, so a relative path resolves from the folder of the caller, which INIT_CWD holds.
const from = process.env.INIT_CWD ?? process.cwd();
const out = resolve(from, options.out);
const env = {
  ...process.env,
  SMOKE_OUT: out,
  SMOKE_STEPS: options.steps ? resolve(from, options.steps) : "",
  SMOKE_CLIENT: options.client,
  SMOKE_FLOWS: JSON.stringify(names),
  SMOKE_NO_API: options.noApi ? "1" : "",
};
// The smoke run writes api.log and api.pid of its own API into the smoke folder.
runProject("smoke", env, out);
