/**
 * Tests of the shard of a Playwright run, read from the env value PLAYWRIGHT_SHARD, and of the serial projects of the config.
 * CI runs the browser check in a matrix of shards. The serial projects keep one worker in each shard.
 */
import { describe, expect, it } from "bun:test";
import { resetModules } from "../test/reset-modules";
import { stubEnv } from "../test/stubs";
import { shardOfEnv } from "./playwright-shard.mjs";

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
