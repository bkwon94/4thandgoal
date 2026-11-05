/**
 * The trade analyzer route at /analyze/.
 * It renders the masthead above the client analyzer, which sits in the centered page column on the white page background.
 * From the tablet tier that white is the form's chapter, a card on the grey body.
 */
import type { Metadata } from "next";
import { Analyzer } from "@cpc/analyzer/form/analyzer";
import { Masthead } from "@cpc/design/shell/masthead";
import { PageColumn } from "@cpc/design/parts/page-column";
import { apiTarget, finderOn } from "@/lib/config";
import { analyzeHref } from "@/lib/routes";
import { mastheadProps, pageTitle } from "@/app/masthead-props";

export const metadata: Metadata = {
  title: pageTitle(undefined, "Trade Analyzer"),
};

export default function AnalyzePage() {
  return (
    <>
      <Masthead {...mastheadProps()} subtitle="Trade Analyzer" pageHref={analyzeHref()} />
      <PageColumn>
        <Analyzer target={apiTarget} finderOn={finderOn} />
      </PageColumn>
    </>
  );
}
