/**
 * The client build: it reads clients/$CLIENT/client.toml, brand.toml, and copy.toml, checks them, and writes the routes,
 * the registry, the client values, the brand CSS, and the wrangler config of the Worker. It copies only that client's
 * published data and assets into public/.
 * The prebuild step runs it, and the fast check runs it for cpc.
 */
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import Ajv from "ajv";
import { parse } from "smol-toml";
import { BRAND_SCHEMA, brandCss, COPY_SCHEMA, setsOf } from "@cpc/design/brand/brand.ts";

/* The repo root, two folders above the site app. */
export const REPO_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "..");
/* The site app that the script writes into. A build for another root still writes the generated files here. */
const SITE_DIR = join(dirname(fileURLToPath(import.meta.url)), "..");

/* The root that holds clients/ and the exported schemas: the repo, or the root that CLIENT_ROOT names. A test client
   then builds from a temp folder, and no test folder goes under clients/. */
export function clientRoot(env) {
  return env.CLIENT_ROOT ?? REPO_ROOT;
}
/* The JSON Schema of the kernel keys, which the league package exports from its pydantic model. "make schema" in
   packages/league/python rewrites it. */
export const SCHEMA_FILE = join("packages", "league", "python", "src", "league", "client.schema.json");

/* The JSON Schema of the package values of the package `name`, which the package exports from its pydantic model.
   "make schema" in packages/<name>/python rewrites it. */
export function valuesSchemaFile(name) {
  return join("packages", name, "python", "src", name, "values.schema.json");
}

/* A client that the build cannot build. The message names the file and the bad value, with no stack. */
export class ClientBuildError extends Error {}

/* One plain line per broken rule: the key path under `prefix` and the reason, with no ajv text. The pipeline check
   words its lines the same way. */
function ruleLine(error, prefix = []) {
  const where = [...prefix, ...error.instancePath.split("/").filter(Boolean)];
  if (error.keyword === "additionalProperties") {
    return `- ${[...where, error.params.additionalProperty].join(".")}: is not a known key`;
  }
  if (error.keyword === "required") return `- ${[...where, error.params.missingProperty].join(".")}: is required`;
  return `- ${where.join(".") || "the file"}: ${error.message}`;
}

/* The checked values of the TOML file `name` of the client `slug`. The JSON Schema checks each key and value, and an
   unknown key fails, so a typo never passes as a default. */
function readChecked(root, slug, name, schema) {
  const file = join(root, "clients", slug, name);
  if (!existsSync(file)) throw new ClientBuildError(`No ${name} for the client ${slug} at ${file}.`);
  let values;
  try {
    values = parse(readFileSync(file, "utf8"));
  } catch (error) {
    throw new ClientBuildError(`${file} is not valid TOML: ${error.message}`);
  }
  const lines = schemaLines(schema, values);
  if (lines.length > 0) throw new ClientBuildError(`${file} breaks a rule:\n${lines.join("\n")}`);
  return values;
}

/* One plain line per rule of `schema` that `values` breaks, each key path under `prefix`. */
function schemaLines(schema, values, prefix = []) {
  const check = new Ajv({ allErrors: true }).compile(schema);
  if (check(values)) return [];
  // An anyOf branch that fails adds a line for each branch, so the check keeps each line once.
  return [...new Set(check.errors.map((error) => ruleLine(error, prefix)))];
}

/* One plain line per broken rule of the [values.<package>] tables. A table names league or a package of the list, and
   the schema of its package checks it, as the model of each package does in the pipeline. */
function tableLines(root, values) {
  const taken = ["league", ...values.packages];
  const lines = [];
  for (const [name, table] of Object.entries(values.values ?? {})) {
    if (!taken.includes(name)) {
      lines.push(`- values.${name}: names a package that is not in the package list`);
      continue;
    }
    const schema = JSON.parse(readFileSync(join(root, valuesSchemaFile(name)), "utf8"));
    lines.push(...schemaLines(schema, table, ["values", name]));
  }
  return lines;
}

/* The checked values of clients/<slug>/client.toml: the kernel keys with the schema of league, and each
   [values.<package>] table with the schema of its package. */
export function readClient(root, slug) {
  const file = join(root, "clients", slug, "client.toml");
  const values = readChecked(root, slug, "client.toml", JSON.parse(readFileSync(join(root, SCHEMA_FILE), "utf8")));
  // A JSON Schema cannot tie a menu item to the package list, so this rule is code, as in the pydantic model.
  const omitted = (values.menu?.items ?? [])
    .filter((item) => item.package !== undefined && !values.packages.includes(item.package))
    .map((item) => `- menu.items: The menu item for ${item.package} names a package that is not in the package list.`);
  const lines = [...omitted, ...tableLines(root, values)];
  if (lines.length > 0) throw new ClientBuildError(`${file} breaks a rule:\n${lines.join("\n")}`);
  return values;
}

