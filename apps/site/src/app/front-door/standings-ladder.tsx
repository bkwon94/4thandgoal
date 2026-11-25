/**
 * The standings ladder of Playoff race, in the Ledger look: the top Finishes of Your team with its status pill, then one
 * row per team with its rank, its name, a bar of its playoff odds, and its record, with a rule at the playoff line, then
 * a link to The Race. Its schema is in lib/data/blocks/.
 */
"use client";

import { motion } from "framer-motion";
import { ArrowRightIcon } from "lucide-react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import {
  type LadderBlock,
  type LadderFinish,
  finishOdds,
  finishWords,
  oddsWords,
} from "@/lib/data/blocks/ladder-schema";
import { SLOW, VERY_SLOW, fadeIn, riseIn, staggerOf } from "./motion";
import { useSimLink } from "./sim-link";

/* The bar of the playoff odds of one team, from the left edge of its track. Red for Your team, gray for the rest. A
   team with no odds shows the empty track. */
function OddsBar({
  odds,
  you,
  index,
  live,
}: {
  odds: number | null;
  you: boolean;
  index: number;
  live: boolean;
}) {
  const off = useMotionOff();
  // A bar grows out from the left edge after its row settles, so the eye reads the race top to bottom.
  const grow = live
    ? {
        initial: off ? { opacity: 0 } : { opacity: 0, scaleX: 0 },
        animate: off ? { opacity: 1 } : { opacity: 1, scaleX: 1 },
        transition: fadeIn(SLOW, 0.2 + staggerOf(index)),
      }
    : {};
  return (
    <span
      aria-hidden
      data-odds={you ? "you" : "team"}
      className="rounded-pill bg-rule relative block h-1.5 overflow-hidden"
    >
      {odds !== null && odds > 0 && (
        <motion.span
          className={`rounded-pill absolute inset-y-0 left-0 origin-left ${you ? "bg-accent" : "bg-mute"}`}
          style={{ width: `${odds}%` }}
          {...grow}
        />
      )}
    </span>
  );
}

/* The quiet tint of the status pill of The Race: green for Clinched, red for Out. A team In the hunt has no pill. */
const PILL_TINT = {
  clinched: "bg-status-in-tint text-status-in-ink",
  out: "bg-status-out-tint text-status-out-ink",
} as const;

function StatusPill({ pill }: { pill: NonNullable<LadderBlock["pill"]> }) {
  return (
    <span
      data-status-pill={pill.kind}
      className={`rounded-pill px-sp-2 text-meta py-sp-0 inline-flex flex-none items-center leading-tight font-bold whitespace-nowrap ${PILL_TINT[pill.kind]}`}
    >
      {pill.label}
    </span>
  );
}

/* The top Finishes of Your team for a playoff spot, in the look of the Finish list of The Race: the Finish and its final
   record, a bar of its odds with its chance, and the odds. The full list and its Paths live on The Race. */
function RaceFinishes({
  finishes,
  pill,
  odds,
  live,
}: {
  finishes: LadderFinish[];
  pill: LadderBlock["pill"];
  odds: number | null;
  live: boolean;
}) {
  const off = useMotionOff();
  const grid = finishes.some((finish) => finish.about)
    ? "grid-cols-[5.5rem_minmax(0,1fr)_5.75rem]"
    : "grid-cols-[5.5rem_minmax(0,1fr)_3.25rem]";
  return (
    <div className="gap-sp-2 flex min-w-0 flex-col" data-race-finishes="">
      <div className="gap-sp-2 flex min-h-6 items-center justify-between">
        {odds !== null && (
          <p className="gap-sp-2 m-0 flex items-baseline">
            <span className="text-meta tracking-caps text-mute font-mono leading-tight uppercase">
              Playoff odds
            </span>
            <span className="text-row text-accent-ink font-mono leading-tight font-bold tabular-nums">
              {`${odds}%`}
            </span>
          </p>
        )}
        {pill !== null && <StatusPill pill={pill} />}
      </div>
      <p
        aria-hidden
        className="text-meta tracking-caps text-mute m-0 font-mono leading-tight uppercase"
      >
        Rest of season
      </p>
      <ul aria-label="Rest of season" className="m-0 flex list-none flex-col p-0">
        {finishes.map((finish, index) => (
          <motion.li
            key={finish.name}
            aria-label={finishWords(finish)}
            className={`gap-x-sp-3 py-sp-2 grid items-center ${grid}`}
            {...(live ? riseIn(off, { delay: staggerOf(index) }) : {})}
          >
            <span aria-hidden className="flex min-w-0 flex-col">
              <span className="text-row text-ink font-mono leading-snug font-bold tabular-nums">
                {finish.name}
              </span>
              <span className="text-meta text-mute leading-tight whitespace-nowrap tabular-nums">
                {`ends ${finish.record}`}
              </span>
            </span>
            <span aria-hidden className="gap-sp-1 flex min-w-0 flex-col">
              <OddsBar odds={finish.odds} you index={index} live={live} />
              <span className="text-meta text-mute leading-tight tabular-nums">
                {`${Math.round(finish.chance)}% likely`}
              </span>
            </span>
            <span
              aria-hidden
              className="text-row text-ink text-right font-mono leading-tight font-bold whitespace-nowrap tabular-nums"
            >
              {finishOdds(finish)}
            </span>
          </motion.li>
        ))}
      </ul>
    </div>
  );
}

