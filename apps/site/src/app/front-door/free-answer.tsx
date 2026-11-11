/**
 * The free answer in the Thread: the plain steps of the tool calls, the text that sharpens from a blur word by word,
 * and the mark that turns from "Checking" to "Checked". useChat reads the stream of the API. No control stops it.
 */
"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport, type UIMessage } from "ai";
import { AnimatePresence, motion } from "framer-motion";
import { forwardRef, useEffect, useMemo, useRef, useState } from "react";
import { CheckIcon } from "lucide-react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { BlockView } from "./answer-block";
import type { AskTarget } from "./ask-api";
import type { Turn } from "./chat-turns";
import { type CheckState, type FreeResult, type FreeView, isKept, newPace, pacedView, shownText, viewOf } from "./free-stream";
import { QuestionBubble, Surface, TopicChip } from "./miss-card";
import { QUICK, SLOW, SMOOTH, STAGGER, VERY_SLOW, fadeIn } from "./motion";
import { Steps } from "./steps";

/* The least time in ms that "Checking" and the fixing line hold on screen, so a fast check still reads as a check
   (AT-20, AT-21): two of --duration-slow, long enough to read one short word. */
export const HOLD_MS = 2 * SLOW * 1000;

/* The wait in ms from "Checked" to the hand-off to the Thread. The mark, the last words, and the link of the full page
   finish their fades first, so the kept card that takes the place of the live card shows the same frame (AT-20). */
export const SETTLE_MS = 2 * SLOW * 1000;

/* The stream of one live Answer of the API at `path` under /clients/<slug>/. It sends `text` once, and reads each
   assistant message into a view with `read`. The view holds "Checking" and the fixing line on screen for HOLD_MS. On
   the end it calls `settle` once with the view, SETTLE_MS after "Checked" shows, or `onError` once on a failed call.
   `settle` returns false when it has no end for the view, and a stream that then ends with no "Checked" mark is an
   error, never a pass. `kept` is true for a kept Answer of the API, which shows whole at once with no hold. */
export function useAnswerStream<V extends FreeView>({
  target,
  passphrase,
  path,
  body,
  text,
  read,
  settle,
  onError,
}: {
  target: AskTarget;
  passphrase: string;
  path: string;
  body: object;
  text: string;
  read: (message: UIMessage | undefined) => V;
  settle: (view: V) => boolean;
  onError: () => void;
}): { view: V; busy: boolean; kept: boolean } {
  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: `${target.url}/clients/${encodeURIComponent(target.client)}/${path}`,
        headers: { "X-League-Passphrase": passphrase },
        // The API reads only these fields, so the prompt of Claude never comes from a message of the chat.
        body,
      }),
    [target, passphrase, path, body],
  );
  const { messages, sendMessage, status, error } = useChat({ transport });
  const sent = useRef(false);
  const ended = useRef(false);
  useEffect(() => {
    // The strict mode of React mounts twice in development, and one question or tap makes one request.
    if (sent.current) return;
    sent.current = true;
    void sendMessage({ text });
  }, [sendMessage, text]);
  const message = messages.findLast((candidate) => candidate.role === "assistant");
  const raw = read(message);
  const kept = isKept(message);
  // The pace keeps the time that each held state first showed. Each read of the time is in this render, so the view
  // and the time of its next change agree.
  const pace = useRef(newPace());
  const checkedAt = useRef<number | null>(null);
  const [, wakeUp] = useState(0);
  const now = performance.now();
  const { view, wake } = kept ? { view: raw, wake: null } : pacedView(raw, pace.current, now, HOLD_MS);
  if (view.check === "checked") checkedAt.current ??= now;
  // The time that the hand-off may run: at once for an end with no mark, else SETTLE_MS after "Checked" shows.
  const settleAt = wake ?? (view.check === "checked" ? checkedAt.current! + SETTLE_MS : null);
  useEffect(() => {
    if (ended.current || settleAt === null || settleAt <= now) return;
    const timer = setTimeout(() => wakeUp((count) => count + 1), settleAt - now);
    return () => clearTimeout(timer);
  });
  useEffect(() => {
    if (ended.current) return;
    if (error || status === "error") {
      ended.current = true;
      onError();
    } else if (status !== "ready" || (settleAt !== null && settleAt > now)) {
      // The stream runs, or a held state or the fades of "Checked" still show.
    } else if (sent.current && settle(view)) {
      ended.current = true;
    } else if (messages.length > 1 && raw.check !== "checked") {
      // A stream that ends with no check is an error, never a pass.
      ended.current = true;
      onError();
    }
  });
  return { view, busy: status !== "ready", kept };
}

