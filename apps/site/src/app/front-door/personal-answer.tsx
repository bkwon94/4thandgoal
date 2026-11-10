/**
 * A personal Topic in the Thread: the data block settles first from code, then the text sharpens word by word under it,
 * then the mark turns from "Checking" to "Checked" and the link to the full page shows. useChat reads the API stream.
 */
"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { motion } from "framer-motion";
import { forwardRef, useEffect, useMemo, useRef } from "react";
import { RotateCwIcon } from "lucide-react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { AnswerBody } from "./answer-card";
import type { AskTarget } from "./ask-api";
import { FreeBody, Shimmer } from "./free-answer";
import { shownText } from "./free-stream";
import { QuestionBubble } from "./miss-card";
import { riseIn } from "./motion";
import { type PersonalBlock, type PersonalCap, type PersonalResult, type PersonalTopic, type PersonalView, personalViewOf } from "./personal-stream";

/* The line before the data block lands, while the API reads the rosters now. */
export const READING_LINE = "Reading the rosters…";

type Shared = {
  name: string;
  href: string | null;
  avatars: Record<number, string | null>;
};

/* The card of one personal Answer: the data block, then the text and the check, then the link once the text is checked. */
function PersonalBody({ block, view, live, href, avatars }: { block: PersonalBlock; view: PersonalView; live: boolean; href: string | null; avatars: Shared["avatars"] }) {
  const checked = view.check === "checked";
  return (
    <AnswerBody answer={{ stats: block.stats, rows: block.rows, text: [], href: checked ? href : null }} avatars={avatars}>
      <div className="flex flex-col gap-sp-3">
        <FreeBody view={view} live={live} />
      </div>
    </AnswerBody>
  );
}

/* The label of the action that streams a fresh Answer in place of a stale one. */
export const REFRESH_LABEL = "Refresh";

/* The stale line above a dimmed Answer, and Refresh beside it. The line lands with a short rise, and with motion off
   it only fades in. */
function StaleLine({ line, onRefresh }: { line: string; onRefresh: () => void }) {
  const off = useMotionOff();
  return (
    <motion.div className="flex flex-wrap items-center gap-x-sp-2 gap-y-sp-1 px-sp-1" {...riseIn(off)}>
      <p role="status" className="m-0 text-meta leading-tight font-semibold text-ink">
        {line}
      </p>
      <button
        type="button"
        onClick={onRefresh}
        className="press flex min-h-touch items-center gap-sp-1 rounded-pill border border-door-hair bg-card px-sp-3 text-meta leading-tight font-semibold text-ink hover-fine:bg-raised"
      >
        <RotateCwIcon aria-hidden className="size-sp-4" strokeWidth={2.25} />
        {REFRESH_LABEL}
      </button>
    </motion.div>
  );
}

/* A personal Answer that the browser kept. It shows as it ended, with no stream and no API call. A stale Answer, whose
   roster changed since the API kept it, shows dimmed with no "Checked" mark, the stale line, and Refresh (AT-34). */
export const PersonalAnswerCard = forwardRef<HTMLElement, Shared & { result: PersonalResult; stale?: { line: string; onRefresh: () => void } | null }>(
  function PersonalAnswerCard({ name, href, avatars, result, stale = null }, ref) {
    const view: PersonalView = {
      steps: [],
      first: result.text,
      second: null,
      // A stale read is no longer checked against the roster now, so it loses its mark.
      check: stale ? null : "checked",
      suggestion: null,
      closest: null,
      block: result.block,
      key: result.key,
      cap: null,
    };
    return (
      <article ref={ref} aria-label={name} data-stale={stale ? "" : undefined} className="flex scroll-mt-door-under-head flex-col gap-sp-3">
        <QuestionBubble question={name} />
        {/* The stale line comes before the read it warns about, so the manager sees it first. */}
        {stale && <StaleLine line={stale.line} onRefresh={stale.onRefresh} />}
        {/* The dim is an opacity change only, so reduced motion keeps it as is. The link to the full page shows only
            under a "Checked" mark, so a stale read hides it too. */}
        <div className={`flex flex-col transition-opacity duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] ${stale ? "opacity-60" : "opacity-100"}`}>
          <PersonalBody block={result.block} view={view} live={false} href={href} avatars={avatars} />
        </div>
      </article>
    );
  },
);

/* A personal Answer as it streams. On the end it hands the Thread a checked result, the closest Topics of an honest
   miss, the line of a cap, or an error, so the Thread keeps only what ended. */
export const PersonalAnswerLive = forwardRef<
  HTMLElement,
  Shared & {
    target: AskTarget;
    passphrase: string;
    body: { topic: PersonalTopic; roster_id: number; team: number | null };
    onDone: (result: PersonalResult) => void;
    onMiss: (closest: string[]) => void;
    onCap: (cap: PersonalCap) => void;
    onError: () => void;
  }
>(function PersonalAnswerLive({ name, href, avatars, target, passphrase, body, onDone, onMiss, onCap, onError }, ref) {
  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: `${target.url}/clients/${encodeURIComponent(target.client)}/personal`,
        headers: { "X-League-Passphrase": passphrase },
        // The API reads only these fields, so the prompt of Claude comes from the facts and never from the chat.
        body,
      }),
    [target, passphrase, body],
  );
  const { messages, sendMessage, status, error } = useChat({ transport });
  const sent = useRef(false);
  const ended = useRef(false);
  useEffect(() => {
    // The strict mode of React mounts twice in development, and one tap makes one request.
    if (sent.current) return;
    sent.current = true;
    void sendMessage({ text: name });
  }, [sendMessage, name]);
  const view = personalViewOf(messages.findLast((message) => message.role === "assistant"));
  useEffect(() => {
    if (ended.current) return;
    if (error || status === "error") {
      ended.current = true;
      onError();
    } else if (status === "ready" && view.check === "checked" && view.block && view.key) {
      ended.current = true;
      onDone({ block: view.block, text: shownText(view), key: view.key });
    } else if (status === "ready" && view.cap) {
      ended.current = true;
      onCap(view.cap);
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
    <article ref={ref} aria-label={name} aria-busy={status !== "ready"} className="flex scroll-mt-door-under-head flex-col gap-sp-3">
      <QuestionBubble question={name} />
      {view.block ? (
        <PersonalBody block={view.block} view={view} live href={href} avatars={avatars} />
      ) : (
        <p className="m-0 px-sp-1 font-mono text-meta leading-tight">
          <Shimmer>{READING_LINE}</Shimmer>
        </p>
      )}
    </article>
  );
});
