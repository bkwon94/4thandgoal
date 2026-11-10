/**
 * The types of the files that the client build writes into src/generated/ from clients/$CLIENT/client.toml.
 * The site reads one client per build, so a value that changes with the league comes from these files and not the env.
 */

import type { ComponentType } from "react";
import type { BrandSets } from "@cpc/design/lib/theme";
import type { Destination } from "@cpc/design/shell/nav";

/* A package that a client takes or omits. league, facts, and design are in every client, so the list never names them. */
export type PackageName = "week" | "rankings" | "managers" | "waiver" | "analyzer" | "sim" | "midseason" | "eggs";

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

/* The items of the menu, in the order of the menu. The look owns the navigation, so a client sets no layout (ADR 0024). */
export type ClientMenu = { items: MenuItem[] };

/* The menu link of each package of the client: its label and its href. A package with no page to link yet gives null,
   so the menu has no entry. */
export type MenuLinks = Partial<Record<PackageName, () => Destination | null>>;

/* The part of a package that every page mounts, such as the egg hunt. */
export type PagePart = ComponentType;

/* The button of a package in the top band of every page, such as the egg button. */
export type BandPart = ComponentType;

/* The strip of a package under the top band of the home page, such as the egg banner. */
export type HomeBanner = ComponentType;
