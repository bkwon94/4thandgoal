/**
 * Tests that the site holds no push notification (AT-55 of playoff-paths): no code of the site or of a package site
 * folder names a service worker, `Notification`, or `PushManager`.
 */
import { describe, expect, it } from "bun:test";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";

const repo = join(import.meta.dir, "..", "..", "..");
const site = join(repo, "apps", "site");
const packages = join(repo, "packages");
// The folders of installed, built, or test output, which hold no code of the repo.
const SKIP = new Set([
  "node_modules",
  ".next",
  "out",
  "public",
  "test-results",
  "playwright-report",
]);
const CODE = /\.(ts|tsx|js|jsx|mjs|cjs)$/;
const PUSH = /serviceWorker|PushManager|\bNotification\b/;

function codeFiles(folder: string): string[] {
  return readdirSync(folder, { withFileTypes: true }).flatMap((entry) => {
    const path = join(folder, entry.name);
    if (entry.isDirectory()) return SKIP.has(entry.name) ? [] : codeFiles(path);
    return CODE.test(entry.name) ? [path] : [];
  });
}

const siteFolders = [
  site,
  ...readdirSync(packages, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => join(packages, entry.name, "site")),
].filter((folder) => existsSync(folder));

describe("the site with no push notification", () => {
  it("names no service worker, Notification, or PushManager in its code", () => {
    const files = siteFolders.flatMap(codeFiles).filter((path) => path !== import.meta.path);
    expect(files.length).toBeGreaterThan(100);
    const hits = files
      .filter((path) => PUSH.test(readFileSync(path, "utf8")))
      .map((path) => relative(repo, path));
    expect(hits).toEqual([]);
  });
});
