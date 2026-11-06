/**
 * The takeover of the home page: the opener of the midseason report, the title race, with a link to the report.
 * The home page shows it in place of its usual top through the takeover end week of the midseason file.
 */
import { oneDecimal, ordinal } from "@cpc/design/format/format";
import { Hero } from "@cpc/design/parts/hero";
import { Rise } from "@cpc/design/parts/rise";
import { Tile } from "@cpc/design/parts/tile";
import type { Midseason } from "../schema/midseason-types";
import { fullRecord } from "../report/numbers";

/* True while the latest published week is at or before the takeover end week, the week of the report plus 1 (PRD). */
export const takeoverOn = (report: Midseason, latestWeek: number) => latestWeek <= report.takeover_end_week;

export function Takeover({ report, href }: { report: Midseason; href: string }) {
  const { leaders, record_leader: top } = report.opener.facts;
  return (
    <Hero label={`${report.season} Midseason Report`}>
      <Rise step={0}>
        <div className="plate w-fit font-mono text-meta leading-tight font-bold tracking-wide text-accent-text uppercase">
          {report.season} midseason report // Week {report.week}
        </div>
      </Rise>
      <Rise step={1}>
        {/* The intro of the home page holds the h1, so the title of the opener is a level 2 heading here. */}
        <h2 className="plate mt-sp-3 mb-0 w-fit text-headline leading-tight font-bold">{report.opener.title}</h2>
      </Rise>
      <Rise step={2}>
        {/* The leaders by title odds, best first, as the opener of the report shows them. */}
        <ol aria-label="Title odds" className="m-0 mt-sp-5 grid list-none grid-cols-1 gap-sp-2 p-0 tablet:grid-cols-3">
          {leaders.map((leader) => (
            <li key={leader.roster_id}>
              <Tile tone="hero" label="Title odds" value={`${oneDecimal(leader.title_odds)}%`} note={leader.name} />
            </li>
          ))}
        </ol>
      </Rise>
      <Rise step={3}>
        <Tile
          tone="hero"
          label="Record leader"
          value={top.title_odds === null ? "No odds" : `${oneDecimal(top.title_odds)}%`}
          note={`${top.name}, ${fullRecord(top.wins, top.losses, top.ties)}${top.title_rank === null ? "" : `, ${ordinal(top.title_rank)} in title odds`}`}
          className="mt-sp-2"
        />
        {/* A full pill and a 44px tap target in the brand color, as the button of the home hero. */}
        <a
          href={href}
          className="press mt-sp-5 flex min-h-touch items-center justify-center rounded-pill bg-accent px-sp-6 text-body font-bold text-on-dark no-underline"
        >
          Read the Midseason Report
        </a>
      </Rise>
    </Hero>
  );
}
