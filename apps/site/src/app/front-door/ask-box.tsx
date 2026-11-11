/**
 * The ask box of the front door: one field and a send button. The send button wakes in the accent once the field holds
 * a question, and its halo grows as the field fills, so the control says it is ready before the thumb reaches it. While
 * a question routes, the button holds busy with the braille spinner of the steps.
 */
"use client";

import { type CSSProperties, useState } from "react";
import { ArrowUpIcon } from "lucide-react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { useKeyboardField } from "@cpc/design/shell/keyboard";
import { haloOf } from "./motion";
import { Spinner } from "./steps";

/* `pending` is true while a question routes. The field still takes keys, and Send waits until the route answers. */
export function AskBox({ onAsk, pending = false }: { onAsk?: (question: string) => void; pending?: boolean }) {
  const off = useMotionOff();
  const [value, setValue] = useState("");
  const question = value.trim();
  // The field opens the keyboard on a phone, so the dock of the shell tucks away while it has the focus.
  const keyboard = useKeyboardField();
  return (
    <form
      aria-label="Ask"
      className="door-glass door-lift flex min-h-ask w-full items-center gap-sp-2 rounded-pill border border-door-hair py-sp-1 pr-sp-1 pl-sp-5 transition-[border-color] duration-150 focus-within:border-door-focus"
      onSubmit={(event) => {
        event.preventDefault();
        if (!question || !onAsk || pending) return;
        onAsk(question);
        setValue("");
      }}
    >
      {/* 16px or more, so iOS does not zoom the page when the field takes the focus. */}
      <input
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onFocus={keyboard.onFocus}
        onBlur={keyboard.onBlur}
        placeholder="Ask about your team"
        aria-label="Ask a question"
        enterKeyHint="send"
        autoComplete="off"
        className="min-w-0 flex-1 bg-transparent text-lead leading-tight text-ink outline-none placeholder:text-mute focus-visible:outline-none"
      />
      <button
        type="submit"
        aria-label="Send"
        aria-busy={pending || undefined}
        disabled={!question || pending}
        style={{ "--halo": haloOf(value) } as CSSProperties}
        className="send-halo flex size-send flex-none items-center justify-center rounded-full bg-accent text-on-dark disabled:bg-raised disabled:text-mute"
      >
        {pending ? (
          // Under reduced motion the busy button holds a static dot, as the live step does.
          off ? <span aria-hidden className="size-1.5 rounded-full bg-current" /> : <Spinner className="font-mono text-lead leading-none" />
        ) : (
          <ArrowUpIcon aria-hidden className="size-sp-5" strokeWidth={2.25} />
        )}
      </button>
    </form>
  );
}
