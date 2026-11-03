/**
 * Holds every file under src/components/ to the rule of ADR 0012: a component takes data and returns markup.
 * It fails on an import of node:fs, the config module, or a lib/data loader, or a read of process.env.
 * A failure names the file and the line.
 */
import { mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, join, relative } from "node:path";
import { describe, expect, it } from "vitest";
import { type Offense, report } from "./rule-report";

const COMPONENTS_DIR = join(process.cwd(), "src", "components");

/* Every source file under the component tree, tests too, because a test that reaches the config hides a prop the component lacks. */
function sourceFiles(dir = COMPONENTS_DIR): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) return sourceFiles(path);
    return /\.(ts|tsx)$/.test(entry.name) ? [path] : [];
  });
}

/* A module name in an import, an export from, a dynamic import, a vi.mock, or a require. Only these reach a module. */
const SPECIFIER = /(?:\bfrom|\bimport\s*\(?|\bmock\s*\(|\brequire\s*\()\s*["']([^"']+)["']/g;

/* The modules a component must not reach. The match takes the alias and a relative path alike. */
const BANNED: { ruleId: string; test: (specifier: string) => boolean; fix: string }[] = [
  {
    ruleId: "components/no-fs",
    test: (s) => /^(node:)?fs(\/promises)?$/.test(s),
    fix: "read the file in src/app/ and pass the value to the component as a prop.",
  },
  {
    ruleId: "components/no-config",
    test: (s) => /(^|\/)lib\/config$/.test(s),
    fix: "read the config in src/app/ and pass the value to the component as a prop.",
  },
  {
    ruleId: "components/no-loader",
    test: (s) => /(^|\/)lib\/data(\/|$)/.test(s),
    fix: "call the loader in src/app/ and pass the value to the component as a prop.",
  },
];

const RULE = "a component takes data and returns markup";
const ADR = "docs/adr/0012-a-component-takes-data-and-returns-markup.md";

/* The rule takes the path and the source apart from the disk, so a test can run it on one string. */
function offenses(path: string, source: string): Offense[] {
  const name = basename(path);
  return source.split("\n").flatMap((line, index) => {
    const at = { path, line: index + 1, rule: RULE, adr: ADR };
    const found: Offense[] = [];
    for (const [, specifier] of line.matchAll(SPECIFIER)) {
      for (const banned of BANNED) {
        if (banned.test(specifier)) found.push({ ...at, ruleId: banned.ruleId, what: `${name} imports ${specifier}.`, fix: banned.fix });
      }
    }
    if (/\bprocess\.env\b/.test(line)) {
      found.push({
        ...at,
        ruleId: "components/no-env",
        what: `${name} reads process.env.`,
        fix: "read process.env in src/app/ and pass the value to the component as a prop.",
      });
    }
    return found;
  });
}

function fileOffenses(file: string): Offense[] {
  return offenses(relative(process.cwd(), file), readFileSync(file, "utf8"));
}

describe("the component rule", () => {
  it("finds the component tree", () => {
    // An empty list would pass with no file read.
    expect(sourceFiles().length).toBeGreaterThan(0);
  });

  it("finds no component that reads a file, reads the env, imports the config, or imports a loader", () => {
    const found = sourceFiles().flatMap(fileOffenses);
    if (found.length > 0) throw new Error(report(found));
  });

  it("finds one offense in a component that imports a loader", () => {
    const found = offenses("src/components/week/standings.tsx", 'import { weekData } from "@/lib/data/week-data";\n');
    expect(found.map(({ ruleId, line }) => ({ ruleId, line }))).toEqual([{ ruleId: "components/no-loader", line: 1 }]);
  });

  it("finds one offense in a component file on disk that imports a loader", () => {
    // The file goes through the same disk path as the real tree, so a break in the read also fails here.
    const dir = mkdtempSync(join(tmpdir(), "component-rule-"));
    try {
      const file = join(dir, "standings.tsx");
      writeFileSync(file, 'import { weekData } from "@/lib/data/week-data";\n');
      const found = fileOffenses(file);
      expect(found.map(({ ruleId, line }) => ({ ruleId, line }))).toEqual([{ ruleId: "components/no-loader", line: 1 }]);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
