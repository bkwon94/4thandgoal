/**
 * Tests of the client build: the check of client.toml, the generated files, and the copy of the published data.
 * Each test builds a real client folder in a temp repo, or runs the script on the real clients/cpc folder.
 */
// @vitest-environment node
import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { buildClient, ClientBuildError, clientRoot, REPO_ROOT, SCHEMA_FILE } from "./client-build.mjs";

const SCRIPT = join(process.cwd(), "scripts", "client-build.mjs");
const CPC_TOML = readFileSync(join(REPO_ROOT, "clients", "cpc", "client.toml"), "utf8");
const CPC_BRAND = readFileSync(join(REPO_ROOT, "clients", "cpc", "brand.toml"), "utf8");
const CPC_COPY = readFileSync(join(REPO_ROOT, "clients", "cpc", "copy.toml"), "utf8");

const temps = [];
afterEach(() => {
  for (const dir of temps.splice(0)) rmSync(dir, { recursive: true, force: true });
});

/* A temp repo with the exported schema, one client folder with the given client.toml and the CPC brand and copy,
   and an empty site app. */
function tempRepo(toml = CPC_TOML, slug = "cpc", { brand = CPC_BRAND, copy = CPC_COPY } = {}) {
  const root = mkdtempSync(join(tmpdir(), "client-build-"));
  temps.push(root);
  const schema = join(root, SCHEMA_FILE);
  mkdirSync(join(schema, ".."), { recursive: true });
  cpSync(join(REPO_ROOT, SCHEMA_FILE), schema);
  mkdirSync(join(root, "clients", slug), { recursive: true });
  writeFileSync(join(root, "clients", slug, "client.toml"), toml);
  writeFileSync(join(root, "clients", slug, "brand.toml"), brand);
  writeFileSync(join(root, "clients", slug, "copy.toml"), copy);
  const site = join(root, "apps", "site");
  mkdirSync(join(site, "public"), { recursive: true });
  return { root, site, slug };
}

function published(root, slug, path, text = "{}") {
  const file = join(root, "clients", slug, "published", path);
  mkdirSync(join(file, ".."), { recursive: true });
  writeFileSync(file, text);
}

/* The values that the client build wrote into src/generated/client-values.ts, read back as JSON. */
function clientValuesOf(site) {
  const text = readFileSync(join(site, "src", "generated", "client-values.ts"), "utf8");
  return JSON.parse(text.slice(text.indexOf("= {") + 2, text.lastIndexOf("}") + 1));
}

/* Each generated route file under src/app/, as a path from src/app/, sorted. */
function routeFiles(site) {
  const app = join(site, "src", "app");
  return readdirSync(app, { recursive: true, withFileTypes: true })
    .filter((entry) => entry.isFile())
    .map((entry) => join(entry.parentPath, entry.name).slice(app.length + 1))
    .sort();
}

