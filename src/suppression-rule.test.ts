/**
 * Holds the site code to the rule of ADR 0006: no comment silences a rule of the type checker or a linter.
 * It reads src/, scripts/, and the root config files. A line that must stay goes in the allow list, with its reason.
 */
import { mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, join, relative } from "node:path";
import { describe, expect, it } from "vitest";
import { type Offense, report } from "./rule-report";

const ROOT = process.cwd();
const TREES = ["src", "scripts"].map((dir) => join(ROOT, dir));
const ROOT_FILES = ["next.config.ts", "vitest.config.ts", "postcss.config.mjs"].map((file) => join(ROOT, file));

/* The test builds each pattern from two parts, so this file holds no match and the test never skips its own file. */
const TS = "@" + "ts-";
const PATTERNS = [TS + "expect-error", TS + "ignore", TS + "nocheck", "eslint" + "-disable"];

/*
 * The allow list is the only place a suppression may live. The key is the path and the line text, and the value is the reason.
 * The key holds the text, not the line number, so the entry does not go stale when a line above it moves.
 * An entry with no match fails the test.
 */
const ALLOW = new Map<string, string>();

const RULE = "no comment silences a rule";
const ADR = "docs/adr/0006-the-rules-are-checks.md";

/* Every source file under a tree, tests too. */
function sourceFiles(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) return sourceFiles(path);
    return /\.(ts|tsx|js|mjs)$/.test(entry.name) ? [path] : [];
  });
}

function siteFiles(): string[] {
  return [...TREES.flatMap((dir) => sourceFiles(dir)), ...ROOT_FILES];
}

function allowKey(path: string, line: string): string {
  return `${path}: ${line.trim()}`;
}

/* Each suppression line with its allow key, before the allow list applies. */
function suppressions(path: string, source: string): { key: string; offense: Offense }[] {
  const name = basename(path);
  return source.split("\n").flatMap((line, index) =>
    PATTERNS.filter((pattern) => line.includes(pattern)).map((pattern) => ({
      key: allowKey(path, line),
      offense: {
        path,
        line: index + 1,
        ruleId: "suppression/comment",
        what: `${name} holds ${pattern}.`,
        rule: RULE,
        adr: ADR,
        fix: "fix the type or the code, or add the line to the allow list of this test with its reason.",
      },
    })),
  );
}

/* The rule takes the path and the source apart from the disk, so a test can run it on one string. */
function offenses(path: string, source: string, allow = ALLOW): Offense[] {
  return suppressions(path, source)
    .filter(({ key }) => !allow.has(key))
    .map(({ offense }) => offense);
}

/* An entry that matches no line is stale, and a stale entry cannot stay. The path is the part of the key before the line text. */
function staleEntries(files: { path: string; source: string }[], allow = ALLOW): Offense[] {
  const keys = new Set(files.flatMap(({ path, source }) => suppressions(path, source).map(({ key }) => key)));
  return [...allow.keys()]
    .filter((key) => !keys.has(key))
    .map((key) => ({
      path: key.slice(0, key.indexOf(": ")),
      line: "allow",
      ruleId: "suppression/stale-allow",
      what: "The allow list names a line that no file holds.",
      rule: RULE,
      adr: ADR,
      fix: "remove the entry from the allow list.",
    }));
}

function readSite(file: string): { path: string; source: string } {
  return { path: relative(ROOT, file), source: readFileSync(file, "utf8") };
}

describe("the suppression rule", () => {
  it("finds the site code and the root config files", () => {
    // An empty list would pass with no file read.
    const paths = siteFiles().map((file) => relative(ROOT, file));
    expect(paths).toContain("scripts/check-export.mjs");
    expect(paths).toContain("src/suppression-rule.test.ts");
    expect(paths).toEqual(expect.arrayContaining(["next.config.ts", "vitest.config.ts", "postcss.config.mjs"]));
  });

  it("finds no suppression comment outside the allow list", () => {
    const found = siteFiles()
      .map(readSite)
      .flatMap(({ path, source }) => offenses(path, source));
    if (found.length > 0) throw new Error(report(found));
  });

  it("finds no stale entry in the allow list", () => {
    const found = staleEntries(siteFiles().map(readSite));
    if (found.length > 0) throw new Error(report(found));
  });

  it(`finds one offense in a source string with a ${TS}ignore line`, () => {
    const found = offenses("src/lib/week.ts", `const a = 1;\n// ${TS}ignore\nconst b: string = a;\n`);
    expect(found.map(({ ruleId, line }) => ({ ruleId, line }))).toEqual([{ ruleId: "suppression/comment", line: 2 }]);
  });

  it("passes a line in the allow list and finds an entry that matches no line", () => {
    const source = `// ${TS}ignore the reason\n`;
    const allow = new Map([
      [allowKey("src/lib/week.ts", `  // ${TS}ignore the reason`), "a test reason"],
      [allowKey("src/lib/gone.ts", `// ${TS}ignore`), "a test reason"],
    ]);
    expect(offenses("src/lib/week.ts", source, allow)).toEqual([]);
    const stale = staleEntries([{ path: "src/lib/week.ts", source }], allow);
    expect(stale.map(({ path, line, ruleId }) => ({ path, line, ruleId }))).toEqual([
      { path: "src/lib/gone.ts", line: "allow", ruleId: "suppression/stale-allow" },
    ]);
  });

  it("finds one offense in a file on disk with a suppression comment", () => {
    // The file goes through the same disk path as the real tree, so a break in the read also fails here.
    const dir = mkdtempSync(join(tmpdir(), "suppression-rule-"));
    try {
      writeFileSync(join(dir, "week.mjs"), `// ${"eslint" + "-disable"}-next-line\nconst a = 1;\n`);
      const found = sourceFiles(dir)
        .map(readSite)
        .flatMap(({ path, source }) => offenses(path, source));
      expect(found.map(({ ruleId, line }) => ({ ruleId, line }))).toEqual([{ ruleId: "suppression/comment", line: 1 }]);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
