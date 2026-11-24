/**
 * The closed analyzer page at /analyze/: the top band, the closed line, and one link to Home.
 * The client build writes it in place of the analyzer page after the Lock, and it reads no query.
 */
import type { Metadata } from "next";
import { Hero } from "@cpc/design/parts/hero";
import { Rise } from "@cpc/design/parts/rise";
import { TopBand } from "@cpc/design/shell/top-band";
import { CLOSED_LINE } from "@/lib/trades-closed";
import { homeHref } from "@/lib/routes";
import { pageTitle, shellProps } from "@/app/shell-props";

export const metadata: Metadata = {
  title: pageTitle(undefined, "Trade Analyzer"),
};

/* The Home button is a full pill and a 44px tap target, as the buttons of the 404 page are. */
const BUTTON =
  "press inline-flex min-h-touch items-center justify-center rounded-pill px-sp-6 text-body font-bold no-underline";

export default function ClosedPage() {
  return (
    <>
      {/* The page is no destination of the menu after the close, so it passes no page href. */}
      <TopBand {...shellProps()} />
      <main className="max-w-page px-gutter py-sp-6 mx-auto w-full">
        <Hero
          label="Trades closed"
          title={CLOSED_LINE}
          action={
            <Rise step={1} className="gap-sp-3 flex flex-wrap">
              <a href={homeHref()} className={`${BUTTON} bg-accent text-on-dark`}>
                Home
              </a>
            </Rise>
          }
        />
      </main>
    </>
  );
}
