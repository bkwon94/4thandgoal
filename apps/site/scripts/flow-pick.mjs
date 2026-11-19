/**
 * The flow pick of the verify skill: the globs of the diff since the merge base pick the flows of the flow list.
 * Run it with pnpm pick [--base <ref>] [<file> ...]. It prints one picked flow per line, or why it picks none.
 */
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(fileURLToPath(new URL(".", import.meta.url)), "..", "..", "..");
export const FLOW_LIST = join(ROOT, ".claude", "skills", "verify", "flows.json");

/*
 * The shared parts of the site. A change to one of them can break each page, so it picks each flow.
 * The smoke run and the flow list are shared too, because a change to them changes each flow.
 */
export const SHARED_GLOBS = [
  "packages/design/site/**",
  "packages/league/site/**",
  "apps/site/src/app/layout.tsx",
  "apps/site/src/app/globals.css",
  "apps/site/src/app/fonts/**",
  "apps/site/src/app/shell-props.ts",
  "apps/site/src/app/viewport.ts",
  "apps/site/src/lib/**",
  "apps/site/scripts/client-build.mjs",
  "apps/site/next.config.*",
  "apps/site/package.json",
  "pnpm-lock.yaml",
  "apps/site/e2e/evidence.ts",
  "apps/site/e2e/floor.ts",
  "apps/site/e2e/smoke.ts",
  "apps/site/e2e/smoke.spec.ts",
  "apps/site/e2e/local-api.ts",
  ".claude/skills/verify/**",
];

/* The folders of the pipeline. A diff of these only picks no flow, because the base and head rebuild covers it. */
const PIPELINE_GLOBS = ["apps/pipeline/**", "packages/*/python/**"];

/* A glob as a RegExp: "**" matches any run of folders, "*" matches within one name, and each other character matches itself. */
function globRegExp(glob) {
  let source = "";
  for (let index = 0; index < glob.length; index += 1) {
    if (glob.startsWith("**/", index)) {
      source += "(?:.*/)?";
      index += 2;
    } else if (glob.startsWith("**", index)) {
      source += ".*";
      index += 1;
    } else if (glob[index] === "*") {
      source += "[^/]*";
    } else {
      source += glob[index].replace(/[.+?^${}()|[\]\\]/g, "\\$&");
    }
  }
  return new RegExp(`^${source}$`);
}

const matchesAny = (file, globs) => globs.some((glob) => globRegExp(glob).test(file));

/* The name, the route, and the globs of each flow of the flow list. The smoke run checks the rest of each flow. */
export function readFlowGlobs(file) {
  return JSON.parse(readFileSync(file, "utf8")).map(({ name, route, globs }) => ({ name, route, globs }));
}

/*
 * Picks the flows of a diff, in the order of the flow list. A file of a shared part picks each flow.
 * The result keeps whether the diff touches the pipeline only, so the output can say why it picks no flow.
 */
export function pickFlows(flows, files) {
  const shared = files.some((file) => matchesAny(file, SHARED_GLOBS));
  const picked = flows.filter((flow) => shared || files.some((file) => matchesAny(file, flow.globs)));
  const pipelineOnly = files.length > 0 && files.every((file) => matchesAny(file, PIPELINE_GLOBS));
  return { flows: picked.map((flow) => flow.name), pipelineOnly };
}

/* The output of the pick: one flow name per line, or one line that says why the pick is empty. */
export function describePick(pick) {
  if (pick.flows.length > 0) return pick.flows.join("\n");
  if (pick.pipelineOnly) return "No flow: the diff touches the pipeline only, and the base and head rebuild covers it.";
  return "No flow: no file of the diff matches a glob of the flow list.";
}

/* The files of the diff since the merge base of the ref and HEAD: the commits, the changes of the worktree, and the new files. */
export function diffFiles(base) {
  const git = (...args) => execFileSync("git", args, { cwd: ROOT, encoding: "utf8" }).split("\n").filter(Boolean);
  const [mergeBase] = git("merge-base", base, "HEAD");
  return [...new Set([...git("diff", "--name-only", mergeBase), ...git("ls-files", "--others", "--exclude-standard")])];
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  const at = args.indexOf("--base");
  const base = at === -1 ? "main" : args[at + 1];
  if (!base) {
    console.error("Usage: pnpm pick [--base <ref>] [<file> ...]");
    process.exit(2);
  }
  // Each file named after the options stands in for the diff, so a pick of one file needs no branch.
  const named = args.filter((_, index) => at === -1 || (index !== at && index !== at + 1));
  console.log(describePick(pickFlows(readFlowGlobs(FLOW_LIST), named.length > 0 ? named : diffFiles(base))));
}
