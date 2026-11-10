/**
 * The ask box of the front door: one field and a send button. The send button wakes in the accent once the field holds
 * a question, so the control says it is ready before the thumb reaches it.
 */
"use client";

import { useState } from "react";
import { ArrowUpIcon } from "lucide-react";

export function AskBox({ onAsk }: { onAsk?: (question: string) => void }) {
  const [value, setValue] = useState("");
  const question = value.trim();
  return (
    <form
      aria-label="Ask"
      className="flex min-h-ask w-full items-center gap-sp-2 rounded-pill border border-rule bg-card py-sp-1 pr-sp-1 pl-sp-5 shadow-ask transition-[border-color,box-shadow] duration-150 focus-within:border-ink"
      onSubmit={(event) => {
        event.preventDefault();
        if (!question || !onAsk) return;
        onAsk(question);
        setValue("");
      }}
    >
      {/* 16px or more, so iOS does not zoom the page when the field takes the focus. */}
      <input
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Ask about your team"
        aria-label="Ask a question"
        enterKeyHint="send"
        autoComplete="off"
        className="min-w-0 flex-1 bg-transparent text-lead leading-tight text-ink outline-none placeholder:text-mute focus-visible:outline-none"
      />
      <button
        type="submit"
        aria-label="Send"
        disabled={!question}
        className="press flex size-send flex-none items-center justify-center rounded-full bg-accent text-on-dark transition-colors duration-150 disabled:bg-raised disabled:text-mute"
      >
        <ArrowUpIcon aria-hidden className="size-sp-5" strokeWidth={2.25} />
      </button>
    </form>
  );
}