describe("the client build", () => {
  it("exits non-zero and names CLIENT when the env has no CLIENT", () => {
    const env = { ...process.env };
    delete env.CLIENT;
    const run = spawnSync(process.execPath, [SCRIPT], { env, encoding: "utf8" });
    expect(run.status).not.toBe(0);
    expect(run.stderr).toContain("CLIENT");
  });

  it("fails on an unknown key and names the key and the file", () => {
    const repo = tempRepo(CPC_TOML.replace("finder = false", "finder = false\nfinderr = true"));
    const file = join(repo.root, "clients", "cpc", "client.toml");
    expect(() => buildClient(repo)).toThrow(ClientBuildError);
    expect(() => buildClient(repo)).toThrow(/finderr/);
    expect(() => buildClient(repo)).toThrow(file);
  });

  it("fails on a menu item for an omitted package and names the item and the package", () => {
    const toml = CPC_TOML.replace('{ package = "week" },', '{ package = "week" },\n  { package = "waiver" },');
    expect(() => buildClient(tempRepo(toml))).toThrow(/menu item for waiver names a package that is not in the package list/);
  });

  it("writes one route file per package of the list, and no route of an omitted package", () => {
    const repo = tempRepo();
    published(repo.root, "cpc", "2026/week-06/page.json");
    published(repo.root, "cpc", "2026/managers.json");
    // A waiver file with no waiver in the list must still give no waiver route.
    published(repo.root, "cpc", "2026/week-06/waiver.json");
    buildClient(repo);
    expect(routeFiles(repo.site)).toEqual([
      "(client)/[season]/[week]/page.tsx",
      "(client)/[season]/managers/[roster]/page.tsx",
      "(client)/[season]/managers/page.tsx",
      "(client)/analyze/page.tsx",
      "(client)/rankings/page.tsx",
    ]);
  });

  it("starts each generated file with a GENERATED line that names the client file", () => {
    const repo = tempRepo();
    published(repo.root, "cpc", "2026/week-06/page.json");
    buildClient(repo);
    const files = [
      ...routeFiles(repo.site).map((path) => join(repo.site, "src", "app", path)),
      join(repo.site, "src", "generated", "registry.ts"),
      join(repo.site, "src", "generated", "client-values.ts"),
    ];
    for (const file of files) {
      expect(readFileSync(file, "utf8").split("\n")[0]).toBe(
        "// GENERATED by apps/site/scripts/client-build.mjs from clients/cpc/client.toml. Do not edit.",
      );
    }
    expect(readFileSync(join(repo.site, "src", "generated", "brand.css"), "utf8").split("\n")[0]).toBe(
      "/* GENERATED by apps/site/scripts/client-build.mjs from clients/cpc/brand.toml. Do not edit. */",
    );
  });

  it("writes the waiver route when the list takes waiver and a week has a waiver file", () => {
    const repo = tempRepo(CPC_TOML.replace('"analyzer"]', '"analyzer", "waiver"]'));
    published(repo.root, "cpc", "2026/week-06/page.json");
    published(repo.root, "cpc", "2026/week-06/waiver.json");
    buildClient(repo);
    expect(routeFiles(repo.site)).toContain("(client)/[season]/[week]/waiver/page.tsx");
    expect(readFileSync(join(repo.site, "src", "generated", "registry.ts"), "utf8")).toContain("@/app/_routes/waiver/menu");
  });

  it("gives the registry no import line of an omitted package", () => {
    const repo = tempRepo();
    buildClient(repo);
    const registry = readFileSync(join(repo.site, "src", "generated", "registry.ts"), "utf8");
    expect(registry).not.toContain("waiver");
    expect(registry).toContain('import { menuLink as rankingsMenuLink } from "@/app/_routes/rankings/menu";');
    expect(registry).toContain("  rankings: rankingsMenuLink,");
    expect(registry).toContain("  week: weekMenuLink,");
  });

  it("lists the home section of each package of the client in the order of the home page", () => {
    // The list puts week first, but the home page shows the tools, then the rankings, then the weeks.
    const repo = tempRepo();
    buildClient(repo);
    const registry = readFileSync(join(repo.site, "src", "generated", "registry.ts"), "utf8");
    const list = registry.slice(registry.indexOf("export const homeSections: HomeSections = ["));
    expect(list.split("\n").slice(0, 6)).toEqual([
      "export const homeSections: HomeSections = [",
      "  analyzerHomeSection,",
      "  managersHomeSection,",
      "  rankingsHomeSection,",
      "  weekHomeSection,",
      "];",
    ]);
    expect(registry).toContain('import { homeSection as rankingsHomeSection } from "@/app/_routes/rankings/home";');
  });

  it("gives a test client with only week a week route, no rankings route, and no rankings line in the registry (AT-23)", () => {
    const toml = ['packages = ["week"]', 'timezone = "America/New_York"', "", "[seasons.2026]", 'provider = "sleeper"', 'league_id = "1"', ""].join("\n");
    const repo = tempRepo(toml, "week-only");
    published(repo.root, "week-only", "2026/week-06/page.json");
    published(repo.root, "week-only", "2026/rankings.json");
    buildClient(repo);
    expect(routeFiles(repo.site)).toEqual(["(client)/[season]/[week]/page.tsx"]);
    const registry = readFileSync(join(repo.site, "src", "generated", "registry.ts"), "utf8");
    expect(registry).not.toContain("rankings");
    expect(registry).toContain('import { homeSection as weekHomeSection } from "@/app/_routes/week/home";');
  });

  it("gives a client with no home section an empty list with its type", () => {
    const toml = ['packages = ["waiver"]', 'timezone = "America/New_York"', "", "[seasons.2026]", 'provider = "sleeper"', 'league_id = "1"', ""].join("\n");
    const repo = tempRepo(toml, "waiver-only");
    buildClient(repo);
    const registry = readFileSync(join(repo.site, "src", "generated", "registry.ts"), "utf8");
    expect(registry).toContain("export const homeSections: HomeSections = [\n];");
  });

  it("reads the clients of the repo, or of the root that CLIENT_ROOT names", () => {
    expect(clientRoot({})).toBe(REPO_ROOT);
    expect(clientRoot({ CLIENT_ROOT: "/tmp/a-test-repo" })).toBe("/tmp/a-test-repo");
  });

  it("writes the finder value, the usage code, and the latest season into the client values", () => {
    const repo = tempRepo(CPC_TOML.replace("[seasons.2026]", '[seasons.2025]\nprovider = "sleeper"\nleague_id = "1"\n\n[seasons.2026]'));
    buildClient(repo);
    const text = readFileSync(join(repo.site, "src", "generated", "client-values.ts"), "utf8");
    expect(text).toContain('"finder": false');
    expect(text).toContain('"usageCode": "cpcfantasy"');
    expect(text).toContain('"season": 2026');
  });

  it("writes the menu layout and the menu items of client.toml into the client values", () => {
    const repo = tempRepo();
    buildClient(repo);
    const menu = clientValuesOf(repo.site).menu;
    expect(menu).toEqual({
      layout: "hamburger",
      items: [
        { page: "home", label: "Home" },
        { package: "week" },
        { package: "rankings", label: "Power Rankings" },
        { package: "managers", label: "Managers" },
        { package: "analyzer", label: "Trade Analyzer" },
      ],
    });
  });

  it("gives a test client with the layout bar and no items a bar with Home, then the items of the package list (AT-16)", () => {
    const toml = [
      'packages = ["week", "waiver", "rankings"]',
      'timezone = "America/Los_Angeles"',
      "",
      "[seasons.2026]",
      'provider = "sleeper"',
      'league_id = "1"',
      "",
      "[menu]",
      'layout = "bar"',
      "",
    ].join("\n");
    const repo = tempRepo(toml, "bar-client");
    buildClient(repo);
    const values = clientValuesOf(repo.site);
    expect(values.menu).toEqual({
      layout: "bar",
      items: [{ page: "home" }, { package: "week" }, { package: "waiver" }, { package: "rankings" }],
    });
    expect(values.usageCode).toBeNull();
  });

  it("gives a client with no [menu] the hamburger, Home, and the items of the package list", () => {
    const toml = CPC_TOML.slice(0, CPC_TOML.indexOf("# Each item names"));
    const repo = tempRepo(toml);
    buildClient(repo);
    expect(clientValuesOf(repo.site).menu).toEqual({
      layout: "hamburger",
      items: [{ page: "home" }, { package: "week" }, { package: "rankings" }, { package: "managers" }, { package: "analyzer" }],
    });
  });

  it("copies only the published data of the client into public/, and drops a season of an earlier build", () => {
    const repo = tempRepo();
    published(repo.root, "cpc", "2026/week-06/page.json", '{"week":6}');
    published(repo.root, "other", "2026/week-07/page.json");
    mkdirSync(join(repo.site, "public", "2019"), { recursive: true });
    mkdirSync(join(repo.site, "public", "images"), { recursive: true });
    writeFileSync(join(repo.site, "public", "images", "logo.png"), "png");
    buildClient(repo);
    expect(readFileSync(join(repo.site, "public", "2026", "week-06", "page.json"), "utf8")).toBe('{"week":6}');
    expect(existsSync(join(repo.site, "public", "2026", "week-07"))).toBe(false);
    expect(existsSync(join(repo.site, "public", "2019"))).toBe(false);
    expect(existsSync(join(repo.site, "public", "images", "logo.png"))).toBe(true);
  });

  it("fails on a client folder that does not exist and names the folder", () => {
    const repo = tempRepo();
    expect(() => buildClient({ ...repo, slug: "nope" })).toThrow(/clients\/nope/);
  });

  it("writes the brand CSS of the client: the light set first, then the dark set under .dark", () => {
    const repo = tempRepo();
    buildClient(repo);
    const css = readFileSync(join(repo.site, "src", "generated", "brand.css"), "utf8");
    const theme = css.slice(css.indexOf("@theme static {"), css.indexOf(".dark {"));
    expect(theme).toContain("--color-page: #ffffff;");
    expect(theme).toContain("--color-ink: #1a1a1a;");
    expect(theme).toContain("--radius-card: 8px;");
    expect(css.slice(css.indexOf(".dark {"))).toContain("--color-page: #141414;");
  });

  it("fails on a brand with a missing base role and names the role and the file", () => {
    const repo = tempRepo(CPC_TOML, "cpc", { brand: CPC_BRAND.replace('muted = "#666666"\n', "") });
    expect(() => buildClient(repo)).toThrow(ClientBuildError);
    expect(() => buildClient(repo)).toThrow(/- light\.muted: is required/);
    expect(() => buildClient(repo)).toThrow(join(repo.root, "clients", "cpc", "brand.toml"));
  });

  it("fails on a brand with an unknown role and names the role", () => {
    const brand = CPC_BRAND.replace('[light]\n', '[light]\nhighlight = "#ffff00"\n');
    expect(() => buildClient(tempRepo(CPC_TOML, "cpc", { brand }))).toThrow(/- light\.highlight: is not a known key/);
  });

  it("fails on a brand with an unknown derived role and names the role", () => {
    const brand = CPC_BRAND.replace('[light.derived]\n', '[light.derived]\nglow = "#ffff00"\n');
    expect(() => buildClient(tempRepo(CPC_TOML, "cpc", { brand }))).toThrow(/- light\.derived\.glow: is not a known key/);
  });

  it("fails on a client with no brand.toml and names the file", () => {
    const repo = tempRepo();
    rmSync(join(repo.root, "clients", "cpc", "brand.toml"));
    expect(() => buildClient(repo)).toThrow(/No brand\.toml for the client cpc/);
  });

  it("writes the sets of the brand and the words of copy.toml into the client values", () => {
    const repo = tempRepo();
    buildClient(repo);
    const values = clientValuesOf(repo.site);
    expect(values.brand.sets).toEqual(["light", "dark"]);
    expect(values.copy).toEqual({
      siteName: "Cornerstone Fantasy Football League",
      masthead: "Cornerstone Fantasy Football League",
      tagline: "League Weekly",
    });
  });

  it("gives a brand with one dark set the dark set first and no .dark block (AT-10)", () => {
    const dark = CPC_BRAND.slice(CPC_BRAND.indexOf("[dark]"));
    const brand = CPC_BRAND.slice(0, CPC_BRAND.indexOf("[light]")) + dark;
    const repo = tempRepo(CPC_TOML, "cpc", { brand });
    buildClient(repo);
    expect(clientValuesOf(repo.site).brand.sets).toEqual(["dark"]);
    const css = readFileSync(join(repo.site, "src", "generated", "brand.css"), "utf8");
    expect(css).toContain("--color-page: #141414;");
    expect(css).not.toContain(".dark {");
  });

  it("copies the logo of assets/ into the site and names its src, and gives null with no logo", () => {
    const repo = tempRepo();
    mkdirSync(join(repo.root, "clients", "cpc", "assets"), { recursive: true });
    writeFileSync(join(repo.root, "clients", "cpc", "assets", "logo.png"), "png");
    buildClient(repo);
    expect(clientValuesOf(repo.site).brand.logo).toBe("/brand/logo.png");
    expect(readFileSync(join(repo.site, "public", "brand", "logo.png"), "utf8")).toBe("png");
    rmSync(join(repo.root, "clients", "cpc", "assets", "logo.png"));
    buildClient(repo);
    expect(clientValuesOf(repo.site).brand.logo).toBeNull();
    // The logo of the earlier build goes, so the export never holds the logo of another client.
    expect(existsSync(join(repo.site, "public", "brand", "logo.png"))).toBe(false);
  });

  it("copies each font file of assets/fonts/ into the site and writes its @font-face", () => {
    const face = '\n[[fonts.faces]]\nfamily = "Inter"\nfile = "Inter-Bold.woff2"\nweight = "700"\n';
    const brand = CPC_BRAND.replace("[light]\n", `${face}\n[light]\n`);
    const repo = tempRepo(CPC_TOML, "cpc", { brand });
    mkdirSync(join(repo.root, "clients", "cpc", "assets", "fonts"), { recursive: true });
    writeFileSync(join(repo.root, "clients", "cpc", "assets", "fonts", "Inter-Bold.woff2"), "font");
    buildClient(repo);
    expect(readFileSync(join(repo.site, "public", "brand", "fonts", "Inter-Bold.woff2"), "utf8")).toBe("font");
    const css = readFileSync(join(repo.site, "src", "generated", "brand.css"), "utf8");
    expect(css).toContain('src: url("/brand/fonts/Inter-Bold.woff2") format("woff2");');
  });

  it("fails on a font face with no file in assets/fonts/ and names the file", () => {
    const face = '\n[[fonts.faces]]\nfamily = "Inter"\nfile = "Inter-Bold.woff2"\n';
    const repo = tempRepo(CPC_TOML, "cpc", { brand: CPC_BRAND.replace("[light]\n", `${face}\n[light]\n`) });
    expect(() => buildClient(repo)).toThrow(/Inter-Bold\.woff2/);
  });

  it("fails on a copy.toml with no site name and names the key", () => {
    const repo = tempRepo(CPC_TOML, "cpc", { copy: CPC_COPY.replace(/^site_name = .*\n/m, "") });
    expect(() => buildClient(repo)).toThrow(/- site_name: is required/);
  });
});
