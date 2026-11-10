/**
 * The Answers of the Thread, top to bottom with the newest at the bottom. The newest Answer stays open on its card.
 * Each older Answer folds to one line, its question and one fact, and a tap opens it in place (decision 08).
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { type ReactNode, type RefObject, useEffect, useRef, useState } from "react";
import { ChevronDownIcon } from "lucide-react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import type { DoorAnswer } from "@/lib/data/front-door-data";
import { AnswerBody, AnswerCard } from "./answer-card";
import { QUICK, SMOOTH, fadeIn, morphId } from "./motion";
import type { ThreadItem } from "./ask-thread";
import { topicName } from "./topics";

/* A fold grows and shrinks its height on --duration-fast and --ease-smooth-out, and its content sharpens from
   --blur-small, as the accordion of transitions-dev. The close is the same length, so a quick second tap never jumps. */
const FOLD = { duration: 0.25, ease: SMOOTH } as const;

/* One item of the Thread with its id, so a reply of the API lands in the place of its question. */
export type Entry = ThreadItem & { id: number };

export function Thread({
  entries,
  answers,
  avatars,
  newest,
  renderOther,
}: {
  entries: Entry[];
  answers: Record<number, DoorAnswer[]>;
  avatars: Record<number, string | null>;
  newest: RefObject<HTMLElement | null>;
  // A miss, a note, a question in flight, or the passphrase card has no fold. The front door renders it as its card.
  renderOther: (entry: Exclude<Entry, { kind: "topic" }>, ref: RefObject<HTMLElement | null> | undefined) => ReactNode;
}) {
  // One fold opens at a time, by its place in the Thread. The open fold holds the length of the Thread at the tap, so
  // a new Answer folds each older one again.
  const [opened, setOpened] = useState<{ at: number; length: number } | null>(null);
  const openAt = opened?.length === entries.length ? opened.at : null;
  return (
    <div className="flex flex-col">
      {entries.map((entry, index) => {
        const last = index === entries.length - 1;
        if (entry.kind !== "topic") {
          return (
            <div key={entry.id} className={last && index > 0 ? "pt-sp-6" : ""}>
              {renderOther(entry, last ? newest : undefined)}
            </div>
          );
        }
        const answer = (answers[entry.team] ?? []).find((candidate) => candidate.topic === entry.key);
        if (!answer) return null;
        // A typed question shows as its own bubble. A tapped Topic shows its name.
        const name = entry.question ?? topicName(entry.key);
        return last ? (
          // The newest Answer sits a step below the folds, so the open card reads apart from the list above it.
          <div key={entry.id} className={index > 0 ? "pt-sp-6" : ""}>
            <AnswerCard ref={newest} name={name} answer={answer} avatars={avatars} morph={entry.question === null ? morphId(entry.key) : undefined} />
          </div>
        ) : (
          <Fold
            key={entry.id}
            name={name}
            answer={answer}
            avatars={avatars}
            open={openAt === index}
            onToggle={() => setOpened(openAt === index ? null : { at: index, length: entries.length })}
          />
        );
      })}
    </div>
  );
}

/* One older Answer: a line with its question and one fact, and under it the Answer, flat, while the fold is open. */
function Fold({
  name,
  answer,
  avatars,
  open,
  onToggle,
}: {
  name: string;
  answer: DoorAnswer;
  avatars: Record<number, string | null>;
  open: boolean;
  onToggle: () => void;
}) {
  const off = useMotionOff();
  const article = useRef<HTMLElement>(null);
  const wasOpen = useRef(open);
  // An opened fold scrolls to its top under the Thread header, so the reread starts at its question.
  useEffect(() => {
    if (open && !wasOpen.current) article.current?.scrollIntoView?.({ behavior: off ? "auto" : "smooth", block: "start" });
    wasOpen.current = open;
  }, [open, off]);
  return (
    <motion.article
      ref={article}
      aria-label={name}
      className="scroll-mt-door-under-head border-b border-rule"
      // A card that folds fades to its line, so the change from card to line reads as one move.
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={fadeIn(QUICK)}
    >
      <button
        type="button"
        aria-expanded={open}
        aria-label={`${name}: ${answer.fact}`}
        onClick={onToggle}
        className="press group flex min-h-touch w-full items-center gap-sp-3 py-sp-2 text-left"
      >
        {/* The name keeps its width up to 70% of the line and the fact takes the rest, so a long fact cuts first and
            a long name still leaves room for the start of its fact. */}
        <span aria-hidden className="max-w-[70%] flex-none truncate text-body leading-tight font-semibold text-ink">
          {name}
        </span>
        <span aria-hidden className="min-w-0 flex-1 truncate font-mono text-meta leading-tight text-mute tabular-nums">
          {answer.fact}
        </span>
        <ChevronDownIcon
          aria-hidden
          className={`size-sp-4 flex-none text-mute transition-transform duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] group-hover:text-ink motion-reduce:transition-none ${open ? "-scale-y-100" : ""}`}
          strokeWidth={2.25}
        />
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="body"
            className="overflow-hidden"
            // With motion off, the height jumps and only the opacity moves.
            initial={off ? { opacity: 0 } : { height: 0, opacity: 0, filter: "blur(2px)" }}
            animate={off ? { opacity: 1 } : { height: "auto", opacity: 1, filter: "blur(0px)" }}
            exit={off ? { opacity: 0, transition: fadeIn(QUICK) } : { height: 0, opacity: 0, filter: "blur(2px)" }}
            transition={FOLD}
          >
            <AnswerBody answer={answer} avatars={avatars} flat />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.article>
  );
}
