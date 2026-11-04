/**
 * The types of the files that the client build writes into src/generated/ from clients/$CLIENT/client.toml.
 * The site reads one client per build, so a value that changes with the league comes from these files and not the env.
 */

/* A package that a client takes or omits. league, facts, and design are in every client, so the list never names them. */
export type PackageName = "week" | "rankings" | "managers" | "waiver" | "analyzer";

/* The values of the client that the site reads. */
export type ClientValues = {
  slug: string;
  packages: PackageName[];
  // The latest season of the client. The teams and analyze routes of the API read it.
  season: number;
  // The GoatCounter site code. With none, the layout loads no count script.
  usageCode: string | null;
  // The trade finder of the analyzer.
  finder: boolean;
};

/* The menu href of each package of the client. A package with no page to link yet gives null, so the menu has no entry. */
export type MenuHrefs = Partial<Record<PackageName, () => string | null>>;
