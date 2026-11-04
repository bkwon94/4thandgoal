/**
 * The home section of the week package: the Weekly Reports chapter, with every published week, newest first.
 * The registry of the client build imports it only when the client takes week.
 */
import { Blurb } from "@cpc/design/parts/blurb";
import { Chapter } from "@cpc/design/parts/chapter";
import { Label } from "@cpc/design/parts/label";
import { Reveal } from "@cpc/design/parts/reveal";
import { stagger } from "@cpc/design/lib/motion";
import { listWeekSummaries } from "@/lib/data/week-data";
import type { HomeSection } from "@/lib/client-values";
import { HomeRow } from "@/app/home-row";

export const homeSection = (): HomeSection => {
  const weeks = listWeekSummaries();
  return {
    place: "below",
    chapter: (step) => (
      <Chapter>
        <Label heading>Weekly Reports</Label>
        {weeks.length === 0 && <Blurb>No weeks are published yet.</Blurb>}
        {weeks.map((week, index) => (
          // Each row reveals once after the rows above it, with a short, capped stagger, so a row in a long season list never shows late.
          <Reveal key={week.href} delay={stagger(index + step)}>
            <HomeRow href={week.href} first={index === 0}>
              <b className="mb-sp-1 block text-lead leading-tight group-hover:text-accent-ink">Week {week.number}</b>
              <span className="block text-meta text-mute tabular-nums">{week.dates}</span>
            </HomeRow>
          </Reveal>
        ))}
      </Chapter>
    ),
  };
};
