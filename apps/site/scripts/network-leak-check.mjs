/**
 * Checks that one run of the site `bun test` suite sends no request to the live API or to a Fly address.
 * Run it with node scripts/network-leak-check.mjs [<bun test flag or path> ...] from apps/site. It exits 1 on a leak.
 */
import { spawnSync } from "node:child_process";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const SITE = join(fileURLToPath(new URL(".", import.meta.url)), "..");

/* Each sign of a request that left the test process. happy-dom prints "Cross-Origin Request Blocked" for a fetch to
   another origin, and Node prints ECONNREFUSED or ECANCELED for a socket that found no server. 66.241.125.83 and
   2a09:8280:: are the Fly addresses of api.4thandgoal.app. */
const SIGNS = [
  { name: "the live API", pattern: /api\.4thandgoal\.app/ },
  { name: "a Fly address", pattern: /fly\.dev|66\.241\.\d+\.\d+|2a09:8280:/ },
  { name: "Cross-Origin Request Blocked", pattern: /Cross-Origin Request Blocked/ },
  { name: "ECONNREFUSED", pattern: /ECONNREFUSED/ },
  { name: "ECANCELED", pattern: /ECANCELED/ },
];

const run = spawnSync("node", ["scripts/bun-test.mjs", ...process.argv.slice(2)], {
  cwd: SITE,
  encoding: "utf8",
  maxBuffer: 256 * 1024 * 1024,
});
const lines = `${run.stdout}\n${run.stderr}`.split("\n");

// The last lines of the run give the test count, so a reader sees that the suite ran.
console.log(
  lines.filter((line) => /^\s*\d+ (pass|fail|skip)\b|^Ran \d+ tests/.test(line)).join("\n"),
);
console.log(`bun test exit code: ${run.status}`);

/* Bun prints the path of a test file on a line of its own before the output of that file, so the last such line names
   the file that printed each hit. A request can fail after its test ends, so the file is a lead, not a proof. */
const hits = new Map();
let file = "(no file)";
for (const line of lines) {
  const heading = line.match(/^(\S+\.test\.[jt]sx?):$/);
  if (heading) {
    file = heading[1];
    continue;
  }
  for (const sign of SIGNS) {
    if (!sign.pattern.test(line)) continue;
    const key = `${file}: ${sign.name}`;
    hits.set(key, (hits.get(key) ?? 0) + 1);
  }
}
for (const [key, count] of [...hits].sort()) console.log(`LEAK ${key} x${count}`);
if (hits.size > 0) {
  const total = [...hits.values()].reduce((sum, count) => sum + count, 0);
  console.log(`FAIL: ${total} output lines show a request that left the test process.`);
  process.exit(1);
}
console.log(
  `PASS: no output line shows a request to ${SIGNS.map((sign) => sign.name).join(", ")}.`,
);
