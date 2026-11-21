/**
 * Tests of the shard of a Playwright run, read from the env value PLAYWRIGHT_SHARD, and of the serial projects of the config.
 * CI runs the browser check in a matrix of shards. The serial projects keep one worker in each shard.
 */
import { describe, expect, it } from "bun:test";
import { resetModules } from "../test/reset-modules";
import { stubEnv } from "../test/stubs";
import { shardOfEnv } from "./playwright-shard.mjs";
import { inShard } from "./playwright-shard-reporter.mjs";

describe("the shard of a Playwright run", () => {
  it("is null when PLAYWRIGHT_SHARD is not set or empty, so a local run takes every test", () => {
    expect(shardOfEnv(undefined)).toBeNull();
    expect(shardOfEnv("")).toBeNull();
  });

  it("reads 2/4 as the second of four shards", () => {
    expect(shardOfEnv("2/4")).toEqual({ current: 2, total: 4 });
  });

  it("stops on a value that names no shard, so a typo in CI cannot run every test in each shard", () => {
    for (const bad of ["4", "0/4", "5/4", "a/b", "2/4/1", " 2/4"]) {
      expect(() => shardOfEnv(bad), bad).toThrow(/PLAYWRIGHT_SHARD/);
    }
  });
});

/* The config as Playwright reads it, with PLAYWRIGHT_SHARD set to `shard`. The config reads the env when it loads. */
async function configWithShard(shard) {
  resetModules();
  stubEnv("PLAYWRIGHT_SHARD", shard);
  return (await import("../playwright.config.ts")).default;
}

describe("the Playwright config", () => {
  it("runs the shard that PLAYWRIGHT_SHARD names, and every test with no value", async () => {
    expect((await configWithShard("3/4")).shard).toEqual({ current: 3, total: 4 });
    expect((await configWithShard("")).shard).toBeNull();
  });

  it("gives the serial projects floor-timing and eggs one worker, so a shard never runs two of their tests at once", async () => {
    const config = await configWithShard("1/4");
    const project = (name) => config.projects.find((each) => each.name === name);
    expect(project("floor-timing").workers).toBe(1);
    expect(project("eggs").workers).toBe(1);
  });

  it("splits floor-timing by test, not by file, so its tests spread over the shards", async () => {
    const config = await configWithShard("1/4");
    expect(config.projects.find((each) => each.name === "floor-timing").fullyParallel).toBe(true);
  });
});

describe("the split of the shard reporter", () => {
  const tests = ["a1", "a2", "a3", "a4", "b1", "b2", "c1"];

  it("gives each shard each Nth test, so the tests of the first file spread over the shards", () => {
    expect(inShard(tests, { current: 1, total: 3 })).toEqual(["a1", "a4", "c1"]);
    expect(inShard(tests, { current: 2, total: 3 })).toEqual(["a2", "b1"]);
    expect(inShard(tests, { current: 3, total: 3 })).toEqual(["a3", "b2"]);
  });

  it("puts every test in exactly one shard", () => {
    for (const total of [1, 2, 6, 7, 9]) {
      const shards = Array.from({ length: total }, (_, index) =>
        inShard(tests, { current: index + 1, total }),
      );
      expect(shards.flat().toSorted()).toEqual(tests.toSorted());
    }
  });

  it("keeps each file of a project in wholeFileProjects in one shard", () => {
    const options = {
      wholeFileProjects: ["eggs"],
      projectOf: (test) => (test.startsWith("a") ? "eggs" : "floor"),
      fileOf: (test) => test[0],
    };
    expect(inShard(tests, { current: 1, total: 2 }, options)).toEqual([
      "a1",
      "a2",
      "a3",
      "a4",
      "b2",
    ]);
    expect(inShard(tests, { current: 2, total: 2 }, options)).toEqual(["b1", "c1"]);
  });
});

describe("the reporter of the Playwright config", () => {
  it("keeps whole the files of each project that is not fully parallel, and only those", async () => {
    const config = await configWithShard("1/4");
    const [, [path, options]] = config.reporter;
    expect(path).toBe("./scripts/playwright-shard-reporter.mjs");
    const serial = config.projects
      .filter((each) => each.fullyParallel === false)
      .map((each) => each.name);
    expect(options.wholeFileProjects).toEqual(serial);
  });
});
