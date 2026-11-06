/**
 * The lower third of a regular week in the replay: a red plate with "WEEK N FINAL" and the median, over a crawl of the
 * scores of the week. Only the plate scales; its text fades in, so the text never stretches.
 */
import { motion } from "framer-motion";
import { oneDecimal } from "@cpc/design/format/format";
import { enter, type Pace } from "./pace";
import type { ReplayWeek } from "./season";

/* One pass of the crawl, in seconds. It is slow, so a name stays readable as it passes. */
const CRAWL = 14;

function Scores({ week }: { week: ReplayWeek }) {
  return (
    <>
      {week.games.map(({ teams: [a, b] }) => (
        <span key={`${a.roster_id}-${b.roster_id}`} className="whitespace-nowrap">
          {`${a.name} ${oneDecimal(a.score)}`}
          <span className="px-sp-1 text-on-dark-muted">·</span>
          {`${b.name} ${oneDecimal(b.score)}`}
        </span>
      ))}
    </>
  );
}

export function LowerThird({ week, pace }: { week: ReplayWeek; pace: Pace }) {
  const crawl = !pace.off && !pace.still;
  return (
    <div role="group" aria-label={`Week ${week.week} final`} className="flex flex-col gap-sp-1">
      <div className="relative flex items-baseline gap-sp-3 self-start px-sp-3 py-sp-1">
        <motion.span
          aria-hidden="true"
          {...enter(pace, { scaleX: 0 }, { duration: 0.4 })}
          className="absolute inset-0 origin-left rounded-report bg-accent"
        />
        <motion.span
          {...enter(pace, {}, { duration: 0.3, delay: 0.25 })}
          className="relative font-mono text-body font-bold tracking-caps text-white"
        >
          {`WEEK ${week.week} FINAL`}
        </motion.span>
        {week.median !== null && (
          <motion.span
            {...enter(pace, {}, { duration: 0.3, delay: 0.3 })}
            className="relative font-mono text-meta font-bold tracking-caps text-white"
          >
            {`Median ${oneDecimal(week.median)}`}
          </motion.span>
        )}
      </div>
      {crawl ? (
        // The crawl runs two copies of the scores end to end, so the loop has no seam. The copy is hidden from a screen reader.
        <div className="overflow-hidden border-y border-rule-dark py-sp-1">
          <motion.div
            className="flex w-max gap-sp-4 font-mono text-meta text-on-dark-2"
            animate={{ x: ["0%", "-50%"] }}
            transition={{ duration: CRAWL, ease: "linear", repeat: Infinity }}
          >
            <span className="flex gap-sp-4 pr-sp-4">
              <Scores week={week} />
            </span>
            <span aria-hidden="true" className="flex gap-sp-4 pr-sp-4">
              <Scores week={week} />
            </span>
          </motion.div>
        </div>
      ) : (
        <motion.div
          {...enter(pace, {}, { duration: 0.3 })}
          className="flex flex-wrap gap-x-sp-4 gap-y-sp-1 border-y border-rule-dark py-sp-1 font-mono text-meta text-on-dark-2"
        >
          <Scores week={week} />
        </motion.div>
      )}
    </div>
  );
}
