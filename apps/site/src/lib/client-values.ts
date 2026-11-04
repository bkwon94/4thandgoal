/**
 * The types of the files that the client build writes into src/generated/ from clients/$CLIENT/client.toml.
 * The site reads one client per build, so a value that changes with the league comes from these files and not the env.
 */

import type { ReactNode } from "react";
import type { BrandSets } from "@cpc/design/lib/theme";
import type { Destination, MenuLayout } from "@cpc/design/shell/menu";

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
  // The menu of [menu] in client.toml. The client build fills the items from the package list when client.toml gives none.
  menu: ClientMenu;
  // The sets of brand.toml in paint order, and the src of the logo in assets/, or null with no logo.
  brand: { sets: BrandSets; logo: string | null };
  // The words of copy.toml.
  copy: { siteName: string; masthead: string; tagline: string };
};

/* One menu item: the home page or one package of the list. With no label, the item takes the label of its package. */
export type MenuItem = { page: "home"; label?: string } | { package: PackageName; label?: string };

/* The layout of the menu and its items, in the order of the menu. */
export type ClientMenu = { layout: MenuLayout; items: MenuItem[] };

/* The menu link of each package of the client: its label and its href. A package with no page to link yet gives null,
   so the menu has no entry. */
export type MenuLinks = Partial<Record<PackageName, () => Destination | null>>;

/* One section that a package gives the home page: a row of the Tools chapter, a chapter beside the Tools chapter, or a
   chapter under the two. The page gives each chapter its stagger step, and the first row of the tools its first flag.
   The head renders before the masthead, as the first child of the page, for a part that renders nothing, such as a prefetch. */
export type HomeSection = (
  | { place: "tools"; row: (first: boolean) => ReactNode }
  | { place: "beside" | "below"; chapter: (step: number) => ReactNode }
) & { head?: ReactNode };

/* The home section of each package of the client, in the order of the page. A package with no data to show gives null,
   so the page shows no empty section. The registry of the client build lists only the packages of the client. */
export type HomeSections = (() => HomeSection | null)[];
