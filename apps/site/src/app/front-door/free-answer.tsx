/**
 * The free answer in the Thread: the plain steps of the tool calls, the text that sharpens from a blur word by word,
 * and the mark that turns from "Checking" to "Checked". useChat reads the stream of the API. No control stops it.
 */
"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { AnimatePresence, motion } from "framer-motion";
import { forwardRef, useEffect, useMemo, useRef } from "react";
import { CheckIcon } from "lucide-react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import type { AskTarget } from "./ask-api";
import { type CheckState, type FreeResult, type FreeView, shownText, viewOf } from "./free-stream";
import { QuestionBubble, Surface, TopicChip } from "./miss-card";
import { QUICK, SMOOTH, STAGGER, fadeIn } from "./motion";

/* The line while Claude writes again after a failed check (decision 11). */
export const FIXING_LINE = "Fixing a number…";

/* The words of a text, each with the space after it. A word keeps its place by its index, so a word that grows as the
   stream adds letters never plays its blur again. */
function StreamText({ text, live }: { text: string; live: boolean }) {
  const words = text.match(/\S+\s*/g) ?? [];
  return (
    <p className="m-0 text-body leading-body text-ink">
      {live ? words.map((word, index) => (
        <span key={index} className="stream-word">
          {word}
        </span>
      )) : text}
    </p>
  );
}

/* A line of work in flight. A band of the ink sweeps the mute text on a linear loop of 2 s, as the shimmer text of
   transitions-dev. With motion off, the line holds still in the mute ink. */
export function Shimmer({ children }: { children: string }) {
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

/* The steps of the tool calls, one line each. Each step lands with a short rise as its call starts, and the step in
   flight shimmers until its result is in, as the thinking states of transitions-dev. */
function Steps({ steps, live }: { steps: FreeView["steps"]; live: boolean }) {
  const off = useMotionOff();
  if (steps.length === 0) return null;
  return (
    <ol aria-label="Steps" className="m-0 flex list-none flex-col gap-sp-1 p-0">
      {steps.map((step, index) => {
        const running = live && !step.done;
        return (
          <motion.li
            key={index}
            className="flex items-center gap-sp-2 font-mono text-meta leading-tight text-mute"
            initial={off ? { opacity: 0 } : { opacity: 0, y: 4, filter: "blur(2px)" }}
            animate={off ? { opacity: 1 } : { opacity: 1, y: 0, filter: "blur(0px)" }}
            transition={fadeIn(QUICK, Math.min(index, 6) * STAGGER)}
          >
            <span aria-hidden className={`size-1.5 flex-none rounded-full ${step.done ? "bg-mute" : "bg-ink"}`} />
            {running ? <Shimmer>{`${step.line}…`}</Shimmer> : <span>{step.line}</span>}
          </motion.li>
        );
      })}
    </ol>
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

/* The body of a free answer: the steps, the text, and the check. A failed check fades the first text out, and the
   rewrite streams under the fixing line. */
export function FreeBody({ view, live }: { view: FreeView; live: boolean }) {
  const off = useMotionOff();
  const fixing = view.second !== null;
  return (
    <>
      <Steps steps={view.steps} live={live} />
      <AnimatePresence mode="wait" initial={false}>
        {fixing ? (
          <motion.div key="second" className="flex flex-col gap-sp-2" {...(off ? {} : { initial: { opacity: 0 }, animate: { opacity: 1 } })} transition={fadeIn(QUICK)}>
            {view.second === "" && (
              <p className="m-0 text-body leading-tight font-semibold">
                <Shimmer>{FIXING_LINE}</Shimmer>
              </p>
            )}
            {view.second && <StreamText text={view.second} live={live} />}
          </motion.div>
        ) : (
          view.first && (
            <motion.div
              key="first"
              exit={off ? { opacity: 0 } : { opacity: 0, filter: "blur(2px)" }}
              transition={{ duration: QUICK, ease: SMOOTH }}
            >
              <StreamText text={view.first} live={live} />
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

/* A free answer that the browser kept. It shows as it ended, with no stream and no API call. */
export const FreeAnswerCard = forwardRef<HTMLElement, Shared & { result: FreeResult }>(function FreeAnswerCard(
  { question, result, teamName, onPick },
  ref,
) {
  const view: FreeView = { steps: result.steps.map((line) => ({ line, done: true })), first: result.text, second: null, check: "checked", suggestion: result.suggestion, closest: null };
  return (
    <article ref={ref} aria-label={question} className="flex scroll-mt-sp-6 flex-col gap-sp-3">
      <QuestionBubble question={question} />
      <Surface>
        <FreeBody view={view} live={false} />
        <SuggestionChip suggestion={result.suggestion} teamName={teamName} onPick={onPick} />
      </Surface>
    </article>
  );
});

/* A free answer as it streams. On the end it hands the Thread a checked result, the closest Topics of an honest miss,
   or an error, so the Thread keeps only what ended. It shows no stop control (AT-55). */
export const FreeAnswerLive = forwardRef<
  HTMLElement,
  Shared & {
    target: AskTarget;
    passphrase: string;
    body: { roster_id: number; week: number };
    onDone: (result: FreeResult) => void;
    onMiss: (closest: string[]) => void;
    onError: () => void;
  }
>(function FreeAnswerLive({ question, target, passphrase, body, teamName, onPick, onDone, onMiss, onError }, ref) {
  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: `${target.url}/clients/${encodeURIComponent(target.client)}/ask/free`,
        headers: { "X-League-Passphrase": passphrase },
        // The API reads only these fields, so the prompt of Claude is the question and never a message of the chat.
        body: { question, ...body },
      }),
    [target, passphrase, question, body],
  );
  const { messages, sendMessage, status, error } = useChat({ transport });
  const sent = useRef(false);
  const ended = useRef(false);
  useEffect(() => {
    // The strict mode of React mounts twice in development, and one question makes one request.
    if (sent.current) return;
    sent.current = true;
    void sendMessage({ text: question });
  }, [sendMessage, question]);
  const view = viewOf(messages.findLast((message) => message.role === "assistant"));
  useEffect(() => {
    if (ended.current) return;
    if (error || status === "error") {
      ended.current = true;
      onError();
    } else if (status === "ready" && sent.current && view.check === "checked") {
      ended.current = true;
      onDone({ steps: view.steps.map((step) => step.line), text: shownText(view), suggestion: view.suggestion });
    } else if (status === "ready" && view.closest) {
      ended.current = true;
      onMiss(view.closest);
    } else if (status === "ready" && messages.length > 1 && view.check !== "checked") {
      // A stream that ends with no check is an error, never a pass.
      ended.current = true;
      onError();
    }
  });
  return (
    <article ref={ref} aria-label={question} aria-busy={status !== "ready"} className="flex scroll-mt-sp-6 flex-col gap-sp-3">
      <QuestionBubble question={question} />
      <Surface>
        {view.steps.length === 0 && !view.first && (
          <p className="m-0 font-mono text-meta leading-tight">
            <Shimmer>Reading the league data…</Shimmer>
          </p>
        )}
        <FreeBody view={view} live />
        {view.check === "checked" && <SuggestionChip suggestion={view.suggestion} teamName={teamName} onPick={onPick} />}
      </Surface>
    </article>
  );
});
