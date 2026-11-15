/**
 * Holds the site side of each package and src/ of the app to the wrapper rule: only packages/design/site/ui/ imports the ui-sdk scope.
 * It fails on an import of the ui-sdk scope in any other .ts or .tsx file. The scope name is built at run time, so a search for it lists no rule file. A failure names the file and the line.
 */
import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, join, relative, sep } from "node:path";
import { describe, expect, it } from "vitest";
import { type Offense, report } from "./rule-report";

/* Built at run time, so a search of the source for the scope finds only the wrapper folder. */
const SCOPE = ["@", "ui-sdk"].join("");
const SRC_DIR = join(process.cwd(), "src");
const PACKAGES_DIR = join(process.cwd(), "..", "..", "packages");
const WRAPPER_DIR = join(PACKAGES_DIR, "design", "site", "ui");

/* The site side of each package, and the source of the app. */
function roots(): string[] {
  const packageSides = existsSync(PACKAGES_DIR)
    ? readdirSync(PACKAGES_DIR).map((name) => join(PACKAGES_DIR, name, "site"))
    : [];
  return [SRC_DIR, ...packageSides].filter((dir) => existsSync(dir));
}

function sourceFiles(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) return entry.name === "node_modules" ? [] : sourceFiles(path);
    return /\.(ts|tsx)$/.test(entry.name) ? [path] : [];
  });
}

/* A module name in an import, an export from, a dynamic import, a vi.mock, or a require. Only these reach a module. */
const SPECIFIER = /(?:\bfrom|\bimport\s*\(?|\bmock\s*\(|\brequire\s*\()\s*["']([^"']+)["']/g;

const RULE = `only the wrapper folder of the design package imports ${SCOPE}`;
const ADR = ".scratch/ui-sdk-sheet/PRD.md";

/* The wrapper folder is the one place that may import the ui-sdk scope. */
function inWrapperDir(file: string): boolean {
  return file.startsWith(WRAPPER_DIR + sep);
}

/* The rule takes the path and the source apart from the disk, so a test can run it on one string. */
function offenses(path: string, source: string): Offense[] {
  const name = basename(path);
  return source.split("\n").flatMap((line, index) =>
    [...line.matchAll(SPECIFIER)]
      .filter(([, specifier]) => specifier.startsWith(`${SCOPE}/`))
      .map(([, specifier]) => ({
        path,
        line: index + 1,
        ruleId: "ui/no-ui-sdk-outside-wrapper",
        what: `${name} imports ${specifier}.`,
        rule: RULE,
        adr: ADR,
        fix: "import the wrapper in the ui folder of the design package",
      })),
  );
}

function fileOffenses(file: string): Offense[] {
  return offenses(relative(process.cwd(), file), readFileSync(file, "utf8"));
}

/* The fixture builds the specifier at run time, so the real-tree scan does not find an import in this file. */
const DRAWER_IMPORT = `import { Drawer } from ${JSON.stringify(`${SCOPE}/react/drawer`)};\n`;

describe("the ui-sdk wrapper rule", () => {
  it("finds the source tree", () => {
    // An empty list would pass with no file read.
    expect(roots().flatMap(sourceFiles).length).toBeGreaterThan(0);
  });

  it("finds no file outside the wrapper folder that imports the ui-sdk scope", () => {
    const found = roots()
      .flatMap(sourceFiles)
      .filter((file) => !inWrapperDir(file))
      .flatMap(fileOffenses);
    if (found.length > 0) throw new Error(report(found));
  });

  it("finds one offense in a shell file that imports the ui-sdk scope", () => {
    const found = offenses("packages/design/site/shell/top-band.tsx", DRAWER_IMPORT);
    expect(found.map(({ ruleId, line }) => ({ ruleId, line }))).toEqual([{ ruleId: "ui/no-ui-sdk-outside-wrapper", line: 1 }]);
  });

  it("finds no offense in a file that imports the wrapper", () => {
    expect(offenses("packages/design/site/shell/top-band.tsx", 'import { Sheet } from "../ui/sheet";\n')).toEqual([]);
  });

  it("finds one offense in a file on disk that imports the ui-sdk scope", () => {
    // The file goes through the same disk path as the real tree, so a break in the read also fails here.
    const dir = mkdtempSync(join(tmpdir(), "ui-sdk-rule-"));
    try {
      const file = join(dir, "top-band.tsx");
      writeFileSync(file, DRAWER_IMPORT);
      const found = fileOffenses(file);
      expect(found.map(({ ruleId, line }) => ({ ruleId, line }))).toEqual([{ ruleId: "ui/no-ui-sdk-outside-wrapper", line: 1 }]);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
