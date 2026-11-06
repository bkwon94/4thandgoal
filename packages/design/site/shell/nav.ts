/**
 * The destinations of the shell and the rules that pick the open one: the item to mark and the week of the week chip.
 * It holds no markup, so the server components of the shell and the app layer share it.
 */

/* One place a link goes. The href carries the base path, because every link is a plain anchor. */
export type Destination = { label: string; href: string };

/* The kind of a destination. The dock picks the icon of each item from it. */
export type NavKind = "home" | "week" | "rankings" | "managers" | "analyzer" | "waiver" | "midseason";

/* One destination of the menu. The pill bar shows the full label, and the dock shows the short label under the icon. */
export type NavItem = Destination & { kind: NavKind; short: string };

/* One published week of the season, for the week chip and the strip of weeks. */
export type WeekLink = { number: number; href: string };

/* The menu of the shell: the destinations in the order of client.toml, and the published weeks, newest first. */
export type SiteMenu = { items: NavItem[]; weeks: WeekLink[] };

/* The home link and the logo src of the brand, each with the base path. A brand with no logo gives null,
   and the top band shows its title as text. */
export type Brand = { home: string; logo: string | null };

/* The week that the open page is about: the week of a week page or of a page under it, else none. */
function weekOfPage(weeks: WeekLink[], pageHref?: string): WeekLink | undefined {
  return pageHref === undefined ? undefined : weeks.find((week) => pageHref.startsWith(week.href));
}

/* The week of the week chip: the week of the open page, else the latest week. A client with no week gives none. */
export function chipWeek(weeks: WeekLink[], pageHref?: string): WeekLink | undefined {
  return weekOfPage(weeks, pageHref) ?? weeks[0];
}

/* The href of the item to mark as the open destination, or none.
   Home matches only its own page, because every href starts with the home href. Another item matches its page and each
   page under it, such as one manager under Managers, and the longest match wins, so the waiver page of a week marks
   Waiver and not the week. The week item stands for every week, so the page of an older week marks it too. */
export function currentHref(items: NavItem[], weeks: WeekLink[], pageHref?: string): string | undefined {
  if (pageHref === undefined) return undefined;
  let best: NavItem | undefined;
  for (const item of items) {
    const match = item.kind === "home" ? item.href === pageHref : pageHref.startsWith(item.href);
    if (match && (best === undefined || item.href.length > best.href.length)) best = item;
  }
  if (best !== undefined && best.kind !== "week") return best.href;
  const week = items.find((item) => item.kind === "week");
  return week !== undefined && weekOfPage(weeks, pageHref) !== undefined ? week.href : best?.href;
}

/* The chip label of a week: "WK 08". The two digits keep every chip the same width. */
export function weekChipLabel(number: number): string {
  return `WK ${String(number).padStart(2, "0")}`;
}
