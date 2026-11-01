/**
 * The trade analyzer route at /analyze/.
 * It renders the masthead above the client analyzer, which sits in the centered page column on the white page background.
 * From the tablet tier that white is the form's chapter, a card on the grey body.
 */
import type { Metadata } from "next";
import { Analyzer } from "@/components/analyzer";
import { Masthead } from "@/components/masthead";
import { PageColumn } from "@/components/page-column";
import { analyzeHref } from "@/lib/routes";
import { mastheadProps } from "../masthead-props";

export const metadata: Metadata = {
  title: "Trade Analyzer · Cornerstone Fantasy Football League",
};

export default function AnalyzePage() {
  return (
    <>
      <Masthead {...mastheadProps()} subtitle="Trade Analyzer" pageHref={analyzeHref()} />
      <PageColumn>
        <Analyzer />
      </PageColumn>
    </>
  );
}
