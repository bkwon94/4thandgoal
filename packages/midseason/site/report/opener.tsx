/**
 * The opener of the midseason report, the title race: the title odds of the leaders, then the record leader and its odds.
 * It is the hero of the report page, with the 8px corners of the report, so it holds the level 1 heading of the page. "See the sim" jumps to the finale.
 */
import { oneDecimal, ordinal } from "@cpc/design/format/format";
import { Hero } from "@cpc/design/parts/hero";
import { Rise } from "@cpc/design/parts/rise";
import { Tile } from "@cpc/design/parts/tile";
import type { Opener as OpenerFacts } from "../schema/midseason-types";
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
  // The first sentence of the blurb is the lead line of the meta, so the meta holds one or two lines. The rest of the
  // blurb sits directly under the hero, outside its frame.
  const [lead, ...rest] = opener.blurb?.sentences ?? [];
  return (
    <>
      <Hero
        label={opener.title}
        className="rounded-report"
        eyebrow={`${season} Midseason Report // Week ${week}`}
        title={opener.title}
        meta={lead?.text}
        stats={
          <Rise step={1} className="w-full">
            {/* The leaders by title odds, best first. Each tile names the team under its odds. */}
            <ol
              aria-label="Title odds"
              className="gap-sp-2 tablet:grid-cols-3 m-0 grid list-none grid-cols-1 p-0"
            >
              {leaders.map((leader) => (
                <li key={leader.roster_id}>
                  <Tile
                    tone="hero"
                    label="Title odds"
                    value={`${oneDecimal(leader.title_odds)}%`}
                    note={leader.name}
                    className="rounded-report"
                  />
                </li>
              ))}
            </ol>
            {/* The record leader, first in the standings, with its own title odds and their place in the league. */}
            <Tile
              tone="hero"
              label="Record leader"
              value={top.title_odds === null ? "No odds" : `${oneDecimal(top.title_odds)}%`}
              note={`${top.name}, ${fullRecord(top.wins, top.losses, top.ties)}${top.title_rank === null ? "" : `, ${placeText(top.title_rank)}`}`}
              className="mt-sp-2 rounded-report"
            />
          </Rise>
        }
        action={
          finaleHref === undefined ? undefined : (
            <Rise step={2}>
              {/* A plain fragment link, so a tap jumps to the sim with scripts off too. */}
              <a
                href={finaleHref}
                className="min-h-touch gap-sp-1 text-meta tracking-caps text-accent-text hover-fine:underline inline-flex w-fit items-center font-mono leading-tight font-bold uppercase no-underline"
              >
                See the sim
                {/* An svg, not a glyph: axe gives no contrast verdict on a lone arrow character, and the floor fails that. */}
                <svg
                  aria-hidden="true"
                  viewBox="0 0 16 16"
                  className="size-[1em]"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M8 2v11M3 8l5 5 5-5" />
                </svg>
              </a>
            </Rise>
          )
        }
      />
      {rest.length > 0 && (
        <p className="max-w-measure text-lead leading-body text-ink-2 m-0">
          {rest.map((sentence) => sentence.text).join(" ")}
        </p>
      )}
    </>
  );
}
