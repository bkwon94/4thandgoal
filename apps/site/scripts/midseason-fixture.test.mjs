/**
 * Tests of the fixture client of the midseason report: a copy of a real client that takes midseason and sim, with the
 * package fixtures in its published season folder, so the floor of the report runs before any client publishes one.
 */
// @vitest-environment node
import { existsSync, readFileSync, rmSync } from "node:fs";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { parse } from "smol-toml";
import { buildClient, REPO_ROOT } from "./client-build.mjs";
import { fixtureRoot } from "./midseason-fixture.mjs";

const temps = [];
afterEach(() => {
  for (const dir of temps.splice(0)) rmSync(dir, { recursive: true, force: true });
});

const fixtureText = (pkg, name) => readFileSync(join(REPO_ROOT, "packages", pkg, "site", "fixtures", name), "utf8");

describe("the fixture client of the midseason report", () => {
  it("copies the client, takes midseason and sim, and holds both package fixtures in the season folder", () => {
    const root = fixtureRoot("cpc");
    temps.push(root);
    const client = join(root, "clients", "cpc");
    const { packages } = parse(readFileSync(join(client, "client.toml"), "utf8"));
    expect(packages).toEqual(expect.arrayContaining(["week", "rankings", "managers", "analyzer", "midseason", "sim"]));
    expect(readFileSync(join(client, "published", "2026", "midseason.json"), "utf8")).toBe(fixtureText("midseason", "midseason.json"));
    expect(readFileSync(join(client, "published", "2026", "sim.json"), "utf8")).toBe(fixtureText("sim", "sim.json"));
    // The real published weeks stay, so the home page shows the takeover over the real latest week.
    expect(existsSync(join(client, "published", "2026", "week-08", "page.json"))).toBe(true);
  });

  it("builds the report route of the fixture season", () => {
    const root = fixtureRoot("cpc");
    temps.push(root);
    const site = join(root, "apps", "site");
    buildClient({ slug: "cpc", root, site });
    expect(existsSync(join(site, "src", "app", "(client)", "midseason", "[season]", "page.tsx"))).toBe(true);
    expect(existsSync(join(site, "public", "2026", "sim.json"))).toBe(true);
  });

  it("leaves the real client folder as it is", () => {
    const before = readFileSync(join(REPO_ROOT, "clients", "cpc", "client.toml"), "utf8");
    temps.push(fixtureRoot("cpc"));
    expect(readFileSync(join(REPO_ROOT, "clients", "cpc", "client.toml"), "utf8")).toBe(before);
    expect(existsSync(join(REPO_ROOT, "clients", "cpc", "published", "2026", "midseason.json"))).toBe(false);
  });
});
