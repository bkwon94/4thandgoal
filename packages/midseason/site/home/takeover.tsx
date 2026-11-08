/**
 * The takeover of the home page: the opener of the midseason report, the title race, with a link to the report.
 * The home page shows it in place of its usual top through the takeover end week of the midseason file.
 */
import { oneDecimal, ordinal } from "@cpc/design/format/format";
import { Hero } from "@cpc/design/parts/hero";
import { Rise } from "@cpc/design/parts/rise";
import { Tile } from "@cpc/design/parts/tile";
import type { Midseason } from "../schema/midseason-types";
import { midseasonScene } from "../report/midseason-scene";
import { fullRecord } from "../report/numbers";

/* True while the latest published week is at or before the takeover end week, the week of the report plus 1 (PRD). */
export const takeoverOn = (report: Midseason, latestWeek: number) => latestWeek <= report.takeover_end_week;

export function Takeover({ report, href }: { report: Midseason; href: string }) {
  const { leaders, record_leader: top } = report.opener.facts;
  return (
    // The intro of the home page holds the h1, so the title of the opener is a level 2 heading here.
    <Hero
      label={`${report.season} Midseason Report`}
      eyebrow={`${report.season} Midseason Report // Week ${report.week}`}
      title={report.opener.title}
      level={2}
      // The takeover replaces the top of the home page, so it is the first hero there and draws the midseason scene.
      scene={midseasonScene(report)}
      stats={
        // From the tablet tier up the stats share the bottom row with the wide pill of the action. The row of tiles
        // keeps its max-content width there, so a long team name such as "Mitseeker5000" never breaks over 2 lines,
        // and the pill wraps between its words instead.
        <Rise step={1} className="w-full tablet:min-w-max">
          {/* The leaders by title odds, best first, as the opener of the report shows them. */}
          <ol aria-label="Title odds" className="m-0 grid list-none grid-cols-1 gap-sp-2 p-0 tablet:grid-cols-3">
            {leaders.map((leader) => (
              <li key={leader.roster_id}>
                <Tile tone="hero" label="Title odds" value={`${oneDecimal(leader.title_odds)}%`} note={leader.name} />
              </li>
            ))}
          </ol>
          <Tile
            tone="hero"
            label="Record leader"
            value={top.title_odds === null ? "No odds" : `${oneDecimal(top.title_odds)}%`}
            note={`${top.name}, ${fullRecord(top.wins, top.losses, top.ties)}${top.title_rank === null ? "" : `, ${ordinal(top.title_rank)} in title odds`}`}
            className="mt-sp-2"
          />
        </Rise>
      }
      action={
        <Rise step={2} className="w-full tablet:w-auto">
          {/* A full pill and a 44px tap target in the brand color, as the button of the home hero. */}
          <a
            href={href}
            className="press flex min-h-touch items-center justify-center rounded-pill bg-accent px-sp-6 text-center text-body font-bold text-on-dark no-underline"
          >
            Read the Midseason Report
          </a>
        </Rise>
      }
    />
  );
}