/* The line while Claude writes again after a failed check (decision 11). */
export const FIXING_LINE = "Fixing a number…";

/* The words of a text, each with the space after it. A word keeps its place by its index, so a word that grows as the
   stream adds letters never plays its blur again. One read of the stream can hold many words, so the new words of a
   read sweep in one after another on --duration-stagger, and the whole read takes no more than --duration-very-slow
   (AT-44). A word that comes while a sweep runs starts after the last word of that sweep, so the words keep their
   order. Each word keeps the delay it got as it first showed, so a later render never plays its blur again. */
function StreamText({ text, live }: { text: string; live: boolean }) {
  const words = text.match(/\S+\s*/g) ?? [];
  const delays = useRef<number[]>([]);
  // The time that the last word of the sweep starts.
  const sweepEnd = useRef(0);
  const fresh = words.length - delays.current.length;
  if (live && fresh > 0) {
    const now = performance.now();
    const step = Math.min(STAGGER, VERY_SLOW / fresh) * 1000;
    let at = Math.max(now, sweepEnd.current);
    for (let index = 0; index < fresh; index++) {
      delays.current.push(at - now);
      at += step;
    }
    sweepEnd.current = at - step;
  }
  return (
    <p className="m-0 text-body leading-body text-ink">
      {live ? words.map((word, index) => (
        <span key={index} className="stream-word" style={{ animationDelay: `${Math.round(delays.current[index] ?? 0)}ms` }}>
          {word}
        </span>
      )) : text}
    </p>
  );
}

/* A line of work in flight. A band of the ink sweeps the mute text on a linear loop of 2 s, as the shimmer text of
   transitions-dev. With motion off, the line holds still in the mute ink. */
function Shimmer({ children }: { children: string }) {
  const off = useMotionOff();
  if (off) return <span className="text-mute">{children}</span>;
  return (
    <motion.span
      className="bg-clip-text text-transparent [background-image:linear-gradient(90deg,var(--color-mute)_0%,var(--color-mute)_40%,var(--color-ink)_50%,var(--color-mute)_60%,var(--color-mute)_100%)] [background-size:400%_100%]"
      initial={{ backgroundPosition: "100% 0%" }}
      animate={{ backgroundPosition: "0% 0%" }}
      transition={{ duration: 2, ease: "linear", repeat: Infinity }}
    >
      {children}
    </motion.span>
  );
}

/* The mark of the check. "Checking" sits in the mute ink, and "Checked" takes the ink with a check, through a soft
   cross-blur in place with no bounce and no move (AT-20). */
function CheckMark({ state, live }: { state: CheckState; live: boolean }) {
  const off = useMotionOff();
  const checked = state === "checked";
  return (
    <p role="status" className="m-0 flex min-h-sp-5 items-center text-meta leading-tight font-semibold">
      {/* A live mark fades in as it first shows. A kept answer shows its mark at once. */}
      <AnimatePresence mode="popLayout" initial={live}>
        <motion.span
          key={checked ? "checked" : "checking"}
          className={`inline-flex items-center gap-sp-1 ${checked ? "text-ink" : "text-mute"}`}
          initial={off ? { opacity: 0 } : { opacity: 0, filter: "blur(2px)" }}
          animate={off ? { opacity: 1 } : { opacity: 1, filter: "blur(0px)" }}
          exit={off ? { opacity: 0 } : { opacity: 0, filter: "blur(2px)" }}
          transition={{ duration: 0.2, ease: "easeInOut" }}
        >
          {checked ? <CheckIcon aria-hidden className="size-sp-4" strokeWidth={2.5} /> : <span aria-hidden className="size-sp-4 rounded-full border-2 border-rule" />}
          {checked ? "Checked" : "Checking"}
        </motion.span>
      </AnimatePresence>
    </p>
  );
}

/* The body of a free answer: the steps, the text with its block, and the check. The steps wait until the check or the text comes,
   with `first` as the stand-in line before the first step. The text shows only with "Checked", and its words sweep in
   from a blur. A failed check shows the fixing line, and the checked rewrite takes its place. */
