/**
 * The Answers of the ask box that hold no Topic: the honest miss and the cap line, each with its 3 closest Topics, a
 * calm note such as the refusal, the line while the question routes, and the field of the league passphrase.
 */
"use client";

import { motion } from "framer-motion";
import { forwardRef, useState, type ReactNode } from "react";
import { ArrowUpIcon } from "lucide-react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { useKeyboardField } from "@cpc/design/shell/keyboard";
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
      className="m-0 max-w-[85%] self-end rounded-hero rounded-br-letter bg-ink px-sp-4 py-sp-2 text-body leading-tight font-semibold break-words text-card"
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
      className="door-sheen flex flex-col gap-sp-3 rounded-card border border-door-hair bg-card p-sp-4"
      initial={off ? { opacity: 0 } : { opacity: 0, y: 6, filter: "blur(3px)" }}
      animate={off ? { opacity: 1 } : { opacity: 1, y: 0, filter: "blur(0px)" }}
      transition={fadeIn(SLOW, 0.08)}
    >
      {children}
    </motion.div>
  );
}

/* One Topic chip, as a Suggestion chip with no fact. A chip of another team names that team after the Topic. */
export function TopicChip({ topic, team, index, onPick }: { topic: string; team?: string; index: number; onPick: (key: string) => void }) {
  const off = useMotionOff();
  const name = TOPICS.find((candidate) => candidate.key === topic)?.name ?? topic;
  return (
    <motion.button
      type="button"
      onClick={() => onPick(topic)}
      initial={off ? { opacity: 0 } : { opacity: 0, scale: 0.97 }}
      animate={off ? { opacity: 1 } : { opacity: 1, scale: 1 }}
      transition={fadeIn(FAST, 0.2 + index * STAGGER)}
      className="press flex min-h-touch items-center rounded-pill border border-rule bg-page px-sp-4 text-body leading-tight font-semibold text-ink transition-colors duration-150 hover-fine:bg-raised"
    >
      {name}
      {team && <span className="ml-sp-2 font-normal text-mute">{team}</span>}
    </motion.button>
  );
}

