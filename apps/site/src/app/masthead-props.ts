/**
 * Builds the masthead props that every page shares: the title, the brand, and the menu, from client.toml, brand.toml, and copy.toml.
 * It reads public/ at build time in the app layer, so the masthead itself reads no file and builds no route.
 */
import { paintOf } from "@cpc/design/lib/theme";
import type { Brand, Destination, SiteMenu } from "@cpc/design/shell/menu";
import { clientValues } from "@/generated/client-values";
import { menuLinks } from "@/generated/registry";
import type { MenuItem, MenuLinks } from "@/lib/client-values";
import { listWeekSummaries } from "@/lib/data/week-data";
import { homeHref, logoSrc } from "@/lib/routes";

/* One destination per menu item, in the order of the items. An item takes the label of its package unless it sets
   its own. A package that the registry omits, or with no page to link yet, gives no destination. */
export function menuPages(items: MenuItem[], links: MenuLinks, home: string): Destination[] {
  return items.flatMap((item) => {
    if ("page" in item) return [{ label: item.label ?? "Home", href: home }];
    const link = links[item.package]?.();
    return link ? [{ label: item.label ?? link.label, href: link.href }] : [];
  });
}

export function mastheadProps(): { title: string; brand: Brand; menu: SiteMenu } {
  // The registry holds only the packages of the client, so an omitted package has no link and no code in the bundle.
  const home = homeHref();
  // The newest week is the week link of the menu, so the past weeks are the rest. A client with no week lists none.
  const pastWeeks = clientValues.packages.includes("week")
    ? listWeekSummaries()
        .slice(1)
        .map((summary) => ({ label: `Week ${summary.number}`, href: summary.href }))
    : [];
  return {
    title: clientValues.copy.masthead,
    brand: { home, logo: logoSrc(clientValues.brand.logo), themeButton: paintOf(clientValues.brand.sets).themeButton },
    menu: {
      layout: clientValues.menu.layout,
      pages: menuPages(clientValues.menu.items, menuLinks, home),
      pastWeeks,
    },
  };
}
