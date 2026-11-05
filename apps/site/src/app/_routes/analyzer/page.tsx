/**
 * The trade analyzer route at /analyze/.
 * It renders the shell above the Stack of the analyzer, in the column of the page.
 * The column keeps the space of the grade bar free at its end, so the bar on the dock covers no content.
 */
import type { Metadata } from "next";
import { Analyzer } from "@cpc/analyzer/form/analyzer";
import { TopBand } from "@cpc/design/shell/top-band";
import { apiTarget, finderOn } from "@/lib/config";
import { analyzeHref } from "@/lib/routes";
import { shellProps, pageTitle } from "@/app/shell-props";

export const metadata: Metadata = {
  title: pageTitle(undefined, "Trade Analyzer"),
};

export default function AnalyzePage() {
  return (
    <>
      <TopBand {...shellProps()} pageHref={analyzeHref()} />
      {/* The bottom space is the 44px bar and the step above it, so the end of the page scrolls clear of the bar. */}
      <main className="mx-auto w-full max-w-page px-gutter pt-sp-6 pb-[calc(var(--spacing-touch)+var(--spacing-sp-6))] tablet:pb-[calc(var(--spacing-touch)+var(--spacing-sp-6)+var(--spacing-sp-4))]">
        <Analyzer target={apiTarget} finderOn={finderOn} />
      </main>
    </>
  );
}
