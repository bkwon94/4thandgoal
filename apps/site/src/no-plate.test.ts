/**
 * Holds the site to ADR 0036: hero text has no plate. No source file of the site or of a package uses the plate class,
 * and globals.css defines no plate utility. The test skips comments, because they may name the rule.
 */
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";
import { describe, expect, it } from "bun:test";

const ROOT = join(process.cwd(), "..", "..");

/* The source folders of the site: the app, and the site side of each package. */
function sourceDirs(): string[] {
  const packages = join(ROOT, "packages");
  const sites = readdirSync(packages)
    .map((name) => join(packages, name, "site"))
    .filter((dir) => existsSync(dir));
  return [join(process.cwd(), "src"), ...sites];
}

function sourceFiles(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) return entry.name === "node_modules" ? [] : sourceFiles(path);
    return /\.(ts|tsx|css)$/.test(entry.name) ? [path] : [];
  });
}

/* Block comments and line comments out, so only code and class strings stay. */
function withoutComments(text: string): string {
  return text.replace(/\/\*[\s\S]*?\*\//g, "").replace(/^\s*\/\/.*$/gm, "");
}

describe("Hero text has no plate (ADR 0036)", () => {
  it("uses no plate class and defines no plate utility in any source file", () => {
    const hits = sourceDirs()
      .flatMap(sourceFiles)
      .filter((path) => !path.endsWith("no-plate.test.ts"))
      .filter((path) => /\bplate\b/.test(withoutComments(readFileSync(path, "utf8"))))
      .map((path) => relative(ROOT, path));
    expect(hits).toEqual([]);
  });
});
