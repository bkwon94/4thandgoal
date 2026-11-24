/**
 * Tests of the scope of a `bun test` run: the shard of a CI job, and the choice between the full suite and the tests the diff can reach.
 * CI runs the unit suite in a matrix of shards, and on a PR it runs only the reachable tests unless the diff names a config file.
 */
import { describe, expect, it } from "bun:test";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import {
  FULL_SUITE_FILES,
  changedFilesSince,
  needsFullSuite,
  scopeArgs,
  shardArg,
  workerCount,
} from "./test-scope.mjs";

const SITE = join(import.meta.dirname, "..");

describe("the count of workers of a bun test run", () => {
  it("is 3 on a local run, with no BUN_TEST_WORKERS and no CI, so many agents at once do not swap the Mac", () => {
    expect(workerCount({ env: {}, cores: 10 })).toBe("3");
  });

  it("is one worker per CPU core when CI is set", () => {
    expect(workerCount({ env: { CI: "true" }, cores: 4 })).toBe("4");
  });

  it("is BUN_TEST_WORKERS when it is set, with or without CI", () => {
    expect(workerCount({ env: { BUN_TEST_WORKERS: "5" }, cores: 10 })).toBe("5");
    expect(workerCount({ env: { BUN_TEST_WORKERS: "2", CI: "true" }, cores: 10 })).toBe("2");
  });
});

describe("the shard of a bun test run", () => {
  it("is no flag when BUN_TEST_SHARD is not set or empty, so a local run takes every file", () => {
    expect(shardArg(undefined)).toEqual([]);
    expect(shardArg("")).toEqual([]);
  });

  it("gives 2/4 to bun test as --shard=2/4, split by the measured time of each file", () => {
    expect(shardArg("2/4")).toEqual(["--shard=2/4", "--timings=bun-test-timings.json"]);
  });

  it("reads a timings file that holds the time of each test file, so no shard gets the slow files of another", () => {
    const { version, files } = JSON.parse(
      readFileSync(join(SITE, "bun-test-timings.json"), "utf8"),
    );
    expect(version).toBe(1);
    // The slowest page test takes about 30 s alone, so a split by file count can put two of them in one shard.
    expect(files["src/app/page-free.test.tsx"]).toBeGreaterThan(1000);
    expect(Object.keys(files).length).toBeGreaterThan(100);
  });

  it("stops on a value that names no shard, so a typo in CI cannot run every file in each shard", () => {
    for (const bad of ["4", "0/4", "5/4", "a/b", "2/4/1", " 2/4"]) {
      expect(() => shardArg(bad), bad).toThrow(/BUN_TEST_SHARD/);
    }
  });
});

describe("the files that run the full suite", () => {
  it("name the lock file, the Bun settings, the test preload, and the runner itself", () => {
    for (const file of [
      "pnpm-lock.yaml",
      "pnpm-workspace.yaml",
      ".bun-version",
      "apps/site/bunfig.toml",
      "apps/site/package.json",
      "apps/site/tsconfig.json",
      "apps/site/test/preload.ts",
      "apps/site/test/stubs.ts",
      "apps/site/scripts/bun-test.mjs",
      "apps/site/scripts/test-scope.mjs",
      ".github/workflows/check.yml",
    ]) {
      expect(needsFullSuite([file]), file).toBe(true);
    }
  });

  it("name the package.json of the site side of each package, also a package that does not exist yet", () => {
    expect(needsFullSuite(["packages/rankings/site/package.json"])).toBe(true);
    expect(needsFullSuite(["packages/some-later-package/site/package.json"])).toBe(true);
  });

  it("name the Oxlint config and each file of the design rules, which the rule tests reach only through Oxlint", () => {
    for (const file of [
      ".oxlintrc.json",
      "packages/design/lint/plugin.mjs",
      "packages/design/lint/rules/use-lines.mjs",
    ]) {
      expect(needsFullSuite([file]), file).toBe(true);
    }
  });

  it("leave out a source file, a test file, and a doc, so Bun picks the reachable tests", () => {
    expect(
      needsFullSuite([
        "packages/rankings/site/chapters/power-rankings.tsx",
        "apps/site/src/app/page.tsx",
        "apps/site/scripts/client-build.test.mjs",
        "packages/rankings/site/chapters/README.md",
        "apps/site/test-other/preload.ts",
      ]),
    ).toBe(false);
  });

  it("is one list, and each entry names a path from the root of the repo", () => {
    expect(FULL_SUITE_FILES.length).toBeGreaterThan(0);
    for (const entry of FULL_SUITE_FILES) {
      expect(entry.startsWith("/") || entry.startsWith("./"), entry).toBe(false);
    }
  });
});

describe("the scope of a bun test run", () => {
  it("is the full suite with no base, as on a push", () => {
    expect(scopeArgs({ base: undefined, changedFiles: [] })).toEqual([]);
    expect(scopeArgs({ base: "", changedFiles: [] })).toEqual([]);
  });

  it("is the reachable tests of the base on a PR that changes one source file", () => {
    expect(
      scopeArgs({
        base: "HEAD^1",
        changedFiles: ["packages/rankings/site/chapters/power-rankings.tsx"],
      }),
    ).toEqual(["--changed=HEAD^1"]);
  });

  it("is the full suite on a PR that changes the lock file next to a source file", () => {
    expect(
      scopeArgs({
        base: "HEAD^1",
        changedFiles: ["packages/rankings/site/chapters/power-rankings.tsx", "pnpm-lock.yaml"],
      }),
    ).toEqual([]);
  });

  it("is the full suite when git cannot list the diff, so a missing base never skips a test", () => {
    expect(scopeArgs({ base: "HEAD^1", changedFiles: null })).toEqual([]);
  });
});

describe("the changed files since a base", () => {
  it("lists each changed file of the work tree as a path from the root of the repo", () => {
    // The tree of HEAD differs from the empty tree of git in each tracked file, so the list holds the package.json of the site.
    const emptyTree = "4b825dc642cb6eb9a060e54bf8d69288fbee4904";
    expect(changedFilesSince(emptyTree)).toContain("apps/site/package.json");
  });

  it("is null for a base that git does not know, so the run takes the full suite", () => {
    expect(changedFilesSince("no-such-ref-of-the-repo")).toBeNull();
  });
});