export function FreeBody({ view, live, first }: { view: FreeView; live: boolean; first?: string }) {
  const off = useMotionOff();
  const fixing = view.second !== null;
  // The steps of the tool calls are done once the check or the text comes, so the wait ends there.
  const waiting = live && view.check === null && !view.first && !fixing;
  return (
    <>
      <Steps steps={view.steps} live={waiting} first={first} />
      <AnimatePresence mode="wait" initial={false}>
        {fixing ? (
          <motion.div key="second" className="flex flex-col gap-sp-4" {...(off ? {} : { initial: { opacity: 0 }, animate: { opacity: 1 } })} transition={fadeIn(QUICK)}>
            {view.second === "" && (
              <p className="m-0 text-body leading-tight font-semibold">
                <Shimmer>{FIXING_LINE}</Shimmer>
              </p>
            )}
            {view.second && <StreamText text={view.second} live={live} />}
            {view.second && view.answerBlock && <BlockView block={view.answerBlock} live={live} />}
          </motion.div>
        ) : (
          view.first && (
            <motion.div
              key="first"
              exit={off ? { opacity: 0 } : { opacity: 0, filter: "blur(2px)" }}
              transition={{ duration: QUICK, ease: SMOOTH }}
              className="flex flex-col gap-sp-4"
            >
              <StreamText text={view.first} live={live} />
              {view.answerBlock && <BlockView block={view.answerBlock} live={live} />}
            </motion.div>
          )
        )}
      </AnimatePresence>
      {view.check && view.check !== "fixing" && view.check !== "failed" && <CheckMark state={view.check} live={live} />}
    </>
  );
}

type Shared = {
  question: string;
  teamName: (team: number | null) => string | undefined;
  onPick: (key: string, team: number | null) => void;
};

/* The chip of the top Topic of a half fit, under a checked answer (AT-12). */
function SuggestionChip({ suggestion, teamName, onPick }: { suggestion: FreeResult["suggestion"] } & Omit<Shared, "question">) {
  if (!suggestion) return null;
  return (
    <div className="flex flex-wrap gap-sp-2">
      <TopicChip topic={suggestion.topic} team={teamName(suggestion.team)} index={0} onPick={(key) => onPick(key, suggestion.team)} />
    </div>
  );
}

/* A free answer that the browser kept. It shows as it ended, with no stream and no API call. It takes the place of
   the live card when the stream ends, so its parts show at once with no fade, and the card never goes blank (AT-20). */
export const FreeAnswerCard = forwardRef<HTMLElement, Shared & { result: FreeResult }>(function FreeAnswerCard(
  { question, result, teamName, onPick },
  ref,
) {
  const view: FreeView = { steps: result.steps.map((line) => ({ line, done: true })), first: result.text, second: null, answerBlock: result.block ?? null, check: "checked", suggestion: result.suggestion, closest: null };
  return (
    <AnimatePresence initial={false}>
      <article key="kept" ref={ref} aria-label={question} className="flex scroll-mt-sp-6 flex-col gap-sp-3">
        <QuestionBubble question={question} />
        <Surface>
          <FreeBody view={view} live={false} />
          <SuggestionChip suggestion={result.suggestion} teamName={teamName} onPick={onPick} />
        </Surface>
      </article>
    </AnimatePresence>
  );
});

/* A free answer as it streams. On the end it hands the Thread a checked result, the closest Topics of an honest miss,
   or an error, so the Thread keeps only what ended. It shows no stop control (AT-55). */
export const FreeAnswerLive = forwardRef<
  HTMLElement,
  Shared & {
    target: AskTarget;
    passphrase: string;
    body: { roster_id: number; week: number; turns?: Turn[] };
    onDone: (result: FreeResult) => void;
    onMiss: (closest: string[]) => void;
    onError: () => void;
  }
>(function FreeAnswerLive({ question, target, passphrase, body, teamName, onPick, onDone, onMiss, onError }, ref) {
  // The question goes in the body, so the prompt of Claude is the question.
  const fields = useMemo(() => ({ question, ...body }), [question, body]);
  const { view, busy, kept } = useAnswerStream({
    target,
    passphrase,
    path: "ask/free",
    body: fields,
    text: question,
    read: viewOf,
    settle: (ended) => {
      if (ended.check === "checked") {
        onDone({ steps: ended.steps.map((step) => step.line), text: shownText(ended), suggestion: ended.suggestion, block: ended.answerBlock });
        return true;
      }
      if (ended.closest) {
        onMiss(ended.closest);
        return true;
      }
      return false;
    },
    onError,
  });
  return (
    <article ref={ref} aria-label={question} aria-busy={busy} className="flex scroll-mt-sp-6 flex-col gap-sp-3">
      <QuestionBubble question={question} />
      <Surface>
        {/* A kept Answer of the API shows whole at once, with no stream of its words. */}
        <FreeBody view={view} live={!kept} />
        {view.check === "checked" && <SuggestionChip suggestion={view.suggestion} teamName={teamName} onPick={onPick} />}
      </Surface>
    </article>
  );
});