/* The closest Topics of a miss or a cap line, as chips that settle in one after another. */
function ClosestTopics({ closest, onPick }: { closest: string[]; onPick: (key: string) => void }) {
  return (
    <div className="flex flex-col gap-sp-2">
      <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">Closest Topics</span>
      <div role="group" aria-label="Closest Topics" className="flex flex-wrap gap-sp-2">
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
  { question: string; closest: string[]; onPick: (key: string) => void; block?: PersonalBlock; avatars?: Record<number, string | null> }
>(function MissCard({ question, closest, onPick, block, avatars = {} }, ref) {
  const shown = block ? shownBlock(block) : null;
  const miss = (
    <>
      <p className="m-0 text-body leading-tight font-semibold text-ink">{MISS_LEAD}</p>
      <ClosestTopics closest={closest} onPick={onPick} />
    </>
  );
  return (
    <article ref={ref} aria-label={question} className="flex scroll-mt-door-under-head flex-col gap-sp-3">
      <QuestionBubble question={question} />
      {shown ? (
        <AnswerBody answer={{ stats: shown.stats, rows: shown.rows, text: [], href: null }} avatars={avatars}>
          {shown.answerBlock && <BlockView block={shown.answerBlock} live={false} />}
          <div className="flex flex-col gap-sp-3">{miss}</div>
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
export const CapCard = forwardRef<HTMLElement, { question: string; line: string; closest: string[]; onPick: (key: string) => void }>(
  function CapCard({ question, line, closest, onPick }, ref) {
    const cut = line.indexOf(". ");
    const lead = cut < 0 ? line : line.slice(0, cut + 1);
    const detail = cut < 0 ? "" : line.slice(cut + 2);
    return (
      <article ref={ref} aria-label={question} className="flex scroll-mt-door-under-head flex-col gap-sp-3">
        <QuestionBubble question={question} />
        <Surface>
          {/* One paragraph, so a screen reader reads the line of the API as one sentence after the other. */}
          <p className="m-0 flex flex-col gap-sp-1 text-body">
            <span className="leading-tight font-semibold text-ink">{lead}</span>
            {/* The space keeps the two sentences apart in the text of the page, and the column hides it. */}
            {detail && <span className="leading-body text-ink-2"> {detail}</span>}
          </p>
          {closest.length > 0 && <ClosestTopics closest={closest} onPick={onPick} />}
        </Surface>
      </article>
    );
  },
);

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
    <article ref={ref} aria-label={question} className="flex scroll-mt-door-under-head flex-col gap-sp-3">
      <QuestionBubble question={question} />
      <Surface>
        <p className="m-0 text-body leading-body text-ink-2">{line}</p>
        {(action || (topic && onPick)) && (
          <div className="flex flex-wrap gap-sp-2">
            {topic && onPick && <TopicChip topic={topic} team={team} index={0} onPick={onPick} />}
            {action && (
              <button
                type="button"
                onClick={action.onClick}
                className="press flex min-h-touch items-center rounded-pill bg-ink px-sp-4 text-body leading-tight font-semibold text-card"
              >
                {action.label}
              </button>
            )}
          </div>
        )}
      </Surface>
    </article>
  );
});

/* The wait while the API routes the question: the first line as a live step in the card, as every kind of Answer
   waits, so the card of the Answer takes its place with the same line. */
export const PendingCard = forwardRef<HTMLElement, { question: string }>(function PendingCard({ question }, ref) {
  return (
    <article ref={ref} aria-label={question} aria-busy="true" className="flex scroll-mt-door-under-head flex-col gap-sp-3">
      <QuestionBubble question={question} />
      <Surface>
        <Steps steps={[]} live />
      </Surface>
    </article>
  );
});

/* The field of the league passphrase. The ask box needs it, so only managers of the league ask. The browser keeps it,
   under the same key as the trade analyzer, so a manager types it once. */
export const PassphraseCard = forwardRef<HTMLElement, { question: string; wrong: boolean; onPassphrase: (value: string) => void }>(
  function PassphraseCard({ question, wrong, onPassphrase }, ref) {
    const [value, setValue] = useState("");
    const typed = value.trim();
    // The field opens the keyboard as the ask box does, so the foot of the Thread moves above the keyboard for it.
    const keyboard = useKeyboardField();
    // The scroll margin is as tall as the foot, so the focused field scrolls into view above the foot, not under it.
    return (
      <article ref={ref} aria-label={question} className="flex scroll-mt-door-under-head scroll-mb-door-foot-clear flex-col gap-sp-3">
        <QuestionBubble question={question} />
        <Surface>
          <p className="m-0 text-body leading-body text-ink-2">
            {wrong ? "That passphrase did not match. Type the league passphrase again." : "Type the league passphrase to ask. You type it once on this phone."}
          </p>
          <form
            aria-label="League passphrase"
            className="flex min-h-ask items-center gap-sp-2 rounded-pill border border-rule bg-page py-sp-1 pr-sp-1 pl-sp-5 transition-[border-color] duration-150 focus-within:border-ink"
            onSubmit={(event) => {
              event.preventDefault();
              if (typed) onPassphrase(typed);
            }}
          >
            <input
              type="password"
              value={value}
              onChange={(event) => setValue(event.target.value)}
              aria-label="League passphrase"
              placeholder="League passphrase"
              autoComplete="current-password"
              // The manager just sent a question, so the field takes the focus and the next keys go to it.
              autoFocus
              enterKeyHint="send"
              {...keyboard}
              className="min-w-0 flex-1 bg-transparent text-lead leading-tight text-ink outline-none placeholder:text-mute focus-visible:outline-none"
            />
            <button
              type="submit"
              aria-label="Ask with this passphrase"
              disabled={!typed}
              className="press flex size-send flex-none items-center justify-center rounded-full bg-accent text-on-dark transition-colors duration-150 disabled:bg-raised disabled:text-mute"
            >
              <ArrowUpIcon aria-hidden className="size-sp-5" strokeWidth={2.25} />
            </button>
          </form>
        </Surface>
      </article>
    );
  },
);
