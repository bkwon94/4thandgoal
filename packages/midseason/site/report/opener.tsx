/**
 * The opener of the midseason report, the title race: the title odds of the leaders, then the record leader and its odds.
 * It is the hero of the report page, so it holds the level 1 heading of the page. "See the sim" jumps to the finale.
 */
import { oneDecimal, ordinal } from "@cpc/design/format/format";
import { Hero } from "@cpc/design/parts/hero";
import { Rise } from "@cpc/design/parts/rise";
import { Tile } from "@cpc/design/parts/tile";
import type { Opener as OpenerFacts } from "../schema/midseason-types";
import { blurbText } from "./chapter-prose";
import { fullRecord } from "./numbers";

/* The place of the record leader's title odds in the league, such as "6th in title odds". */
const placeText = (rank: number) => `${ordinal(rank)} in title odds`;

export function Opener({
  opener,
  season,
  week,
  finaleHref,
}: {
  opener: OpenerFacts;
  season: number;
  week: number;
  // The fragment link of the sim at the end of the report. Undefined when the page has no sim, so the link hides.
  finaleHref?: string;
}) {
  const { leaders, record_leader: top } = opener.facts;
  return (
    <Hero label={opener.title}>
      <Rise step={0}>
        <div className="plate w-fit font-mono text-meta leading-tight font-bold tracking-wide text-accent-text uppercase">
          {season} Midseason Report // Week {week}
        </div>
      </Rise>
      <Rise step={1}>
        <h1 className="plate mt-sp-3 mb-0 w-fit text-headline leading-tight font-bold">{opener.title}</h1>
      </Rise>
      <Rise step={2}>
        {/* The leaders by title odds, best first. Each tile names the team under its odds. */}
        <ol aria-label="Title odds" className="m-0 mt-sp-5 grid list-none grid-cols-1 gap-sp-2 p-0 tablet:grid-cols-3">
          {leaders.map((leader) => (
            <li key={leader.roster_id}>
              <Tile tone="hero" label="Title odds" value={`${oneDecimal(leader.title_odds)}%`} note={leader.name} />
            </li>
          ))}
        </ol>
      </Rise>
      <Rise step={3}>
        {/* The record leader, first in the standings, with its own title odds and their place in the league. */}
        <Tile
          tone="hero"
          label="Record leader"
          value={top.title_odds === null ? "No odds" : `${oneDecimal(top.title_odds)}%`}
          note={`${top.name}, ${fullRecord(top.wins, top.losses, top.ties)}${top.title_rank === null ? "" : `, ${placeText(top.title_rank)}`}`}
          className="mt-sp-2"
        />
      </Rise>
      {finaleHref !== undefined && (
        <Rise step={3}>
          {/* A plain fragment link, so a tap jumps to the sim with scripts off too. */}
          <a
            href={finaleHref}
            className="plate mt-sp-3 inline-flex min-h-touch w-fit items-center gap-sp-1 font-mono text-meta leading-tight font-bold tracking-caps text-accent-text uppercase no-underline hover-fine:underline"
          >
            See the sim
            <span aria-hidden="true">↓</span>
          </a>
        </Rise>
      )}
      {opener.blurb !== null && (
        <Rise step={4}>
          <p className="plate mt-sp-4 mb-0 w-fit max-w-measure text-lead leading-body text-on-dark-2">
            {blurbText(opener.blurb)}
          </p>
        </Rise>
      )}
    </Hero>
  );
}
