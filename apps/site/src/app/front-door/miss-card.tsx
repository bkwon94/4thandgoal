/**
 * The Answers of the ask box that hold no Topic: the honest miss and the cap line, each with its 3 closest Topics, a
 * calm note such as the refusal, and the line while the question routes.
 */
"use client";

import { PendingButton } from "@cpc/design/ui/pending-button";
import { motion } from "framer-motion";
import { forwardRef, type ReactNode } from "react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { BlockView } from "./answer-block";
import { AnswerBody } from "./answer-card";
import { FAST, SLOW, STAGGER, bubbleIn, fadeIn } from "./motion";
import { type PersonalBlock, shownBlock } from "./personal-stream";
import { Steps } from "./steps";
import { TOPICS } from "./topics";

/* What the site holds and what it does not, as the state of the route says it. One line serves each miss, so the site
   never names one cause that the route did not check. The line says only that the site cannot answer. */
export const MISS_LEAD = "I can't answer that.";

/* The typed question, on the right as in a chat. A tapped Suggestion passes its `morph` id, so the chip morphs into it. */
export function QuestionBubble({ question, morph }: { question: string; morph?: string }) {
  const off = useMotionOff();
  return (
    <motion.p
      className="rounded-hero rounded-br-letter bg-ink px-sp-4 py-sp-2 text-body text-card m-0 max-w-[85%] self-end leading-tight font-semibold break-words"
      {...bubbleIn(off, morph)}
    >
      {question}
    </motion.p>
  );
}

/* The surface of each card here: the plain card of the Thread, which settles in with a soft fade under the bubble. */
export function Surface({ children }: { children: ReactNode }) {
  const off = useMotionOff();
  return (
    <motion.div
      className="door-sheen gap-sp-3 rounded-card border-door-hair bg-card p-sp-4 flex flex-col border"
      initial={off ? { opacity: 0 } : { opacity: 0, y: 6, filter: "blur(3px)" }}
      animate={off ? { opacity: 1 } : { opacity: 1, y: 0, filter: "blur(0px)" }}
      transition={fadeIn(SLOW, 0.08)}
    >
      {children}
    </motion.div>
  );
}

/* One Topic chip, as a Suggestion chip with no fact. A chip of another team names that team after the Topic. */
export function TopicChip({
  topic,
  team,
  index,
  onPick,
}: {
  topic: string;
  team?: string;
  index: number;
  onPick: (key: string) => void;
}) {
  const off = useMotionOff();
  const name = TOPICS.find((candidate) => candidate.key === topic)?.name ?? topic;
  return (
    <motion.button
      type="button"
      onClick={() => onPick(topic)}
      initial={off ? { opacity: 0 } : { opacity: 0, scale: 0.97 }}
      animate={off ? { opacity: 1 } : { opacity: 1, scale: 1 }}
      transition={fadeIn(FAST, 0.2 + index * STAGGER)}
      className="press min-h-touch rounded-pill border-rule bg-page px-sp-4 text-body text-ink hover-fine:bg-raised flex items-center border leading-tight font-semibold transition-colors duration-150"
    >
      {name}
      {team && <span className="ml-sp-2 text-mute font-normal">{team}</span>}
    </motion.button>
  );
}

/* The closest Topics of a miss or a cap line, as chips that settle in one after another. */
function ClosestTopics({ closest, onPick }: { closest: string[]; onPick: (key: string) => void }) {
  return (
    <div className="gap-sp-2 flex flex-col">
      <span className="text-meta tracking-caps text-mute font-mono leading-tight uppercase">
        Closest Topics
      </span>
      <div role="group" aria-label="Closest Topics" className="gap-sp-2 flex flex-wrap">
        {closest.map((topic, index) => (
          <TopicChip key={topic} topic={topic} index={index} onPick={onPick} />
        ))}
      </div>
    </div>
  );
}

/* The honest miss: the question, the line that says the site cannot answer, and the 3 closest Topics. The miss of a
   personal Topic keeps its data block from code, so the line and the chips sit in the place of the text under it. */
export const MissCard = forwardRef<
  HTMLElement,
  {
    question: string;
    closest: string[];
    onPick: (key: string) => void;
    block?: PersonalBlock;
    avatars?: Record<number, string | null>;
  }
