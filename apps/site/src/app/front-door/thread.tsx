/**
 * The Answers of the Thread, top to bottom with the newest at the bottom. The newest Answer stays open on its card.
 * Each older settled Answer of each kind folds to one line, its question and one fact, and a tap opens it in place
 * (decision 08).
 */
"use client";

import { AnimatePresence, MotionConfig, motion } from "framer-motion";
import { type ReactNode, type RefObject, useEffect, useRef, useState } from "react";
import { ChevronDownIcon } from "lucide-react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import type { DoorAnswer } from "@/lib/data/front-door-data";
import { AnswerBody, AnswerCard } from "./answer-card";
import { QUICK, SMOOTH, fadeIn, morphId } from "./motion";
import type { ThreadItem } from "./ask-thread";
import type { TradeAnswer } from "./trade-api";
import { topicName } from "./topics";

/* The opened body of a fold of a kind other than a league Topic: the card of the item, flat. The fold line already
   shows the question, so the bubble of the card hides. Each surface of the card drops its frame and its fill, so the
   body reads flat with the hairline of the fold, not as a card inside a card (decision 08). */
const FLAT_CARD =
  "pt-sp-1 pb-sp-5 [&>article>p:first-child]:hidden [&_.door-sheen]:rounded-none [&_.door-sheen]:border-0 [&_.door-sheen]:bg-transparent [&_.door-sheen]:p-0 [&_.door-sheen]:shadow-none";

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
  teamName,
  renderOther,
}: {
  entries: Entry[];
  answers: Record<number, DoorAnswer[]>;
  avatars: Record<number, string | null>;
  newest: RefObject<HTMLElement | null>;
  // The name of a team that is not Your team, for the line of a fold. Your team gives undefined.
  teamName: (team: number) => string | undefined;
  // The front door renders each item that is not a league Topic as its card: a trade, a free or personal Answer, a
  // miss, a cap line, a note, a question in flight, or the passphrase card.
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
        const fold = {
          open: openAt === index,
          onToggle: () => setOpened(openAt === index ? null : { at: index, length: entries.length }),
        };
        if (entry.kind !== "topic") {
          // An item in flight never folds, so its stream or its field stays live.
          const line = last ? null : foldLine(entry, teamName);
          if (line) {
            return (
              <Fold key={entry.id} name={line.name} fact={line.fact} {...fold}>
                {/* The card settled once already, so a reopen drops each move and blur of its parts and keeps the fades,
                    and only the fold moves. */}
                <MotionConfig reducedMotion="always">
                  <div className={FLAT_CARD}>{renderOther(entry, undefined)}</div>
                </MotionConfig>
              </Fold>
            );
          }
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
          <Fold key={entry.id} name={name} fact={answer.fact} {...fold}>
            <AnswerBody answer={answer} avatars={avatars} flat />
          </Fold>
        );
      })}
    </div>
  );
}

/* The name of a personal Topic in the Thread: the typed question, else the Topic name, with the team after it when it
   is not Your team. */
export function personalName(entry: { key: string; question: string | null }, other: string | undefined): string {
  const topic = topicName(entry.key);
  return entry.question ?? (other ? `${topic}: ${other}` : topic);
}

/* The first sentence of a text, for the line of a fold. A text with no stop gives all of it, and the line cuts it. */
const firstSentence = (text: string) => text.match(/^.*?[.!?](?=\s|$)/s)?.[0] ?? text;

/* The one fact of each trade Answer: the Lean of a trade check, the count of the trade ideas, or the players to sell. */
function tradeFact(answer: TradeAnswer): string {
  switch (answer.kind) {
    case "check":
      return answer.document.lean;
    case "form":
      return "Pick the players on the Trade page";
    case "ideas": {
      const count = answer.document.trades.length;
      return count === 0 ? "No offer found" : count === 1 ? "1 offer" : `${count} offers`;
    }
    case "sell": {
      const names = answer.document.picks.map((pick) => pick.player.name);
      return names.length === 0 ? "No clear sell" : `Sell ${names.join(", ")}`;
    }
  }
}

/* The line of the fold of an item that is not a league Topic: its question and one fact from its own data. An item in
   flight has no line, so it never folds: a question that routes, the passphrase field, or a stream that has not ended. */
export function foldLine(entry: Exclude<ThreadItem, { kind: "topic" }>, teamName: (team: number) => string | undefined): { name: string; fact: string } | null {
  switch (entry.kind) {
    case "pending":
    case "passphrase":
      return null;
    case "trade":
      return entry.answer ? { name: entry.question, fact: tradeFact(entry.answer) } : null;
    case "free":
      return entry.result ? { name: entry.question, fact: firstSentence(entry.result.text) } : null;
    case "personal":
      return entry.result ? { name: personalName(entry, teamName(entry.team)), fact: entry.result.block.fact } : null;
    case "miss":
      return { name: entry.question, fact: entry.closest.length > 0 ? `No answer · try ${topicName(entry.closest[0])}` : "No answer" };
    case "cap":
    case "note":
      return { name: entry.question, fact: entry.line };
  }
}

/* One older Answer: a line with its question and one fact, and under it the Answer, flat, while the fold is open. */
function Fold({
  name,
  fact,
  open,
  onToggle,
  children,
}: {
  name: string;
  fact: string;
  open: boolean;
  onToggle: () => void;
  children: ReactNode;
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
        aria-label={`${name}: ${fact}`}
        onClick={onToggle}
        className="press group flex min-h-touch w-full items-center gap-sp-3 py-sp-2 text-left"
      >
        {/* The name keeps its width up to 70% of the line and the fact takes the rest, so a long fact cuts first and
            a long name still leaves room for the start of its fact. */}
        <span aria-hidden className="max-w-[70%] flex-none truncate text-body leading-tight font-semibold text-ink">
          {name}
        </span>
        <span aria-hidden className="min-w-0 flex-1 truncate font-mono text-meta leading-tight text-mute tabular-nums">
          {fact}
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
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.article>
  );
}