/* The checked values of clients/<slug>/brand.toml, with the schema of the design package. */
export function readBrand(root, slug) {
  return readChecked(root, slug, "brand.toml", BRAND_SCHEMA);
}

/* The checked values of clients/<slug>/copy.toml: the site name, the masthead text, and the tagline. */
export function readCopy(root, slug) {
  return readChecked(root, slug, "copy.toml", COPY_SCHEMA);
}

/* The folders that the build owns. It empties each one first, so a route of the last client never stays behind. */
const ROUTE_GROUP = join("src", "app", "(client)");
const GENERATED_DIR = join("src", "generated");
/* The logo of the client, copied from its assets/. The site serves it at /brand/. */
const BRAND_DIR = join("public", "brand");

/* The logo of a client is the one file named logo in its assets/. A client with none shows its site name as text. */
const LOGO = /^logo\.(png|svg|webp|jpg)$/;

/* A season folder name, such as 2026. */
const SEASON = /^\d{4}$/;

/* Any file under `dir` that matches `test`. A missing folder holds none. */
function hasFile(dir, test) {
  if (!existsSync(dir)) return false;
  return readdirSync(dir, { recursive: true }).some((path) => test(String(path)));
}

/* The latest season folder of the published data, or null when it holds none. */
function latestSeasonDir(publishedDir) {
  if (!existsSync(publishedDir)) return null;
  const seasons = readdirSync(publishedDir).filter((name) => SEASON.test(name)).sort();
  return seasons.length > 0 ? join(publishedDir, seasons.at(-1)) : null;
}


/* The route files of each package. A route file re-exports its page from src/app/_routes/, which Next does not route.
   A static export fails on a dynamic route with no params, so a dynamic route needs the published file that gives its
   params. `dynamicParams` stays a literal in the route file, because Next reads the segment config with no import. */
const ROUTES = {
  week: [
    {
      path: "[season]/[week]/page.tsx",
      source: "@/app/_routes/week/page",
      exports: ["default", "generateStaticParams", "generateMetadata"],
      dynamic: true,
      needs: (published) => hasFile(published, (path) => path.endsWith("page.json")),
    },
  ],
  rankings: [{ path: "rankings/page.tsx", source: "@/app/_routes/rankings/page", exports: ["default", "metadata"] }],
  managers: [
    {
      path: "[season]/managers/page.tsx",
      source: "@/app/_routes/managers/page",
      exports: ["default", "generateStaticParams", "metadata"],
      dynamic: true,
      needs: managersFile,
    },
    {
      path: "[season]/managers/[roster]/page.tsx",
      source: "@/app/_routes/managers/manager-page",
      exports: ["default", "generateStaticParams", "generateMetadata"],
      dynamic: true,
      needs: managersFile,
    },
  ],
  waiver: [
    {
      path: "[season]/[week]/waiver/page.tsx",
      source: "@/app/_routes/waiver/page",
      exports: ["default", "generateStaticParams", "metadata"],
      dynamic: true,
      needs: (published) => hasFile(published, (path) => path.endsWith("waiver.json")),
    },
  ],
  analyzer: [{ path: "analyze/page.tsx", source: "@/app/_routes/analyzer/page", exports: ["default", "metadata"] }],
  // The sim has no page of its own. The report page mounts its replay.
  sim: [],
  // The egg board renders in the browser from the API, so it needs no published file.
  eggs: [{ path: "eggs/page.tsx", source: "@/app/_routes/eggs/page", exports: ["default", "metadata"] }],
  midseason: [
    {
      path: "midseason/[season]/page.tsx",
      source: "@/app/_routes/midseason/page",
      exports: ["default", "generateStaticParams", "generateMetadata"],
      dynamic: true,
      needs: (published) => hasFile(published, (path) => path.endsWith("midseason.json")),
    },
  ],
};

/* The home tool of each package that has one: a row of the Tools chapter of the home page, in the order of the chapter.
   The registry imports it only for a package of the list, so the home page of a client that omits the package holds
   none of its code. The order is fixed here and not by the package list, so the order of client.toml never moves a row. */
const HOME_TOOLS = { analyzer: "@/app/_routes/analyzer/home", managers: "@/app/_routes/managers/home" };

/* The part that a package mounts on every page, such as the egg hunt. The registry imports it only for a package of the
   list, so the bundle of a client that omits the package holds none of its code. */
