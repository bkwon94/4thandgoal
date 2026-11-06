/**
 * Builds and checks the fixture client of the midseason report: a temp copy of a real client that takes midseason and
 * sim, with the package fixtures in its published season folder. The full check runs it after each real client.
 */
import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { parse, stringify } from "smol-toml";
import { REPO_ROOT, SCHEMA_FILE, valuesSchemaFile } from "./client-build.mjs";

/* The client that the fixture copies. The fixtures hold the real CPC week 8 data, so the names match its weeks. */
const SLUG = "cpc";

/* The package fixtures, by the file name the site reads from the season folder. */
const FIXTURES = {
  "midseason.json": join(REPO_ROOT, "packages", "midseason", "site", "fixtures", "midseason.json"),
  "sim.json": join(REPO_ROOT, "packages", "sim", "site", "fixtures", "sim.json"),
};

/* The packages that the report needs. The fixture client takes them even before the real client does. */
const REPORT_PACKAGES = ["midseason", "sim"];

/* A temp root with the exported schemas and a copy of the client `slug`. The copy takes midseason and sim, and its
   season folder holds both package fixtures. The client build reads it through CLIENT_ROOT, so no file under clients/
   changes. */
export function fixtureRoot(slug = SLUG) {
  const root = mkdtempSync(join(tmpdir(), "midseason-fixture-"));
  const schemas = readdirSync(join(REPO_ROOT, "packages"))
    .map(valuesSchemaFile)
    .filter((path) => existsSync(join(REPO_ROOT, path)));
  for (const path of [SCHEMA_FILE, ...schemas]) {
    mkdirSync(join(root, path, ".."), { recursive: true });
    cpSync(join(REPO_ROOT, path), join(root, path));
  }
  const client = join(root, "clients", slug);
  cpSync(join(REPO_ROOT, "clients", slug), client, { recursive: true });
  const toml = join(client, "client.toml");
  const values = parse(readFileSync(toml, "utf8"));
  values.packages = [...values.packages, ...REPORT_PACKAGES.filter((name) => !values.packages.includes(name))];
  writeFileSync(toml, stringify(values));
  const season = String(JSON.parse(readFileSync(FIXTURES["midseason.json"], "utf8")).season);
  mkdirSync(join(client, "published", season), { recursive: true });
  for (const [name, file] of Object.entries(FIXTURES)) cpSync(file, join(client, "published", season, name));
  return root;
}

/* The steps of the check. The floor runs only the checks of the report and the takeover, because the run of each real
   client already holds the rest of the floor. */
const STEPS = [["build"], ["check:export"], ["check:floor", "-g", "midseason"]];

/* Runs the steps in order and gives the exit status of the first failure, or 0. */
function runSteps(env, season) {
  for (const [script, ...args] of STEPS) {
    console.log(`==> site ${script}: the midseason fixture of ${SLUG}`);
    const run = spawnSync("pnpm", [script, ...args], { stdio: "inherit", env });
    if (run.status !== 0) {
      console.error(`The site ${script} of the midseason fixture failed.`);
      return run.status ?? 1;
    }
    // Each check of the report skips a client with no report page, so a build with no page must fail here.
    if (script === "build" && !existsSync(join("out", "midseason", season, "index.html"))) {
      console.error("The build of the midseason fixture has no report page.");
      return 1;
    }
  }
  return 0;
}

function main() {
  const root = fixtureRoot();
  const season = String(JSON.parse(readFileSync(FIXTURES["midseason.json"], "utf8")).season);
  // process.exit skips a finally block, so the temp root goes first and the exit comes after.
  const status = runSteps({ ...process.env, CLIENT: SLUG, CLIENT_ROOT: root }, season);
  rmSync(root, { recursive: true, force: true });
  process.exit(status);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) main();
