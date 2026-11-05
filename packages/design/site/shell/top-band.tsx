/**
 * The shell of every page: the top band with the brand mark, the pill bar, the week chip, and the theme button,
 * and the dock at the bottom of a phone and a tablet. The top band stays on screen at every scroll.
 */
import type { ReactNode } from "react";
import { Dock } from "./dock";
import { chipWeek, currentHref, type Brand, type SiteMenu } from "./nav";
import { PillBar } from "./pill-bar";
import { ThemeButton } from "./theme-button";
import { WeekChip } from "./week-chip";

type TopBandProps = {
  // The site name of copy.toml. It names the home link. The app layer passes it, so the shell names no league.
  title: string;
  // The home link and the logo of the brand, each with the base path.
  brand: Brand;
  // The destinations and the published weeks. The app layer builds them from client.toml and the published data.
  menu: SiteMenu;
  // The href of the open page, with the base path. A static export cannot read the request path, so each page passes its own.
  // A page that is no destination, such as the 404 page, passes none, and no item is marked.
  pageHref?: string;
  // The head of a page with no hero, such as its week line, under the band. A page with a hero passes none.
  children?: ReactNode;
};

export function TopBand({ title, brand, menu, pageHref, children }: TopBandProps) {
  const current = currentHref(menu.items, menu.weeks, pageHref);
  const week = chipWeek(menu.weeks, pageHref);
  return (
    <>
      {/* Sticky, so the band stays at the top at every scroll and takes its space in the flow, and the page never jumps.
          The band paints the page color in both themes. The hero is the one loud surface of a page. */}
      <header className="sticky top-0 z-40 border-b border-rule bg-page text-ink">
        {/* One row at every tier, so the band keeps one height at every width. On a phone and a tablet it holds the brand
            mark, the week chip, and the theme button. From the desktop tier the pill bar sits between them, with full labels. */}
        <div className="mx-auto flex max-w-band items-center gap-x-sp-3 px-gutter py-sp-2">
          {/* A plain anchor, so the home link works with scripts off. The title names the link, so the logo is decorative.
              Under the rail tier the logo shows alone, so the pill bar has room for its full labels on one row. The title
              stays for a screen reader. A long title cuts at the end.
              The link is 44px or more on each side, so the logo alone is still a full tap target. */}
          <a href={brand.home} className="flex min-h-touch min-w-touch items-center gap-sp-3 text-inherit no-underline">
            {brand.logo !== null && (
              <img src={brand.logo} alt="" width={30} height={30} className="size-logo flex-none rounded-full" />
            )}
            <span
              translate="no"
              className={`truncate text-meta leading-tight font-bold tracking-wide uppercase ${brand.logo !== null ? "max-rail:sr-only" : ""}`}
            >
              {title}
            </span>
          </a>
          <PillBar
            items={menu.items}
            current={current}
            className="min-w-0 flex-1 justify-center"
          />
          <div className="ml-auto flex flex-none items-center gap-sp-2">
            {week !== undefined && <WeekChip weeks={menu.weeks} week={week} pageHref={pageHref} />}
            {/* The theme button needs the script, so it hides with scripts off. The negative margin lines the icon up with the edge. */}
            <ThemeButton className="-mr-sp-3 [@media(scripting:none)]:hidden" />
          </div>
        </div>
      </header>
      {children && <div className="mx-auto max-w-page px-gutter pt-sp-5">{children}</div>}
      <Dock items={menu.items} current={current} />
    </>
  );
}
