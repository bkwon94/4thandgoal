/**
 * The shell of every page: the top band with the brand mark, the pill bar, the actions, the theme button,
 * and the menu button with its sheet of pages below the desktop tier.
 * The top band stays on screen at every scroll.
 */
import type { ReactNode } from "react";
import { MenuSheet } from "./menu-sheet";
import { currentHref, type Brand, type SiteMenu } from "./nav";
import { PillBar } from "./pill-bar";
import { ThemeButton } from "./theme-button";

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
  // The buttons of the packages of the client, such as the egg button, just before the theme button. The app layer
  // passes them, so the shell names no package. A client with none passes none.
  actions?: ReactNode;
  // The rows of the open page at the foot of the menu sheet, such as the replay of the Tour on the front door. The app
  // layer passes them, so the shell names no part of a page. A page with none passes none.
  menuFoot?: ReactNode;
};

export function TopBand({
  title,
  brand,
  menu,
  pageHref,
  children,
  actions,
  menuFoot,
}: TopBandProps) {
  const current = currentHref(menu.items, menu.weeks, pageHref);
  return (
    <>
      {/* Sticky, so the band stays at the top at every scroll and takes its space in the flow, and the page never jumps.
          The band paints the page color in both themes. The hero is the one loud surface of a page. */}
      <header className="border-rule bg-page text-ink sticky top-0 z-40 border-b">
        {/* One row at every tier, so the band keeps one height at every width. On a phone and a tablet it holds the brand
            mark and the theme button. From the desktop tier the pill bar sits between them, with full labels. */}
        <div className="max-w-band gap-x-sp-3 px-gutter py-sp-2 mx-auto flex items-center">
          {/* A plain anchor, so the home link works with scripts off. The title names the link, so the logo is decorative.
              Under the rail tier the logo shows alone, so the pill bar has room for its full labels on one row. The title
              stays for a screen reader. A long title cuts at the end.
              The link is 44px or more on each side, so the logo alone is still a full tap target.
              Its high shrink lets the title cut before the pill bar loses width, so the bar keeps each full label with no scroll. */}
          <a
            href={brand.home}
            className="min-h-touch min-w-touch gap-sp-3 flex shrink-999 items-center text-inherit no-underline"
          >
            {brand.logo !== null && (
              <img
                src={brand.logo}
                alt=""
                width={30}
                height={30}
                className="size-logo flex-none rounded-full"
              />
            )}
            <span
              translate="no"
              className={`text-meta truncate leading-tight font-bold tracking-wide uppercase ${brand.logo !== null ? "max-rail:sr-only" : ""}`}
            >
              {title}
            </span>
          </a>
          {/* The bar starts at the width of its labels and grows into the free space. A bar that starts at no width
              leaves the free space to the title, and then a full title makes the bar scroll. */}
          <PillBar
            items={menu.items}
            current={current}
            className="min-w-0 flex-auto justify-center"
          />
          <div className="gap-sp-2 ml-auto flex flex-none items-center">
            {actions}
            {/* The theme button needs the script, so it hides with scripts off. The negative margin lines the icon up with the edge. */}
            <ThemeButton className="[@media(scripting:none)]:hidden" />
            <MenuSheet
              items={menu.items}
              weeks={menu.weeks}
              current={current}
              pageHref={pageHref}
              foot={menuFoot}
            />
          </div>
        </div>
      </header>
      {children && <div className="max-w-page px-gutter pt-sp-5 mx-auto">{children}</div>}
    </>
  );
}
