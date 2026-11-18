/**
 * The command pnpm smoke --out <dir> [--steps <file>] [--client <slug>] [<flow name> ...]: it runs the Playwright project "smoke".
 * Playwright takes no free args, so this wrapper passes each option as an env value. No flow name runs each flow of the list.
 */
import { spawnSync } from "node:child_process";
import { resolve } from "node:path";

const usage = "Usage: pnpm smoke --out <dir> [--steps <file>] [--client <slug>] [<flow name> ...]";
const args = process.argv.slice(2);
const options = { out: "", steps: "", client: "cpc" };
const names = [];
for (let index = 0; index < args.length; index += 1) {
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
const env = {
  ...process.env,
  SMOKE_OUT: resolve(from, options.out),
  SMOKE_STEPS: options.steps ? resolve(from, options.steps) : "",
  SMOKE_CLIENT: options.client,
  SMOKE_FLOWS: JSON.stringify(names),
};
const run = spawnSync("pnpm", ["exec", "playwright", "test", "--project=smoke"], { env, stdio: "inherit" });
process.exit(run.status ?? 1);
