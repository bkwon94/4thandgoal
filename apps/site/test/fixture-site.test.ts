/**
 * Tests that the working folder of a fixed site is a spy that the preload restores.
 * The fixed folder holds inside one test, and the real folder returns in the next test.
 */
import { describe, expect, it } from "bun:test";
import { fixtureSite, readFixtureSite } from "@/fixtures/sites";

const realCwd = process.cwd();

describe("readFixtureSite", () => {
  it("points the working folder at the fixed site folder", () => {
    readFixtureSite("cpc");
    expect(process.cwd()).toBe(fixtureSite("cpc"));
  });

  it("leaves the real folder to the next test, because the preload restores the spy", () => {
    expect(process.cwd()).toBe(realCwd);
  });
});