>(function MissCard({ question, closest, onPick, block, avatars = {} }, ref) {
  const shown = block ? shownBlock(block) : null;
  const miss = (
    <>
      <p className="text-body text-ink m-0 leading-tight font-semibold">{MISS_LEAD}</p>
      <ClosestTopics closest={closest} onPick={onPick} />
    </>
  );
  return (
    <article
      ref={ref}
      aria-label={question}
      className="scroll-mt-door-under-head gap-sp-3 flex flex-col"
    >
      <QuestionBubble question={question} />
      {shown ? (
        <AnswerBody
          answer={{ stats: shown.stats, rows: shown.rows, text: [], href: null }}
          avatars={avatars}
        >
          {shown.answerBlock && <BlockView block={shown.answerBlock} live={false} />}
          <div className="gap-sp-3 flex flex-col">{miss}</div>
        </AnswerBody>
      ) : (
        <Surface>{miss}</Surface>
      )}
    </article>
  );
});

/* The cap line: the question, the calm line of the API that says why and when the questions come back, and the
   closest Topics. It has the shape and the motion of the honest miss, because both say "not this one, try these".
   The first sentence of the line says why and leads as the miss does, and the rest says when, in the softer ink. */
export const CapCard = forwardRef<
  HTMLElement,
  { question: string; line: string; closest: string[]; onPick: (key: string) => void }
>(function CapCard({ question, line, closest, onPick }, ref) {
  const cut = line.indexOf(". ");
  const lead = cut < 0 ? line : line.slice(0, cut + 1);
  const detail = cut < 0 ? "" : line.slice(cut + 2);
  return (
    <article
      ref={ref}
      aria-label={question}
      className="scroll-mt-door-under-head gap-sp-3 flex flex-col"
    >
      <QuestionBubble question={question} />
      <Surface>
        {/* One paragraph, so a screen reader reads the line of the API as one sentence after the other. */}
        <p className="gap-sp-1 text-body m-0 flex flex-col">
          <span className="text-ink leading-tight font-semibold">{lead}</span>
          {/* The space keeps the two sentences apart in the text of the page, and the column hides it. */}
          {detail && <span className="leading-body text-ink-2"> {detail}</span>}
        </p>
        {closest.length > 0 && <ClosestTopics closest={closest} onPick={onPick} />}
      </Surface>
    </article>
  );
});

/* A calm line under the question, such as the refusal, the free answer to come, or a retry. An optional action and
   an optional Topic chip sit under the line. */
export const NoteCard = forwardRef<
  HTMLElement,
  {
    question: string;
    line: string;
    action?: { label: string; onClick: () => void };
    topic?: string;
    team?: string;
    onPick?: (key: string) => void;
  }
>(function NoteCard({ question, line, action, topic, team, onPick }, ref) {
  return (
    <article
      ref={ref}
      aria-label={question}
      className="scroll-mt-door-under-head gap-sp-3 flex flex-col"
    >
      <QuestionBubble question={question} />
      <Surface>
        <p className="text-body leading-body text-ink-2 m-0">{line}</p>
        {(action || (topic && onPick)) && (
          <div className="gap-sp-2 flex flex-wrap">
            {topic && onPick && <TopicChip topic={topic} team={team} index={0} onPick={onPick} />}
            {action && (
              <PendingButton
                type="button"
                onClick={action.onClick}
                className="press min-h-touch rounded-pill bg-ink px-sp-4 text-body text-card flex items-center leading-tight font-semibold"
              >
                {action.label}
              </PendingButton>
            )}
          </div>
        )}
      </Surface>
    </article>
  );
});

/* The wait while the API routes the question: the first line as a live step in the card, as every kind of Answer
   waits, so the card of the Answer takes its place with the same line. */
export const PendingCard = forwardRef<HTMLElement, { question: string }>(function PendingCard(
  { question },
  ref,
) {
  return (
    <article
      ref={ref}
      aria-label={question}
      aria-busy="true"
      className="scroll-mt-door-under-head gap-sp-3 flex flex-col"
    >
      <QuestionBubble question={question} />
      <Surface>
        <Steps steps={[]} live />
      </Surface>
    </article>
  );
});
