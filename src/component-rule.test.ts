/**
 * Holds every file under src/components/ to the rule of ADR 0004: a component takes data and returns markup.
 * It fails on an import of node:fs, the config module, or a lib/data loader, or a read of process.env.
 * A failure names the file and the line.
 */
import { readdirSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";
import { describe, expect, it } from "vitest";

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
const BANNED: { why: string; test: (specifier: string) => boolean }[] = [
  { why: "imports the node fs", test: (s) => /^(node:)?fs(\/promises)?$/.test(s) },
  { why: "imports the config module", test: (s) => /(^|\/)lib\/config$/.test(s) },
  { why: "imports a lib/data loader", test: (s) => /(^|\/)lib\/data(\/|$)/.test(s) },
];

function breaches(file: string): string[] {
  const name = relative(process.cwd(), file);
  return readFileSync(file, "utf8")
    .split("\n")
    .flatMap((line, index) => {
      const where = `${name}:${index + 1}`;
      const found: string[] = [];
      for (const [, specifier] of line.matchAll(SPECIFIER)) {
        for (const rule of BANNED) if (rule.test(specifier)) found.push(`${where} ${rule.why}: ${line.trim()}`);
      }
      if (/\bprocess\.env\b/.test(line)) found.push(`${where} reads process.env: ${line.trim()}`);
      return found;
    });
}

describe("the component rule", () => {
  it("finds the component tree", () => {
    // An empty list would pass with no file read.
    expect(sourceFiles().length).toBeGreaterThan(0);
  });

  it("finds no component that reads a file, reads the env, imports the config, or imports a loader", () => {
    const found = sourceFiles().flatMap(breaches);
    if (found.length > 0) throw new Error(`A component breaks ADR 0004. Pass the value as a prop from src/app/:\n${found.join("\n")}`);
  });
});
