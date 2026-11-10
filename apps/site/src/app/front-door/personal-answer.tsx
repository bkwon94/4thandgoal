/**
 * A personal Topic in the Thread: the data block settles first from code, then the text sharpens word by word under it,
 * then the mark turns from "Checking" to "Checked" and the link to the full page shows. useChat reads the API stream.
 */
"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { forwardRef, useEffect, useMemo, useRef } from "react";
import { AnswerBody } from "./answer-card";
import type { AskTarget } from "./ask-api";
import { FreeBody, Shimmer } from "./free-answer";
import { shownText } from "./free-stream";
import { QuestionBubble } from "./miss-card";
import { type PersonalBlock, type PersonalResult, type PersonalTopic, type PersonalView, personalViewOf } from "./personal-stream";

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

/* A personal Answer that the browser kept. It shows as it ended, with no stream and no API call. */
export const PersonalAnswerCard = forwardRef<HTMLElement, Shared & { result: PersonalResult }>(function PersonalAnswerCard(
  { name, href, avatars, result },
  ref,
) {
  const view: PersonalView = { steps: [], first: result.text, second: null, check: "checked", suggestion: null, closest: null, block: result.block, key: result.key };
  return (
    <article ref={ref} aria-label={name} className="flex scroll-mt-door-under-head flex-col gap-sp-3">
      <QuestionBubble question={name} />
      <PersonalBody block={result.block} view={view} live={false} href={href} avatars={avatars} />
    </article>
  );
});

/* A personal Answer as it streams. On the end it hands the Thread a checked result, the closest Topics of an honest
   miss, or an error, so the Thread keeps only what ended. */
export const PersonalAnswerLive = forwardRef<
  HTMLElement,
  Shared & {
    target: AskTarget;
    passphrase: string;
    body: { topic: PersonalTopic; roster_id: number; team: number | null };
    onDone: (result: PersonalResult) => void;
    onMiss: (closest: string[]) => void;
    onError: () => void;
  }
>(function PersonalAnswerLive({ name, href, avatars, target, passphrase, body, onDone, onMiss, onError }, ref) {
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
