/**
 * The Answers of the Thread, top to bottom with the newest at the bottom, as a plain chat. Each question and its Answer
 * stay as they rendered, so the manager scrolls up to reread an older one.
 */
"use client";

import { MotionConfig } from "framer-motion";
import { type ReactNode, type RefObject, useState } from "react";
import type { DoorAnswer } from "@/lib/data/front-door-data";
import { AnswerCard } from "./answer-card";
import { morphId } from "./motion";
import { TRADE_TOPIC_OF, type ThreadItem } from "./ask-thread";
import { topicName } from "./topics";

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
  // The front door renders each item that is not a league Topic as its card: a trade, a free or personal Answer, a
  // miss, a cap line, a note, a question in flight, or the passphrase card.
  // `morph` is the id that the newest item shares with its tapped Suggestion, so the chip morphs into its question.
  renderOther: (entry: Exclude<Entry, { kind: "topic" }>, ref: RefObject<HTMLElement | null> | undefined, morph: string | undefined) => ReactNode;
}) {
  // A kept Thread loads whole, so each Answer above the newest one settled on an earlier visit. Those show at rest: a
  // reread plays no rise and no blur again, and only the fades stay. The set holds for the life of the Thread, so a
  // wrapper never changes and no card mounts again.
  const [kept] = useState(() => new Set(entries.slice(0, -1).map((entry) => entry.id)));
  return (
    <div className="flex flex-col">
      {entries.map((entry, index) => {
        const last = index === entries.length - 1;
        // Each entry keeps one element and one key for its life, so an older Answer stays mounted as it rendered and
        // never plays its entrance or its stream again.
        let body: ReactNode;
        if (entry.kind !== "topic") {
          body = renderOther(entry, last ? newest : undefined, last ? morphOf(entry) : undefined);
        } else {
          const answer = (answers[entry.team] ?? []).find((candidate) => candidate.topic === entry.key);
          if (!answer) return null;
          // A typed question shows as its own bubble. A tapped Topic shows its name.
          const name = entry.question ?? topicName(entry.key);
          // Only the newest Answer shares its id with a Suggestion, so a chip never morphs into an older question.
          body = (
            <AnswerCard
              ref={last ? newest : undefined}
              name={name}
              answer={answer}
              avatars={avatars}
              morph={last ? morphOf(entry) : undefined}
            />
          );
        }
        return (
          // Each Answer sits a step below the one above it, so each question and its Answer read as one turn.
          <div key={entry.id} className={index > 0 ? "pt-sp-6" : ""}>
            <MotionConfig reducedMotion={kept.has(entry.id) ? "always" : "never"}>{body}</MotionConfig>
          </div>
        );
      })}
    </div>
  );
}

/* The id that an item shares with the Suggestion chip that opened it, so the chip morphs into its question. A tapped
   league or personal Topic has no typed question. A tapped trade Topic asks with the name of its Topic, as
   tradeRequestOf reads it. A typed question has no chip, so it gets no id. */
function morphOf(entry: Entry): string | undefined {
  if (entry.kind === "topic" || entry.kind === "personal") return entry.question === null ? morphId(entry.key) : undefined;
  if (entry.kind === "trade") return entry.question === topicName(TRADE_TOPIC_OF[entry.mode]) ? morphId(TRADE_TOPIC_OF[entry.mode]) : undefined;
  return undefined;
}

/* The name of a personal Topic in the Thread: the typed question, else the Topic name, with the team after it when it
   is not Your team. */
export function personalName(entry: { key: string; question: string | null }, other: string | undefined): string {
  const topic = topicName(entry.key);
  return entry.question ?? (other ? `${topic}: ${other}` : topic);
}
