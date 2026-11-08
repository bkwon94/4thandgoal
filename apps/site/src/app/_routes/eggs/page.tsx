/**
 * The egg board route at /eggs/. It renders the shell above the egg board, which reads the API at each visit.
 * The client build writes the route only for a client of the eggs package. Before the first egg drop it shows the 404 hero.
 */
import type { Metadata } from "next";
import { TopBand } from "@cpc/design/shell/top-band";
import { metadata as notFoundMetadata, NotFoundHero } from "@/app/not-found";
import { pageTitle, shellProps } from "@/app/shell-props";
import { eggsHref } from "@/lib/routes";
import { EggBoardPart } from "./board";

// The page loads with the title of the 404 page, so the tab names no egg before the first drop. The board sets its own
// title once the hunt is on.
export const metadata: Metadata = notFoundMetadata;

export default function EggsPage() {
  return (
    <>
      <TopBand {...shellProps()} pageHref={eggsHref()} />
      {/* The hero of the egg board, or of the 404 page, holds the h1 of the page. */}
      <main className="mx-auto w-full max-w-page px-gutter pt-sp-5 pb-sp-6">
        <EggBoardPart closed={<NotFoundHero />} title={pageTitle(undefined, "Egg Board")} />
      </main>
    </>
  );
}
