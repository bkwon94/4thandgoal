/**
 * Tests that the working folder of a fixed site is a stub that the test puts back.
 * The fixed folder holds inside one test, and the real folder returns after the restore.
 */
import { describe, expect, it } from "bun:test";
import { fixtureSite, readFixtureSite, restoreFixtureSite } from "@/fixtures/sites";

const realCwd = process.cwd();

describe("readFixtureSite", () => {
  it("points the working folder at the fixed site folder, and the restore puts the real folder back", () => {
    readFixtureSite("cpc");
    expect(process.cwd()).toBe(fixtureSite("cpc"));
    restoreFixtureSite();
    expect(process.cwd()).toBe(realCwd);
  });
});