const PAGE_PARTS = { eggs: "@/app/_routes/eggs/hunt" };

/* The button that a package puts in the top band of every page, such as the egg button, just before the theme button.
   The registry imports it only for a package of the list, so the top band of a client that omits the package holds none. */
const BAND_PARTS = { eggs: "@/app/_routes/eggs/band" };

/* The strip that a package puts under the top band of the home page, such as the egg banner. The registry imports it
   only for a package of the list, so the home page of a client that omits the package holds none. */
const HOME_BANNERS = { eggs: "@/app/_routes/eggs/home-banner" };

/* The managers routes build only for the latest season, so its managers file gives their params. */
function managersFile(published) {
  const season = latestSeasonDir(published);
  return season !== null && existsSync(join(season, "managers.json"));
}

function headerLine(slug) {
  return `// GENERATED by apps/site/scripts/client-build.mjs from clients/${slug}/client.toml. Do not edit.`;
}

function routeText(slug, route) {
  const lines = [headerLine(slug), `export { ${route.exports.join(", ")} } from "${route.source}";`];
  if (route.dynamic) {
    lines.push("// The export is static, so a param with no published file at build time has no page.");
    lines.push("export const dynamicParams = false;");
  }
  return `${lines.join("\n")}\n`;
}

/* The packages that give the home page its parts. Each one has src/app/_routes/<package>/home.tsx, and each part
   names its own place on the page. The order is fixed here and not by the package list, so the order of client.toml
   never moves a part. */
const HOME_SECTIONS = ["midseason", "rankings", "week"];

/* The registry of import lines. Only a package of the list gets an import line, so an omitted package is absent from
   the bundle. The map and the list have an explicit type, so a client with no package still type-checks. */
function registryText(slug, values) {
  const tools = Object.keys(HOME_TOOLS).filter((name) => values.packages.includes(name));
  const home = HOME_SECTIONS.filter((name) => values.packages.includes(name));
  const parts = Object.keys(PAGE_PARTS).filter((name) => values.packages.includes(name));
  const band = Object.keys(BAND_PARTS).filter((name) => values.packages.includes(name));
  const banners = Object.keys(HOME_BANNERS).filter((name) => values.packages.includes(name));
  return [
    headerLine(slug),
    `import type { BandPart, HomeBanner, HomeSections, HomeTool, MenuLinks, PagePart } from "@/lib/client-values";`,
    ...values.packages.map((name) => `import { menuLink as ${name}MenuLink } from "@/app/_routes/${name}/menu";`),
    ...tools.map((name) => `import { HomeTool as ${name}HomeTool } from "${HOME_TOOLS[name]}";`),
    ...home.map((name) => `import { homeSection as ${name}HomeSection } from "@/app/_routes/${name}/home";`),
    ...parts.map((name) => `import { PagePart as ${name}PagePart } from "${PAGE_PARTS[name]}";`),
    ...band.map((name) => `import { BandPart as ${name}BandPart } from "${BAND_PARTS[name]}";`),
    ...banners.map((name) => `import { HomeBanner as ${name}HomeBanner } from "${HOME_BANNERS[name]}";`),
    "",
    "/* The menu link of each package of the client. */",
    "export const menuLinks: MenuLinks = {",
    ...values.packages.map((name) => `  ${name}: ${name}MenuLink,`),
    "};",
    "",
    "/* The home tool of each package of the client that has one, in the order of the Tools chapter. */",
    `export const homeTools: HomeTool[] = [${tools.map((name) => `${name}HomeTool`).join(", ")}];`,
    "",
    "/* The home chapter of each package of the client, in the order of the home page. */",
    "export const homeSections: HomeSections = [",
    ...home.map((name) => `  ${name}HomeSection,`),
    "];",
    "",
    "/* The part of each package of the client that every page mounts. */",
    `export const pageParts: PagePart[] = [${parts.map((name) => `${name}PagePart`).join(", ")}];`,
    "",
    "/* The button of each package of the client in the top band, just before the theme button. */",
    `export const bandParts: BandPart[] = [${band.map((name) => `${name}BandPart`).join(", ")}];`,
    "",
    "/* The strip of each package of the client under the top band of the home page. */",
    `export const homeBanners: HomeBanner[] = [${banners.map((name) => `${name}HomeBanner`).join(", ")}];`,
    "",
  ].join("\n");
}

/* The menu of the client. The look owns the navigation, so the menu holds only its items (ADR 0024). With no items, the
   menu takes the home page, then the package list in its order, because Brian chose Home as the first item of a default menu. */
function menuOf(values) {
  return {
    items: values.menu?.items ?? [{ page: "home" }, ...values.packages.map((name) => ({ package: name }))],
  };
}

