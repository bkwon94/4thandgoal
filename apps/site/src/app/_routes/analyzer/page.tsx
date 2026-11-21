/**
 * The trade analyzer route at /analyze/.
 * It renders the shell above the Stack of the analyzer, in the column of the page.
 * The grade bar rests inside the Stack, so the column needs no space for it at its end.
 */
import type { Metadata } from "next";
import { Analyzer } from "@cpc/analyzer/form/analyzer";
import { TopBand } from "@cpc/design/shell/top-band";
import { apiTarget, finderOn } from "@/lib/config";
import { analyzeHref } from "@/lib/routes";
import { shellProps, pageTitle } from "@/app/shell-props";
import { clientValues } from "@/generated/client-values";

export const metadata: Metadata = {
  title: pageTitle(undefined, "Trade Analyzer"),
};

export default function AnalyzePage() {
  return (
    <>
      <TopBand {...shellProps()} pageHref={analyzeHref()} />
      <main className="max-w-page px-gutter pt-sp-6 pb-sp-6 mx-auto w-full">
        <Analyzer target={apiTarget} finderOn={finderOn} lock={clientValues.lock} />
      </main>
    </>
  );
}
