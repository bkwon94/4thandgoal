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
import { SLOW, VERY_SLOW, fadeIn, riseIn } from "./motion";

export const AnswerCard = forwardRef<HTMLElement, { name: string; answer: DoorAnswer; avatars: Record<number, string | null> }>(
  function AnswerCard({ name, answer, avatars }, ref) {
    const off = useMotionOff();
    return (
      <article ref={ref} aria-label={name} className="flex scroll-mt-door-under-head flex-col gap-sp-3">
        {/* The tap reads as the manager's question, on the right as in a chat. */}
        <motion.p className="m-0 max-w-[85%] self-end rounded-hero rounded-br-letter bg-ink px-sp-4 py-sp-2 text-body leading-tight font-semibold text-card" {...riseIn(off)}>
          {name}
        </motion.p>
        <AnswerBody answer={answer} avatars={avatars} />
      </article>
    );
  },
);

/* The data block, the text, and the link of one Answer. The newest Answer shows it on a card that settles in. An
   opened fold shows it flat, with no card and no settle, so a reread opens calm (decision 08). A live Answer puts its
   streamed text in `children`, under the data block and above the link. */
export function AnswerBody({
  answer,
  avatars,
  flat = false,
  children,
}: {
  // The body reads only the parts of an Answer that it shows, so a personal Answer from the API fits it too.
  answer: Pick<DoorAnswer, "stats" | "rows" | "text" | "href">;
  avatars: Record<number, string | null>;
  flat?: boolean;
  children?: ReactNode;
}) {
  const off = useMotionOff();
  return (
    /* The data block settles from a soft blur at 0.98 (decision 07). With motion off, it only fades in. */
    <motion.div
      className={flat ? "flex flex-col gap-sp-4 pt-sp-1 pb-sp-5" : "flex flex-col gap-sp-4 rounded-card border border-rule bg-card p-sp-4"}
      initial={flat ? false : off ? { opacity: 0 } : { opacity: 0, scale: 0.98, filter: "blur(6px)" }}
      animate={off ? { opacity: 1 } : { opacity: 1, scale: 1, filter: "blur(0px)" }}
      transition={fadeIn(SLOW, 0.08)}
    >
      {answer.stats.length > 0 && (
        // Each stat takes the width of its own value, so three short stats share one row on a phone and a long value
        // such as "12th of 12" wraps to the next row whole.
        <dl className="m-0 flex flex-wrap gap-x-sp-6 gap-y-sp-3">
          {answer.stats.map((stat) => (
            <div key={stat.label} className="flex min-w-0 flex-col gap-sp-1">
              <dt className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">{stat.label}</dt>
              <dd className="m-0 text-stat leading-tight font-bold whitespace-nowrap tabular-nums">{stat.value}</dd>
            </div>
          ))}
        </dl>
      )}
      {answer.rows.length > 0 && (
        <ul className="m-0 flex list-none flex-col border-t border-rule p-0">
          {answer.rows.map((row, index) => (
            <AnswerRow key={`${row.label}-${index}`} row={row} avatar={row.roster_id === null ? undefined : avatars[row.roster_id]} />
          ))}
        </ul>
      )}
      {answer.text.length > 0 && (
        <motion.div className="flex flex-col gap-sp-3" {...(flat ? {} : riseIn(off, { delay: 0.2, text: true }))}>
          {answer.text.map((paragraph, index) => (
            <p key={index} className="m-0 text-body leading-body text-ink-2">
              {paragraph}
            </p>
          ))}
        </motion.div>
      )}
      {children}
      {answer.href !== null && (
        <motion.a
          href={answer.href}
          className="press group -mx-sp-2 flex min-h-touch items-center gap-sp-2 self-start rounded-pill px-sp-2 text-body leading-tight font-semibold text-accent-ink no-underline"
          initial={flat ? false : { opacity: 0 }}
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
