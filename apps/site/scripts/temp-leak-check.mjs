/**
 * Checks that one run of the site `bun test` suite leaves no temp folder behind, for each `mkdtemp` prefix of a site test.
 * Run it with node scripts/temp-leak-check.mjs [<bun test flag or path> ...] from apps/site. It exits 1 on a leak.
 */
import { spawnSync } from "node:child_process";
import { mkdirSync, readdirSync, readFileSync, rmSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const SITE = join(fileURLToPath(new URL(".", import.meta.url)), "..");

/* The run sets TMPDIR to an empty folder of its own, so `os.tmpdir()` of each test points there. Other sessions make
   entries in the macOS temp folder at the same time, so a count there can grow with no leak of this run. The folder is
   under the ignored test-results/ folder of the site, and the check removes it at the end. */
const temp = join(SITE, "test-results", `temp-leak-${process.pid}`);
rmSync(temp, { recursive: true, force: true });
mkdirSync(temp, { recursive: true });

// The prefix of each `mkdtemp` call of a site test, such as "week-data-", read from each source file of the suite.
function sitePrefixes() {
  const listed = spawnSync("git", ["ls-files", "src", "scripts", "test", "../../packages"], {
    cwd: SITE,
    encoding: "utf8",
  });
  const prefixes = new Set();
  for (const file of listed.stdout.split("\n")) {
    if (!/\.(m?[jt]sx?)$/.test(file) || file.endsWith("temp-leak-check.mjs")) continue;
    const text = readFileSync(join(SITE, file), "utf8");
    for (const match of text.matchAll(/mkdtemp(?:Sync)?\(\s*join\(\s*tmpdir\(\),\s*"([^"]+)"/g)) {
      prefixes.add(match[1]);
    }
  }
  return [...prefixes].sort();
}

function counts(prefixes) {
  const names = readdirSync(temp);
  return Object.fromEntries(
    prefixes.map((prefix) => [prefix, names.filter((name) => name.startsWith(prefix)).length]),
  );
}

const prefixes = sitePrefixes();
const before = counts(prefixes);
const run = spawnSync("node", ["scripts/bun-test.mjs", ...process.argv.slice(2)], {
  cwd: SITE,
  env: { ...process.env, TMPDIR: temp },
  encoding: "utf8",
});
const after = counts(prefixes);
rmSync(temp, { recursive: true, force: true });

// The last lines of the run give the test count, so a reader sees that the suite ran.
const summary = `${run.stdout}\n${run.stderr}`
  .split("\n")
  .filter((line) => /^\s*\d+ (pass|fail|skip)\b|^Ran \d+ tests/.test(line));
console.log(summary.join("\n"));
console.log(`bun test exit code: ${run.status}`);

const grew = prefixes.filter((prefix) => after[prefix] > before[prefix]);
for (const prefix of prefixes) {
  console.log(
    `${grew.includes(prefix) ? "LEAK" : "ok  "} ${prefix}: ${before[prefix]} -> ${after[prefix]}`,
  );
}
if (grew.length > 0) {
  console.log(`FAIL: ${grew.length} of ${prefixes.length} prefixes left temp folders behind.`);
  process.exit(1);
}
console.log(`PASS: 0 of ${prefixes.length} prefixes left temp folders behind.`);
