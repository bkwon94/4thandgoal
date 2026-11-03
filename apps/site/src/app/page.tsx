/**
 * The home page at /: the tools, the top of the power rankings, and every published week, newest first, read from each week's page.json.
 * It is a server component, so the list is part of the static export.
 */
import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Masthead, WeekLine } from "@/components/shell/masthead";
import { PageColumn } from "@/components/parts/page-column";
import { Movement } from "@/components/rankings/power-rankings";
import { Reveal } from "@/components/parts/reveal";
import { TeamsPrefetch } from "@/components/analyzer/teams-prefetch";
import { Blurb } from "@/components/parts/blurb";
import { Chapter } from "@/components/parts/chapter";
import { Label } from "@/components/parts/label";
import { season } from "@/lib/config";
import { currentManagersHref } from "@/lib/data/manager-data";
import { stagger } from "@/lib/motion";
import { biggestMover } from "@/lib/format/rankings";
import { loadRankings } from "@/lib/data/rankings-data";
import { analyzeHref, homeHref, rankingsHref } from "@/lib/routes";
import { cn } from "@/lib/utils";
import { listWeekSummaries } from "@/lib/data/week-data";
import { mastheadProps } from "@/app/masthead-props";

export const metadata: Metadata = {
  title: "Cornerstone Fantasy Football League",
};

/* A plain anchor, like the masthead link. An anchor skips the router, so the caller passes an href with the base path. */
function HomeRow({ href, first, children }: { href: string; first?: boolean; children: ReactNode }) {
  return (
    <a
      href={href}
      className={cn(
        "press group block border-b border-rule py-sp-3 text-inherit no-underline",
        // The label already gives the first row its top space.
        first && "pt-0",
      )}
    >
      {children}
    </a>
  );
}

export default function HomePage() {
  const weeks = listWeekSummaries();
  const rankings = loadRankings()?.weeks.at(-1);
  const mover = rankings ? biggestMover(rankings) : null;
  // A missing managers file hides the card, as the menu hides its entry, so the page ships before the pipeline writes the file.
  const managersHref = currentManagersHref();
  // The week rows start the stagger one step after the rankings chapter, or after the tools row when the chapter is hidden.
  const firstWeekStep = rankings ? 2 : 1;
  return (
    <>
      {/* A reader who opens the analyzer next sees the pickers at once, because the teams are already in session storage. */}
      <TeamsPrefetch />
      <Masthead {...mastheadProps()} pageHref={homeHref()}>
        <WeekLine label="SEASON" number={season} />
      </Masthead>
      <PageColumn>
        {/* The Tools chapter holds the analyzer row and the managers row, and the Power Rankings chapter holds one tall row,
            so side by side they fill the column.
            The row is one child of the main, so the main's card gap sits above and below it. On a phone the row is a plain
            block, so the chapters stack with the chapter rule. With no rankings file the grid has one column, so the Tools
            chapter takes the full width and the row has no empty half. */}
        <div className={cn("tablet:grid tablet:gap-card-gap", rankings ? "tablet:grid-cols-2" : "tablet:grid-cols-1")}>
          {/* The masthead and the label show at once. Each row reveals as it enters the view. */}
          <Chapter>
            <Label heading>Tools</Label>
            {/* The row reveals first, so a new week never pushes it down or delays it. */}
            <Reveal delay={stagger(0)}>
              <HomeRow href={analyzeHref()} first>
                <b className="mb-sp-1 block text-lead leading-tight group-hover:text-red-ink">Trade Analyzer</b>
                <span className="block text-meta text-mute">Grade a trade offer before you send it.</span>
                <span className="block text-meta text-mute">League passphrase needed.</span>
              </HomeRow>
            </Reveal>
            {managersHref && (
              <Reveal delay={stagger(0)}>
                <HomeRow href={managersHref}>
                  <b className="mb-sp-1 block text-lead leading-tight group-hover:text-red-ink">Managers</b>
                  <span className="block text-meta text-mute">One page per team: grade, odds, moves, and performers.</span>
                </HomeRow>
              </Reveal>
            )}
          </Chapter>
          {/* A missing season file hides the chapter, so the page ships before the pipeline writes the file. */}
          {rankings && (
            <Chapter>
              <Label heading>Power Rankings</Label>
              <Reveal delay={stagger(1)}>
                <HomeRow href={rankingsHref()} first>
                  <b className="mb-sp-1 block text-lead leading-tight group-hover:text-red-ink">Top Three</b>
                  <ol className="m-0 mb-sp-1 list-none p-0">
                    {rankings.rows.slice(0, 3).map((row) => (
                      <li key={row.roster_id} className="text-meta text-ink-2 tabular-nums">
                        <span className="mr-sp-1 text-mute">{row.rank}</span>
                        {row.name}
                      </li>
                    ))}
                  </ol>
                  {mover && (
                    <span className="block text-meta text-mute tabular-nums">
                      Biggest mover: <Movement movement={mover.movement} /> {mover.name}
                    </span>
                  )}
                  <span className="block text-meta text-mute">See all twelve teams.</span>
                </HomeRow>
              </Reveal>
            </Chapter>
          )}
        </div>
        <Chapter>
          <Label heading>Weekly Reports</Label>
          {weeks.length === 0 && <Blurb>No weeks are published yet.</Blurb>}
          {weeks.map((week, index) => (
            // Each row reveals once after the rows above it, with a short, capped stagger, so a row in a long season list never shows late.
            <Reveal key={week.href} delay={stagger(index + firstWeekStep)}>
              <HomeRow href={week.href} first={index === 0}>
                <b className="mb-sp-1 block text-lead leading-tight group-hover:text-red-ink">Week {week.number}</b>
                <span className="block text-meta text-mute tabular-nums">{week.dates}</span>
              </HomeRow>
            </Reveal>
          ))}
        </Chapter>
      </PageColumn>
    </>
  );
}