export function StandingsLadder({ block, live }: { block: LadderBlock; live: boolean }) {
  const off = useMotionOff();
  const simHref = useSimLink();
  return (
    <div className="gap-sp-2 flex min-w-0 flex-col" data-block="ladder">
      {block.finishes.length > 0 && (
        <RaceFinishes
          finishes={block.finishes}
          pill={block.pill}
          odds={block.rows.find((row) => row.you)?.odds ?? null}
          live={live}
        />
      )}
      {/* The heads of the two number columns, so "62%" and "11-7" read without a guess. On a phone the odds bar is
          narrower, so a team name such as "The Blue Tent" keeps more of its letters. */}
      <p
        aria-hidden
        className="desktop:grid-cols-[1.5rem_minmax(0,1fr)_minmax(3rem,26%)_2.5rem_2.75rem] gap-x-sp-3 text-meta tracking-caps text-mute m-0 grid grid-cols-[1.5rem_minmax(0,1fr)_minmax(2.5rem,16%)_2.5rem_2.75rem] font-mono leading-tight uppercase"
      >
        <span className="col-start-3">Odds</span>
        <span className="col-start-5 text-right">W-L</span>
      </p>
      <ul aria-label="Standings" className="border-rule m-0 flex list-none flex-col border-t p-0">
        {block.rows.map((row, index) => {
          const cut = index === block.playoff_teams - 1 && index < block.rows.length - 1;
          return (
            <motion.li
              key={row.roster_id}
              aria-label={`${row.rank}. ${row.name}${row.you ? ", your team" : ""}, ${row.record}, ${oddsWords(row.odds)}${cut ? ", the last playoff spot" : ""}`}
              {...(row.you ? { "data-you": "" } : {})}
              {...(cut ? { "data-cut": "" } : {})}
              // The row on the playoff line trades its hairline for a rule in the ink, so the cut reads at a glance.
              className={`desktop:grid-cols-[1.5rem_minmax(0,1fr)_minmax(3rem,26%)_2.5rem_2.75rem] gap-x-sp-3 py-sp-2 relative grid grid-cols-[1.5rem_minmax(0,1fr)_minmax(2.5rem,16%)_2.5rem_2.75rem] items-center ${cut ? "border-ink-2 border-b-2" : "border-rule border-b last:border-b-0"}`}
              {...(live ? riseIn(off, { delay: staggerOf(index) }) : {})}
            >
              <span
                aria-hidden
                className="text-meta text-mute font-mono leading-tight tabular-nums"
              >
                {row.rank}
              </span>
              <span aria-hidden className="gap-sp-2 flex min-w-0 items-baseline">
                <span
                  className={`text-row truncate leading-tight font-semibold ${row.you ? "text-accent-ink" : "text-ink"}`}
                >
                  {row.name}
                </span>
                {/* "You" names the row of Your team in words, so it never rests on the red alone. */}
                {row.you && (
                  <span className="text-meta tracking-caps text-accent-ink flex-none font-mono leading-tight uppercase">
                    You
                  </span>
                )}
              </span>
              <OddsBar odds={row.odds} you={row.you} index={index} live={live} />
              <span
                aria-hidden
                className={`text-meta text-right font-mono leading-tight tabular-nums ${row.you ? "text-accent-ink font-semibold" : "text-ink-2"}`}
              >
                {row.odds === null ? "–" : `${row.odds}%`}
              </span>
              <span
                aria-hidden
                className="text-meta text-ink-2 text-right font-mono leading-tight tabular-nums"
              >
                {row.record}
              </span>
              {cut && (
                <span
                  aria-hidden
                  className="bg-card pl-sp-2 text-meta tracking-caps text-ink-2 absolute right-0 bottom-0 translate-y-1/2 font-mono leading-none uppercase"
                >
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
          className="press group -mx-sp-2 min-h-touch gap-sp-2 rounded-pill px-sp-2 text-body text-accent-ink flex items-center self-start leading-tight font-semibold no-underline"
          {...(live
            ? {
                initial: { opacity: 0 },
                animate: { opacity: 1 },
                transition: fadeIn(VERY_SLOW, 0.3),
              }
            : {})}
        >
          <span>Open The Race</span>
          <ArrowRightIcon
            aria-hidden
            className="size-sp-4 group-hover:translate-x-sp-0 transition-transform duration-150 ease-out motion-reduce:transition-none"
            strokeWidth={2.25}
          />
        </motion.a>
      )}
    </div>
  );
}
