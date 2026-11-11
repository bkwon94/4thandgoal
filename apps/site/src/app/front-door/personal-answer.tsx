/**
 * A personal Topic in the Thread: the data block settles first from code, then the text sharpens word by word under it,
 * then the mark turns from "Checking" to "Checked" and the link to the full page shows. useChat reads the API stream.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { forwardRef } from "react";
import { RotateCwIcon } from "lucide-react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { AnswerBody } from "./answer-card";
import type { AskTarget } from "./ask-api";
import type { Turn } from "./chat-turns";
import { FreeBody, Shimmer, useAnswerStream } from "./free-answer";
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
   it only fades in. A stale trade Answer shows the same line. */
export function StaleLine({ line, onRefresh }: { line: string; onRefresh: () => void }) {
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
   roster changed since the API kept it, shows dimmed with no "Checked" mark, the stale line, and Refresh (AT-34). It
   takes the place of the live card when the stream ends, so its parts show at once with no fade, and the card never
   goes blank (AT-20). A stale line that shows later still rises in. */
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
      <AnimatePresence initial={false}>
        <article key="kept" ref={ref} aria-label={name} data-stale={stale ? "" : undefined} className="flex scroll-mt-door-under-head flex-col gap-sp-3">
          <QuestionBubble question={name} />
          {/* The stale line comes before the read it warns about, so the manager sees it first. */}
          {stale && <StaleLine line={stale.line} onRefresh={stale.onRefresh} />}
          {/* The dim is an opacity change only, so reduced motion keeps it as is. The link to the full page shows only
              under a "Checked" mark, so a stale read hides it too. */}
          <div className={`flex flex-col transition-opacity duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] ${stale ? "opacity-60" : "opacity-100"}`}>
            <PersonalBody block={result.block} view={view} live={false} href={href} avatars={avatars} />
          </div>
        </article>
      </AnimatePresence>
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
    body: { topic: PersonalTopic; roster_id: number; team: number | null; turns?: Turn[] };
    onDone: (result: PersonalResult) => void;
    onMiss: (closest: string[]) => void;
    onCap: (cap: PersonalCap) => void;
    onError: () => void;
  }
>(function PersonalAnswerLive({ name, href, avatars, target, passphrase, body, onDone, onMiss, onCap, onError }, ref) {
  // The API reads only the body, so the prompt of Claude comes from the facts.
  const { view, busy, kept } = useAnswerStream({
    target,
    passphrase,
    path: "personal",
    body,
    text: name,
    read: personalViewOf,
    settle: (ended) => {
      if (ended.check === "checked" && ended.block && ended.key) {
        onDone({ block: ended.block, text: shownText(ended), key: ended.key });
        return true;
      }
      if (ended.cap) {
        onCap(ended.cap);
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
    <article ref={ref} aria-label={name} aria-busy={busy} className="flex scroll-mt-door-under-head flex-col gap-sp-3">
      <QuestionBubble question={name} />
      {view.block ? (
        // A kept Answer of the API shows whole at once, with no stream of its words (AT-8).
        <PersonalBody block={view.block} view={view} live={!kept} href={href} avatars={avatars} />
      ) : (
        <p className="m-0 px-sp-1 font-mono text-meta leading-tight">
          <Shimmer>{READING_LINE}</Shimmer>
        </p>
      )}
    </article>
  );
});
