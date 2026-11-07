/**
 * Builds the shell props of every page from client.toml, brand.toml, and copy.toml: the title, the brand, the menu, and the band buttons.
 * It reads public/ at build time in the app layer, so the shell itself reads no file and builds no route.
 */
import type { Brand, NavItem, NavKind, SiteMenu } from "@cpc/design/shell/nav";
import { clientValues } from "@/generated/client-values";
import { createElement, type ReactNode } from "react";
import { bandParts, menuLinks } from "@/generated/registry";
import type { ClientValues, MenuItem, MenuLinks } from "@/lib/client-values";
import { listWeekSummaries } from "@/lib/data/week-data";
import { homeHref, logoSrc } from "@/lib/routes";

/* The short label of each package in the dock, where five items share the width of a phone. The week item keeps
   the label of its package, "Week N", and the pill bar shows the full label of each item. The dock leaves out
   the midseason item, so its short label serves only a menu with no pill bar. */
const SHORT: Record<Exclude<NavKind, "home" | "week">, string> = {
  midseason: "Report",
  rankings: "Rankings",
  managers: "Managers",
  analyzer: "Trade",
  waiver: "Waiver",
};

/* One destination per menu item, in the order of the items. An item takes the label of its package unless it sets
   its own. A package that the registry omits, or with no page to link yet, gives no destination. */
export function menuPages(items: MenuItem[], links: MenuLinks, home: string): NavItem[] {
  return items.flatMap((item): NavItem[] => {
    if ("page" in item) return [{ kind: "home", label: item.label ?? "Home", short: "Home", href: home }];
    // The sim adds no menu item and no dock item (midseason PRD), so it has no kind.
    if (item.package === "sim") return [];
    // The egg board is not a menu item, so the dock keeps its five items. The egg button of the top band opens it.
    if (item.package === "eggs") return [];
    // The midseason report adds no menu item yet: a sixth item overflows the pill bar of CPC at 1280px. The home
    // takeover and the report tile link to the report.
    if (item.package === "midseason") return [];
    const link = links[item.package]?.();
    if (!link) return [];
    const short = item.package === "week" ? link.label : SHORT[item.package];
    return [{ kind: item.package, label: item.label ?? link.label, short, href: link.href }];
  });
}

/* The metadata title of a page: the page name, then the site name of copy.toml. The home page gives no page name. */
export function pageTitle(copy: ClientValues["copy"] = clientValues.copy, page?: string): string {
  return page ? `${page} · ${copy.siteName}` : copy.siteName;
}

/* The subtitle of the week page: the tagline of copy.toml. */
export function weekSubtitle(): string {
  return clientValues.copy.tagline;
}

export function shellProps(): { title: string; brand: Brand; menu: SiteMenu; actions: ReactNode } {
  // The registry holds only the packages of the client, so an omitted package has no link and no code in the bundle.
  const home = homeHref();
  // Every published week, newest first, for the week chip and the strip. A client with no week lists none.
  const weeks = clientValues.packages.includes("week")
    ? listWeekSummaries().map((summary) => ({ number: summary.number, href: summary.href }))
    : [];
  return {
    title: clientValues.copy.masthead,
    brand: { home, logo: logoSrc(clientValues.brand.logo) },
    menu: { items: menuPages(clientValues.menu.items, menuLinks, home), weeks },
    // The button of each package of the client, such as the egg button. The registry lists only the packages of the client.
    actions: bandParts.map((Part, index) => createElement(Part, { key: index })),
  };
}
