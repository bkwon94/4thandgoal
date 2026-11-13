/**
 * One league Answer in the Thread: the Topic as the question, then the data block, the blurbs of the week, and
 * "Read the full report" to its page. The data block settles first, so the numbers show before the text.
 */
"use client";

import { motion } from "framer-motion";
import { type ReactNode, forwardRef } from "react";
import { ArrowRightIcon } from "lucide-react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import type { DoorAnswer } from "@/lib/data/front-door-data";
import type { TopicRow } from "@/lib/data/topics-schema";
import { type LiveSource, readTimeLine, useLiveMatchup } from "./live-matchup";
import { FAST, SLOW, VERY_SLOW, bubbleIn, fadeIn, riseIn } from "./motion";
import { type AnswerBlock, BlockView } from "./answer-block";
import { TextBlock } from "./text-block";

export const AnswerCard = forwardRef<
  HTMLElement,
  { name: string; answer: DoorAnswer; team: number; avatars: Record<number, string | null>; morph?: string; live?: LiveSource }
>(function AnswerCard({ name, answer, team, avatars, morph, live }, ref) {
    const off = useMotionOff();
    // Your next matchup swaps the card of the weekly build for the live card of the API when it comes. The text and the
    // link stay from topics.json.
    const card = useLiveMatchup(live, answer.topic, team);
    // A tapped Suggestion shares its id with the question, so the chip morphs into the question on the shared layout
    // spring. The question then only fades, because the morph is its move. With motion off it only fades in.
    const shared = bubbleIn(off, morph);
    return (
      <article ref={ref} aria-label={name} className="flex scroll-mt-door-under-head flex-col gap-sp-3">
        {/* The tap reads as the manager's question, on the right as in a chat. */}
        <motion.p className="m-0 max-w-[85%] self-end rounded-hero rounded-br-letter bg-ink px-sp-4 py-sp-2 text-body leading-tight font-semibold text-card" {...shared}>
          {name}
        </motion.p>
        <AnswerBody
          answer={card ? { ...answer, block: card } : answer}
          avatars={avatars}
          asOf={card?.read_at ? readTimeLine(card.read_at) : undefined}
          swap={card?.read_at}
        />
      </article>
    );
});

/* The data block, the text, and the link of one Answer, on a card that settles in. A live Answer puts its streamed
   text in `children`, under the data block and above the link. An Answer with a block, such as the recap card, shows
   the block in the place of its stats and rows, which stay in topics.json only for a reader of version 1. */
export function AnswerBody({
  answer,
  avatars,
  asOf,
  swap,
  children,
}: {
  // The body reads only the parts of an Answer that it shows, so a personal Answer from the API fits it too.
  answer: Pick<DoorAnswer, "stats" | "rows" | "text" | "href"> & { block?: AnswerBlock | null };
  avatars: Record<number, string | null>;
  // A quiet label under the stats that says when the numbers are from, such as "as of today".
  asOf?: string;
  // The key of a block that takes the place of the block shown first, such as the time of the read of a live card.
  swap?: string;
  children?: ReactNode;
}) {
  const off = useMotionOff();
  const block = answer.block ?? null;
  const stats = block ? [] : answer.stats;
  const rows = block ? [] : answer.rows;
  return (
    /* The data block settles from a soft blur at 0.98 (decision 07). With motion off, it only fades in. */
    <motion.div
      className="door-sheen flex flex-col gap-sp-4 rounded-card border border-door-hair bg-card p-sp-4"
      initial={off ? { opacity: 0 } : { opacity: 0, scale: 0.98, filter: "blur(6px)" }}
      animate={off ? { opacity: 1 } : { opacity: 1, scale: 1, filter: "blur(0px)" }}
      transition={fadeIn(SLOW, 0.08)}
    >
      {block && (
        // A swapped block changes its values in place, so it cross-blurs in at rest, with no second entrance of its
        // parts. With motion off it only fades. The first block shows as it is, because the card itself settles in.
        <motion.div
          key={swap ?? "first"}
          initial={swap === undefined ? false : off ? { opacity: 0.4 } : { opacity: 0.4, filter: "blur(2px)" }}
          animate={off ? { opacity: 1 } : { opacity: 1, filter: "blur(0px)" }}
          transition={fadeIn(FAST)}
        >
          <BlockView block={block} live={swap === undefined} />
        </motion.div>
      )}
      {stats.length > 0 && (
        // Each stat takes the width of its own value, so three short stats share one row on a phone and a long value
        // such as "12th of 12" wraps to the next row whole.
        <dl className="m-0 flex flex-wrap gap-x-sp-6 gap-y-sp-3">
          {stats.map((stat) => (
            <div key={stat.label} className="flex min-w-0 flex-col gap-sp-1">
              <dt className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">{stat.label}</dt>
              <dd className="m-0 text-stat leading-tight font-bold whitespace-nowrap tabular-nums">{stat.value}</dd>
            </div>
          ))}
        </dl>
      )}
      {asOf && <p className="m-0 font-mono text-meta leading-tight text-mute">{asOf}</p>}
      {rows.length > 0 && (
        <ul className="m-0 flex list-none flex-col border-t border-rule p-0">
          {rows.map((row, index) => (
            <AnswerRow key={`${row.label}-${index}`} row={row} avatar={row.roster_id === null ? undefined : avatars[row.roster_id]} />
          ))}
        </ul>
      )}
      {answer.text.length > 0 && (
        <motion.div {...riseIn(off, { delay: 0.2, text: true })}>
          {/* Each blurb is one paragraph of the text block, so a blank line keeps them apart. */}
          <TextBlock text={answer.text.join("\n\n")} className="text-ink-2" />
        </motion.div>
      )}
      {children}
      {answer.href !== null && (
        <motion.a
          href={answer.href}
          className="press group -mx-sp-2 flex min-h-touch items-center gap-sp-2 self-start rounded-pill px-sp-2 text-body leading-tight font-semibold text-accent-ink no-underline"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={fadeIn(VERY_SLOW, 0.3)}
        >
          <span>Read the full report</span>
          <ArrowRightIcon
            aria-hidden
            className="size-sp-4 transition-transform duration-150 ease-out group-hover:translate-x-sp-0 motion-reduce:transition-none"
            strokeWidth={2.25}
          />
        </motion.a>
      )}
    </motion.div>
  );
}

/* One line of the data block. The line of Your team carries the ink, so it stands out from the lines around it. */
function AnswerRow({ row, avatar }: { row: TopicRow; avatar: string | null | undefined }) {
  return (
    <li className={`grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-x-sp-3 border-b border-rule py-sp-2 last:border-b-0 ${row.you ? "" : "text-ink-2"}`}>
      {avatar === undefined ? (
        <span aria-hidden className={`h-sp-5 w-sp-1 rounded-pill ${row.you ? "bg-accent" : "bg-rule"}`} />
      ) : avatar ? (
        <img src={avatar} alt="" width={24} height={24} className={`size-sp-6 flex-none rounded-full bg-raised object-cover ${row.you ? "ring-2 ring-accent" : ""}`} />
      ) : (
        <span aria-hidden className="size-sp-6 flex-none rounded-full bg-raised" />
      )}
      <span className="flex min-w-0 flex-col">
        <span className={`truncate text-row leading-tight ${row.you ? "font-bold text-ink" : "font-semibold"}`}>{row.label}</span>
        {row.note && <span className="truncate font-mono text-meta leading-tight text-mute">{row.note}</span>}
      </span>
      <span className={`font-mono text-row leading-tight tabular-nums ${row.you ? "font-bold text-ink" : ""}`}>{row.value}</span>
    </li>
  );
}
