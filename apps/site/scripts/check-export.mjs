/**
 * Checks that out/ holds a byte-identical copy of every file under public/, and that each week page holds its text.
 * Run it after pnpm build. It exits 1 and names the first mismatch.
 */
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

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
console.log(`check:export passed: ${sources.length} files are byte-identical; ${pages.length} week pages hold every team name.`);
