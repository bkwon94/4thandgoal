/**
 * Holds each package folder to the rule of ADR 0006: a README of under 25 lines with the headings Knows, Ports, and Does not do.
 * A package folder is each folder directly under src/components/ and src/lib/, plus src/lib/ and src/hooks/. No tracked CLAUDE.md sits below the root.
 */
import { execFileSync } from "node:child_process";
import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, join, relative } from "node:path";
import { describe, expect, it } from "vitest";
import { type Offense, report } from "./rule-report";

const ROOT = process.cwd();
const SRC = join(ROOT, "src");

/* The title, then the three headings in this order. The title text is free. */
const HEADINGS = ["## Knows", "## Ports", "## Does not do"];
const MAX_LINES = 24;

const RULE = "each package folder holds a README of under 25 lines with the headings Knows, Ports, and Does not do";
const CLAUDE_MD_RULE = "no CLAUDE.md sits below the repo root";
const ADR = "docs/adr/0006-the-rules-are-checks.md";

function subfolders(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => join(dir, entry.name));
}

/* The rule finds the folders and holds no list, so a new folder needs a README on its first day. */
function packageFolders(): string[] {
  const components = join(SRC, "components");
  const lib = join(SRC, "lib");
  return [...subfolders(components), lib, ...subfolders(lib), join(SRC, "hooks")];
}

/* The source is null when the folder holds no README. */
function readFolder(dir: string): { path: string; source: string | null } {
  const file = join(dir, "README.md");
  return { path: relative(ROOT, file), source: existsSync(file) ? readFileSync(file, "utf8") : null };
}

/* The rule takes the path and the source apart from the disk, so a test can run it on one string. */
function offenses(path: string, source: string | null): Offense[] {
  const at = { path, line: 1, rule: RULE, adr: ADR };
  if (source === null) {
    return [
      {
        ...at,
        ruleId: "readme/missing",
        what: `${path.slice(0, -"/README.md".length)} holds no README.md.`,
        fix: "add a README.md with a one-line title and the headings Knows, Ports, and Does not do.",
      },
    ];
  }
  const found: Offense[] = [];
  const lines = source.replace(/\n$/, "").split("\n");
  const headings = lines.filter((line) => line.startsWith("#"));
  const titled = headings.length > 0 && headings[0].startsWith("# ");
  if (!titled || headings.slice(1).join("\n") !== HEADINGS.join("\n")) {
    found.push({
      ...at,
      ruleId: "readme/headings",
      what: `${basename(path)} has the headings ${headings.join(", ") || "none"}.`,
      fix: "write a one-line title, then exactly ## Knows, ## Ports, and ## Does not do, in that order.",
    });
  }
  if (lines.length > MAX_LINES) {
    found.push({
      ...at,
      line: MAX_LINES + 1,
      ruleId: "readme/length",
      what: `${basename(path)} has ${lines.length} lines.`,
      fix: "cut the README to 24 lines or fewer, and move the detail into the header comments of the files.",
    });
  }
  return found;
}

/* The paths come from git ls-files, so a CLAUDE.md in node_modules or in an ignored folder does not count. */
function claudeMdOffenses(paths: string[]): Offense[] {
  return paths
    .filter((path) => basename(path) === "CLAUDE.md" && path !== "CLAUDE.md")
    .map((path) => ({
      path,
      line: 1,
      ruleId: "readme/no-claude-md",
      what: `${path} is a tracked CLAUDE.md below the root.`,
      rule: CLAUDE_MD_RULE,
      adr: ADR,
      fix: "move the text into the README.md of the folder and delete the CLAUDE.md.",
    }));
}

function trackedFiles(): string[] {
  return execFileSync("git", ["ls-files"], { cwd: ROOT, encoding: "utf8" }).split("\n").filter(Boolean);
}

describe("the readme rule", () => {
  it("finds the package folders", () => {
    // An empty list would pass with no folder read.
    const paths = packageFolders().map((dir) => relative(ROOT, dir));
    expect(paths).toEqual(expect.arrayContaining(["src/components/ui", "src/lib", "src/lib/schemas", "src/hooks"]));
  });

  it("finds a README with the three headings and under 25 lines in each package folder", () => {
    const found = packageFolders()
      .map(readFolder)
      .flatMap(({ path, source }) => offenses(path, source));
    if (found.length > 0) throw new Error(report(found));
  });

  it("finds no tracked CLAUDE.md below the root", () => {
    const paths = trackedFiles();
    // An empty list would pass with no git read.
    expect(paths).toContain("CLAUDE.md");
    const found = claudeMdOffenses(paths);
    if (found.length > 0) throw new Error(report(found));
  });

  it("finds one offense in a README of 25 lines", () => {
    const source = ["# lib", ...HEADINGS, ...Array(21).fill("A line.")].join("\n") + "\n";
    const found = offenses("src/lib/README.md", source);
    expect(found.map(({ ruleId, line }) => ({ ruleId, line }))).toEqual([{ ruleId: "readme/length", line: 25 }]);
  });

  it("finds one offense in a CLAUDE.md below the root", () => {
    const found = claudeMdOffenses(["CLAUDE.md", "src/lib/CLAUDE.md", ".scratch/notes-on-CLAUDE.md"]);
    expect(found.map(({ path, ruleId }) => ({ path, ruleId }))).toEqual([{ path: "src/lib/CLAUDE.md", ruleId: "readme/no-claude-md" }]);
  });

  it("finds one offense in a folder on disk with one source file and no README", () => {
    // The folder goes through the same disk path as the real tree, so a break in the read also fails here.
    const dir = mkdtempSync(join(tmpdir(), "readme-rule-"));
    try {
      writeFileSync(join(dir, "standings.tsx"), "export const a = 1;\n");
      const { path, source } = readFolder(dir);
      expect(offenses(path, source).map(({ ruleId }) => ruleId)).toEqual(["readme/missing"]);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("finds one offense in a README on disk with the headings out of order", () => {
    const dir = mkdtempSync(join(tmpdir(), "readme-rule-"));
    try {
      writeFileSync(join(dir, "README.md"), "# week\n\n## Ports\n\nNone.\n\n## Knows\n\n## Does not do\n");
      const { path, source } = readFolder(dir);
      expect(offenses(path, source).map(({ ruleId }) => ruleId)).toEqual(["readme/headings"]);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
