/**
 * The standings ladder of Playoff race, in the Ledger look: one row per team with its rank, its name, a bar of its
 * playoff odds, and its record, with a rule at the playoff line, then a link to the sim page. Its schema is in lib/data/blocks/.
 */
"use client";

import { motion } from "framer-motion";
import { ArrowRightIcon } from "lucide-react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { type LadderBlock, oddsWords } from "@/lib/data/blocks/ladder-schema";
import { SLOW, VERY_SLOW, fadeIn, riseIn, staggerOf } from "./motion";
import { useSimLink } from "./sim-link";

/* The bar of the playoff odds of one team, from the left edge of its track. Red for Your team, gray for the rest. A
   team with no odds shows the empty track. */
function OddsBar({ odds, you, index, live }: { odds: number | null; you: boolean; index: number; live: boolean }) {
  const off = useMotionOff();
  // A bar grows out from the left edge after its row settles, so the eye reads the race top to bottom.
  const grow = live ? { initial: off ? { opacity: 0 } : { opacity: 0, scaleX: 0 }, animate: off ? { opacity: 1 } : { opacity: 1, scaleX: 1 }, transition: fadeIn(SLOW, 0.2 + staggerOf(index)) } : {};
  return (
    <span aria-hidden data-odds={you ? "you" : "team"} className="relative block h-1.5 overflow-hidden rounded-pill bg-rule">
      {odds !== null && odds > 0 && (
        <motion.span className={`absolute inset-y-0 left-0 origin-left rounded-pill ${you ? "bg-accent" : "bg-mute"}`} style={{ width: `${odds}%` }} {...grow} />
      )}
    </span>
  );
}

export function StandingsLadder({ block, live }: { block: LadderBlock; live: boolean }) {
  const off = useMotionOff();
  const simHref = useSimLink();
  return (
    <div className="flex min-w-0 flex-col gap-sp-2" data-block="ladder">
      {/* The heads of the two number columns, so "62%" and "11-7" read without a guess. On a phone the odds bar is
          narrower, so a team name such as "The Blue Tent" keeps more of its letters. */}
      <p aria-hidden className="m-0 grid grid-cols-[1.5rem_minmax(0,1fr)_minmax(2.5rem,16%)_2.5rem_2.75rem] desktop:grid-cols-[1.5rem_minmax(0,1fr)_minmax(3rem,26%)_2.5rem_2.75rem] gap-x-sp-3 font-mono text-meta leading-tight tracking-caps text-mute uppercase">
        <span className="col-start-3">Odds</span>
        <span className="col-start-5 text-right">W-L</span>
      </p>
      <ul aria-label="Standings" className="m-0 flex list-none flex-col border-t border-rule p-0">
        {block.rows.map((row, index) => {
          const cut = index === block.playoff_teams - 1 && index < block.rows.length - 1;
          return (
            <motion.li
              key={row.roster_id}
              aria-label={`${row.rank}. ${row.name}${row.you ? ", your team" : ""}, ${row.record}, ${oddsWords(row.odds)}${cut ? ", the last playoff spot" : ""}`}
              {...(row.you ? { "data-you": "" } : {})}
              {...(cut ? { "data-cut": "" } : {})}
              // The row on the playoff line trades its hairline for a rule in the ink, so the cut reads at a glance.
              className={`relative grid grid-cols-[1.5rem_minmax(0,1fr)_minmax(2.5rem,16%)_2.5rem_2.75rem] desktop:grid-cols-[1.5rem_minmax(0,1fr)_minmax(3rem,26%)_2.5rem_2.75rem] items-center gap-x-sp-3 py-sp-2 ${cut ? "border-b-2 border-ink-2" : "border-b border-rule last:border-b-0"}`}
              {...(live ? riseIn(off, { delay: staggerOf(index) }) : {})}
            >
              <span aria-hidden className="font-mono text-meta leading-tight text-mute tabular-nums">{row.rank}</span>
              <span aria-hidden className="flex min-w-0 items-baseline gap-sp-2">
                <span className={`truncate text-row leading-tight font-semibold ${row.you ? "text-accent-ink" : "text-ink"}`}>{row.name}</span>
                {/* "You" names the row of Your team in words, so it never rests on the red alone. */}
                {row.you && <span className="flex-none font-mono text-meta leading-tight tracking-caps text-accent-ink uppercase">You</span>}
              </span>
              <OddsBar odds={row.odds} you={row.you} index={index} live={live} />
              <span aria-hidden className={`text-right font-mono text-meta leading-tight tabular-nums ${row.you ? "font-semibold text-accent-ink" : "text-ink-2"}`}>
                {row.odds === null ? "–" : `${row.odds}%`}
              </span>
              <span aria-hidden className="text-right font-mono text-meta leading-tight text-ink-2 tabular-nums">{row.record}</span>
              {cut && (
                <span aria-hidden className="absolute right-0 bottom-0 translate-y-1/2 bg-card pl-sp-2 font-mono text-meta leading-none tracking-caps text-ink-2 uppercase">
                  Playoff line
                </span>
              )}
            </motion.li>
          );
        })}
      </ul>
      {/* The race on the ladder plays out on the sim page, so the ladder ends with the way there (decision 06). It fades in
          after the rows, in the look of the link of an Answer. */}
      {simHref !== null && (
        <motion.a
          href={simHref}
          className="press group -mx-sp-2 flex min-h-touch items-center gap-sp-2 self-start rounded-pill px-sp-2 text-body leading-tight font-semibold text-accent-ink no-underline"
          {...(live ? { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: fadeIn(VERY_SLOW, 0.3) } : {})}
        >
          <span>Open the season sim</span>
          <ArrowRightIcon
            aria-hidden
            className="size-sp-4 transition-transform duration-150 ease-out group-hover:translate-x-sp-0 motion-reduce:transition-none"
            strokeWidth={2.25}
          />
        </motion.a>
      )}
    </div>
  );
}
