/**
 * The 404 page: the shell, and the hero with "404", a plain line about why, and the buttons to the latest week and home.
 * Next exports it as 404.html, which the Worker of each client serves for a path that no page has. The egg board reuses the hero.
 */
import type { Metadata } from "next";
import { driftScene } from "@cpc/design/parts/drift-scene";
import { Hero } from "@cpc/design/parts/hero";
import type { HeroScene } from "@cpc/design/parts/scene-math";
import { Rise } from "@cpc/design/parts/rise";
import { NOT_FOUND, stableId } from "@cpc/design/lib/stable-id";
import { TopBand } from "@cpc/design/shell/top-band";
import { pageTitle, shellProps } from "@/app/shell-props";

export const metadata: Metadata = {
  title: pageTitle(undefined, "Page Not Found"),
};

/* The two buttons of the page. Each is a full pill and a 44px tap target. Each color pair holds 4.5 to 1 in the brand tests. */
const BUTTON =
  "press inline-flex min-h-touch items-center justify-center rounded-pill px-sp-6 text-body font-bold no-underline";

/* The hero of the 404 page. The egg board shows it before the first egg drop, so the board looks like no page.
   The 404 page passes the drift scene. The egg board passes none, because only the first hero of a page draws a scene (ADR 0027). */
export function NotFoundHero({ scene }: { scene?: HeroScene }) {
  const shell = shellProps();
  const latest = shell.menu.weeks[0];
  return (
    <Hero
      label="Page not found"
      title="Page not found"
      scene={scene}
      meta="This page does not exist. The link may be old, or the week is not out yet."
      feature={
        /* The big "404" is art, so the title keeps the one title style of every hero. The plate keeps the grid
           and the glow from under each digit. The title names the page, so a screen reader skips the art.
           The art keeps the stable id of the egg hunt. */
        <Rise step={1}>
          <div
            aria-hidden="true"
            className="plate w-fit font-mono text-hero leading-none font-bold tracking-grade"
            {...stableId("not-found-hero")}
          >
            404
          </div>
        </Rise>
      }
      action={
        <Rise step={2} className="flex flex-wrap gap-sp-3">
          {/* A client with no published week has no week to go to, so it shows only the home button. */}
          {latest !== undefined && (
            <a href={latest.href} className={`${BUTTON} bg-accent text-on-dark`}>
              Go to Week {latest.number}
            </a>
          )}
          <a href={shell.brand.home} className={`${BUTTON} border border-rule-dark bg-chip-dark text-on-dark`}>
            Go Home
          </a>
        </Rise>
      }
    />
  );
}

export default function NotFound() {
  return (
    <>
      {/* The page is no destination, so it passes no page href, and no item of the shell is marked. */}
      <TopBand {...shellProps()} />
      {/* The mark tells the egg hunt that the page is the 404 page, whatever path the reader typed. */}
      <main className="mx-auto w-full max-w-page px-gutter py-sp-6" {...{ [NOT_FOUND]: true }}>
        {/* A lost page has no data to chart, so its lights drift and never settle (story 28). */}
        <NotFoundHero scene={driftScene} />
      </main>
    </>
  );
}
