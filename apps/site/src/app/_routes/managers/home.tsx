/**
 * The home section of the managers package: the Managers row of the Tools chapter.
 * The registry of the client build imports it only when the client takes managers.
 */
import { Reveal } from "@cpc/design/parts/reveal";
import { stagger } from "@cpc/design/lib/motion";
import { currentManagersHref } from "@/lib/data/manager-data";
import type { HomeSection } from "@/lib/client-values";
import { HomeRow } from "@/app/home-row";

/* A missing managers file hides the row, as the menu hides its entry, so the page ships before the pipeline writes the file. */
export const homeSection = (): HomeSection | null => {
  const managersHref = currentManagersHref();
  if (!managersHref) return null;
  return {
    place: "tools",
    row: (first) => (
      <Reveal delay={stagger(0)}>
        <HomeRow href={managersHref} first={first}>
          <b className="mb-sp-1 block text-lead leading-tight group-hover:text-accent-ink">Managers</b>
          <span className="block text-meta text-mute">One page per team: grade, odds, moves, and performers.</span>
        </HomeRow>
      </Reveal>
    ),
  };
};