/* The values of the client that the site reads. The site season is the latest season of the client. */
function clientValuesText(slug, values, brand, copy) {
  const seasons = Object.keys(values.seasons).map(Number);
  const site = {
    slug,
    packages: values.packages,
    season: Math.max(...seasons),
    usageCode: values.usage_code ?? null,
    finder: values.values?.analyzer?.finder ?? false,
    menu: menuOf(values),
    brand,
    copy: { siteName: copy.site_name, masthead: copy.masthead, tagline: copy.tagline },
  };
  return [
    headerLine(slug),
    `import type { ClientValues } from "@/lib/client-values";`,
    "",
    `export const clientValues: ClientValues = ${JSON.stringify(site, null, 2)};`,
    "",
  ].join("\n");
}

/* Copy the season folders of the client into public/. Each season folder of an earlier build goes first, so the
   export never holds the data of another client. The shared images of public/ stay. */
function copyPublished(published, publicDir) {
  mkdirSync(publicDir, { recursive: true });
  for (const name of readdirSync(publicDir)) {
    if (SEASON.test(name)) rmSync(join(publicDir, name), { recursive: true, force: true });
  }
  if (!existsSync(published)) return;
  for (const name of readdirSync(published)) {
    if (SEASON.test(name)) cpSync(join(published, name), join(publicDir, name), { recursive: true });
  }
}

/* Copy the logo from the assets/ of the client into public/brand/. The folder of an earlier build goes first, so the
   export never holds the logo of another client. Returns the src of the logo, or null with no logo. */
function copyAssets(root, slug, site) {
  const assets = join(root, "clients", slug, "assets");
  const target = join(site, BRAND_DIR);
  rmSync(target, { recursive: true, force: true });
  const logo = existsSync(assets) ? readdirSync(assets).filter((name) => LOGO.test(name)).sort()[0] : undefined;
  if (logo === undefined) return null;
  mkdirSync(target, { recursive: true });
  cpSync(join(assets, logo), join(target, logo));
  return `/brand/${logo}`;
}

/* The wrangler config of the Worker of the client `slug`. The Worker name is the slug. It serves the static export in
   out/ with no Worker script, and the 404.html of the export answers each unknown path. The config declares no route:
   Brian adds the Custom Domain <slug>.4thandgoal.app in the Cloudflare dashboard. */
function wranglerText(slug) {
  const config = {
    name: slug,
    // A fixed date keeps the runtime of the Worker the same from deploy to deploy.
    compatibility_date: "2026-11-01",
    assets: { directory: "./out", not_found_handling: "404-page" },
  };
  return `${headerLine(slug)}\n${JSON.stringify(config, null, 2)}\n`;
}

function writeFile(file, text) {
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, text);
}

/* Build the client `slug`: check its client.toml, then write the generated files of the site app `site`. */
export function buildClient({ slug, root = REPO_ROOT, site = join(root, "apps", "site") }) {
  const values = readClient(root, slug);
  const brand = readBrand(root, slug);
  const copy = readCopy(root, slug);
  const published = join(root, "clients", slug, "published");
  rmSync(join(site, ROUTE_GROUP), { recursive: true, force: true });
  rmSync(join(site, GENERATED_DIR), { recursive: true, force: true });
  for (const name of values.packages) {
    for (const route of ROUTES[name]) {
      if (route.needs && !route.needs(published)) continue;
      writeFile(join(site, ROUTE_GROUP, route.path), routeText(slug, route));
    }
  }
  writeFile(join(site, GENERATED_DIR, "registry.ts"), registryText(slug, values));
  const logo = copyAssets(root, slug, site);
  writeFile(join(site, GENERATED_DIR, "client-values.ts"), clientValuesText(slug, values, { sets: setsOf(brand), logo }, copy));
  writeFile(join(site, GENERATED_DIR, "brand.css"), brandCss(brand, { source: `clients/${slug}/brand.toml` }));
  copyPublished(published, join(site, "public"));
  writeFile(join(site, "wrangler.jsonc"), wranglerText(slug));
  return values;
}

function main() {
  const slug = process.env.CLIENT;
  if (!slug) {
    throw new ClientBuildError(
      "Set CLIENT to the slug of one folder under clients/. Example: CLIENT=cpc pnpm build",
    );
  }
  buildClient({ slug, root: clientRoot(process.env), site: SITE_DIR });
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  try {
    main();
  } catch (error) {
    if (!(error instanceof ClientBuildError)) throw error;
    console.error(`client build failed: ${error.message}`);
    process.exit(1);
  }
}
