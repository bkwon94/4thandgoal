/**
 * The egg board route at /eggs/. It renders the shell above the egg board, which reads the API at each visit.
 * The client build writes the route only for a client of the eggs package.
 */
import type { Metadata } from "next";
import { TopBand } from "@cpc/design/shell/top-band";
import { pageTitle, shellProps } from "@/app/shell-props";
import { eggsHref } from "@/lib/routes";
import { EggBoardPart } from "./board";

export const metadata: Metadata = {
  title: pageTitle(undefined, "Egg Board"),
};

export default function EggsPage() {
  return (
    <>
      <TopBand {...shellProps()} pageHref={eggsHref()} />
      <main className="mx-auto w-full max-w-page px-gutter pt-sp-6 pb-sp-6">
        <h1 className="mb-sp-4 text-headline font-black uppercase">Egg Board</h1>
        <EggBoardPart />
      </main>
    </>
  );
}
