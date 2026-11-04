/**
 * The client build: it reads clients/$CLIENT/client.toml, checks it, and writes the routes, the registry, and the client values.
 * It copies only that client's published data into public/. The prebuild step runs it, and the fast check runs it for cpc.
 */
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import Ajv from "ajv";
import { parse } from "smol-toml";

/* The repo root, two folders above the site app. */
export const REPO_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "..");
/* The JSON Schema that the pipeline exports from its pydantic model. "make schema" in apps/pipeline rewrites it. */
export const SCHEMA_FILE = join("apps", "pipeline", "src", "cornerstone", "client.schema.json");

/* A client that the build cannot build. The message names the file and the bad value, with no stack. */
export class ClientBuildError extends Error {}

/* One plain line per broken rule: the key path and the reason, with no ajv text. The pipeline check words its lines the same way. */
function ruleLine(error) {
  const where = error.instancePath.split("/").filter(Boolean);
  if (error.keyword === "additionalProperties") {
    return `- ${[...where, error.params.additionalProperty].join(".")}: is not a known key`;
  }
  if (error.keyword === "required") return `- ${[...where, error.params.missingProperty].join(".")}: is required`;
  return `- ${where.join(".") || "the file"}: ${error.message}`;
}

/* The checked values of clients/<slug>/client.toml. The JSON Schema checks each key and value, and an unknown key fails,
   so a typo never passes as a default. */
export function readClient(root, slug) {
  const folder = join(root, "clients", slug);
  const file = join(folder, "client.toml");
  if (!existsSync(file)) throw new ClientBuildError(`No client.toml for the client ${slug} at ${file}.`);
  let values;
  try {
    values = parse(readFileSync(file, "utf8"));
  } catch (error) {
    throw new ClientBuildError(`${file} is not valid TOML: ${error.message}`);
  }
  const schema = JSON.parse(readFileSync(join(root, SCHEMA_FILE), "utf8"));
  const check = new Ajv({ allErrors: true }).compile(schema);
  if (!check(values)) {
    // An anyOf branch that fails adds a line for each branch, so the check keeps each line once.
    const lines = [...new Set(check.errors.map(ruleLine))];
    throw new ClientBuildError(`${file} breaks a rule:\n${lines.join("\n")}`);
  }
  // A JSON Schema cannot tie a menu item to the package list, so this rule is code, as in the pydantic model.
  const omitted = (values.menu?.items ?? [])
    .filter((item) => item.package !== undefined && !values.packages.includes(item.package))
    .map((item) => `- menu.items: The menu item for ${item.package} names a package that is not in the package list.`);
  if (omitted.length > 0) throw new ClientBuildError(`${file} breaks a rule:\n${omitted.join("\n")}`);
  return values;
}

/* The folders that the build owns. It empties each one first, so a route of the last client never stays behind. */
const ROUTE_GROUP = join("src", "app", "(client)");
const GENERATED_DIR = join("src", "generated");

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
};

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

/* The registry of import lines. Only a package of the list gets an import line, so an omitted package is absent from
   the bundle. The map has an explicit type, so a client with no package still type-checks. */
function registryText(slug, values) {
  return [
    headerLine(slug),
    `import type { MenuLinks } from "@/lib/client-values";`,
    ...values.packages.map((name) => `import { menuLink as ${name}MenuLink } from "@/app/_routes/${name}/menu";`),
    "",
    "/* The menu link of each package of the client. */",
    "export const menuLinks: MenuLinks = {",
    ...values.packages.map((name) => `  ${name}: ${name}MenuLink,`),
    "};",
    "",
  ].join("\n");
}

/* The menu of the client. The layout defaults to the hamburger. With no items, the menu takes the home page, then the
   package list in its order, because Brian chose Home as the first item of a default menu. */
function menuOf(values) {
  return {
    layout: values.menu?.layout ?? "hamburger",
    items: values.menu?.items ?? [{ page: "home" }, ...values.packages.map((name) => ({ package: name }))],
  };
}

/* The values of the client that the site reads. The site season is the latest season of the client. */
function clientValuesText(slug, values) {
  const seasons = Object.keys(values.seasons).map(Number);
  const site = {
    slug,
    packages: values.packages,
    season: Math.max(...seasons),
    usageCode: values.usage_code ?? null,
    finder: values.values?.analyzer?.finder ?? false,
    menu: menuOf(values),
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

function writeFile(file, text) {
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, text);
}

/* Build the client `slug`: check its client.toml, then write the generated files of the site app `site`. */
export function buildClient({ slug, root = REPO_ROOT, site = join(root, "apps", "site") }) {
  const values = readClient(root, slug);
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
  writeFile(join(site, GENERATED_DIR, "client-values.ts"), clientValuesText(slug, values));
  copyPublished(published, join(site, "public"));
  return values;
}

function main() {
  const slug = process.env.CLIENT;
  if (!slug) {
    throw new ClientBuildError(
      "Set CLIENT to the slug of one folder under clients/. Example: CLIENT=cpc pnpm build",
    );
  }
  buildClient({ slug });
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
