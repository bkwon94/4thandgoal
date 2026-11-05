/**
 * Checks that out/ holds a byte-identical copy of every file under public/, that each week page holds its text, that
 * each package the client omits is absent, that each page opens dark, and that the pages show the copy, the theme button,
 * and the finder of the client. Run it after pnpm build with the same CLIENT. It exits 1 on a mismatch.
 */
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { ClientBuildError, clientRoot, readClient, readCopy } from "./client-build.mjs";

function filesUnder(dir) {
  return readdirSync(dir, { withFileTypes: true })
    .sort((a, b) => (a.name < b.name ? -1 : 1))
    .flatMap((entry) =>
      entry.isDirectory() ? filesUnder(join(dir, entry.name)) : [join(dir, entry.name)],
    );
}

function fail(message) {
  console.error(`check:export failed: ${message}`);
  process.exit(1);
}

let sources;
try {
  sources = filesUnder("public");
} catch {
  fail("public does not exist");
}

for (const file of sources) {
  const copy = join("out", file.slice("public/".length));
  let bytes;
  try {
    bytes = readFileSync(copy);
  } catch {
    fail(`${copy} is missing`);
  }
  if (!bytes.equals(readFileSync(file))) fail(`${copy} differs from ${file}`);
}
// The reveal starts each section at no opacity, but the text must still be in the static HTML,
// so the page reads with no script and search engines see it. Every team name of the standings must be there.
// React escapes these characters in text, so the check escapes the names the same way.
const escapeHtml = (text) =>
  text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#x27;");

const pages = sources.filter((file) => file.endsWith("/page.json"));
for (const file of pages) {
  const html = join("out", file.slice("public/".length).replace(/page\.json$/, "index.html"));
  let text;
  try {
    text = readFileSync(html, "utf8");
  } catch {
    fail(`${html} is missing`);
  }
  for (const row of JSON.parse(readFileSync(file, "utf8")).table) {
    if (!text.includes(escapeHtml(row.team.name))) fail(`${html} does not contain the team name ${row.team.name}`);
  }
}
// An omitted package must leave no route and no code in the export. Each mark is a route of the package and a text
// that only its client code holds, so a shared page that imports a part of the package fails the check.
const PACKAGE_MARKS = {
  waiver: { route: /(^|\/)waiver\/index\.html$/, text: "War chest" },
  // The movement cell of the rankings table, a client component that the home page chapter of rankings shows too.
  rankings: { route: /^rankings\/index\.html$/, text: "No last week" },
  // The key prefix of the teams store of @cpc/analyzer. The analyzer page and the teams prefetch of the home page both
  // hold it, so the mark finds a home page that still imports a part of the analyzer.
  analyzer: { route: /(^|\/)analyze\/index\.html$/, text: "cpc.teams." },
  // The title of the points line, a client component of @cpc/managers that only the manager page shows.
  managers: { route: /(^|\/)managers\/index\.html$/, text: "Points per week" },
};

if (!process.env.CLIENT) fail("set CLIENT to the client of the build, the same value as pnpm build");
let values;
try {
  values = readClient(clientRoot(process.env), process.env.CLIENT);
} catch (error) {
  if (!(error instanceof ClientBuildError)) throw error;
  fail(error.message);
}
const exported = filesUnder("out");
const omitted = Object.keys(PACKAGE_MARKS).filter((name) => !values.packages.includes(name));
for (const name of omitted) {
  const { route, text } = PACKAGE_MARKS[name];
  const page = exported.find((file) => route.test(file.slice("out/".length)));
  if (page) fail(`${page} is a route of ${name}, which the client ${process.env.CLIENT} omits`);
  const code = exported.find((file) => /\.(js|html)$/.test(file) && readFileSync(file, "utf8").includes(text));
  if (code) fail(`${code} holds the ${name} text "${text}", but the client ${process.env.CLIENT} omits ${name}`);
}
// The marks of the client values: the masthead text of copy.toml on the home page, the dark class on <html> of each
// page and the theme button, because each brand gives both sets and dark is the default (ADR 0024), and the finder
// flag of the analyzer page. The flag sits in the page data of the static HTML, because
// the finder shows only after a reader picks two teams.
const copy = readCopy(clientRoot(process.env), process.env.CLIENT);
const home = readFileSync(join("out", "index.html"), "utf8");
if (!home.includes(escapeHtml(copy.masthead))) fail(`out/index.html does not show the masthead text "${copy.masthead}"`);
const htmlPages = exported.filter((file) => file.endsWith(".html"));
const light = htmlPages.find((file) => !/<html[^>]*\sclass="(?:[^"]*\s)?dark(?:\s[^"]*)?"/.test(readFileSync(file, "utf8")));
if (light) fail(`${light} has no dark class on <html>, so it does not open dark`);
if (!htmlPages.some((file) => readFileSync(file, "utf8").includes("Switch to"))) fail("no page shows the theme button");
let finder = "no analyzer";
if (values.packages.includes("analyzer")) {
  const finderOn = values.values?.analyzer?.finder ?? false;
  const analyze = readFileSync(join("out", "analyze", "index.html"), "utf8");
  if (!analyze.includes(`finderOn\\":${finderOn}`)) fail(`out/analyze/index.html does not set the finder to ${finderOn}`);
  finder = finderOn ? "the finder" : "no finder";
}
console.log(
  `check:export passed: ${sources.length} files are byte-identical; ${pages.length} week pages hold every team name; ` +
    `the client ${process.env.CLIENT} omits ${omitted.join(", ") || "no checked package"}, and the export holds none of it; ` +
    `${htmlPages.length} pages open dark; the pages show "${copy.masthead}", the theme button, and ${finder}.`,
);
