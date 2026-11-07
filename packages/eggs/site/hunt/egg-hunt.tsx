/**
 * The egg hunt of a page: the listener, the find card after a match, the claim sheet, and the end of each path.
 * The app mounts it once on every page of a client of the eggs package.
 */
"use client";

import { useEffect, useState } from "react";
import type { CheckAnswer, ClaimAnswer, EggsApi } from "../lib/api";
import { listenForEggs } from "../listener/listener";
import { ClaimSheet } from "./claim-sheet";
import { FindCard } from "./find-card";

type HuntState =
  | { step: "idle" }
  | { step: "found"; letter: string; token: string }
  | { step: "claimed-first" }
  | { step: "sheet"; letter: string; token: string }
  | { step: "done"; answer: ClaimAnswer };

/* The state that a check answer opens. No match keeps the page as it is. */
function afterCheck(answer: CheckAnswer): HuntState {
  if (!answer.match) return { step: "idle" };
  if (answer.claimed) return { step: "claimed-first" };
  return { step: "found", letter: answer.letter, token: answer.token };
}

export function EggHunt({ api }: { api: EggsApi }) {
  const [state, setState] = useState<HuntState>({ step: "idle" });

  useEffect(() => {
    return listenForEggs(document, {
      page: () => window.location.pathname,
      send: (check) => {
        // A failed check shows nothing, so a stranger learns nothing from an error.
        api.check(check).then((answer) => setState(afterCheck(answer)), () => undefined);
      },
    });
  }, [api]);

  const close = () => setState({ step: "idle" });
  if (state.step === "found") {
    return (
      <FindCard
        letter={state.letter}
        onClaim={() => setState({ step: "sheet", letter: state.letter, token: state.token })}
        onClose={close}
      />
    );
  }
  if (state.step === "claimed-first") {
    return <EndCard title="The egg is gone" line="Another manager claimed first." onClose={close} />;
  }
  if (state.step === "sheet") {
    return (
      <ClaimSheet
        api={api}
        letter={state.letter}
        token={state.token}
        onClaimed={(answer) => setState({ step: "done", answer })}
        onClaimedFirst={() => setState({ step: "claimed-first" })}
        onClose={close}
      />
    );
  }
  if (state.step === "done") {
    const { letter, word } = state.answer;
    return <EndCard title="Claimed" line={`${letter} is yours in ${word}.`} onClose={close} board />;
  }
  return null;
}

/* The plain card at the end of a path, with a link to the egg board after a claim. */
function EndCard({ title, line, onClose, board = false }: { title: string; line: string; onClose: () => void;
  board?: boolean }) {
  return (
    <div role="dialog" aria-modal="true" aria-labelledby="egg-end-title" className="fixed inset-0 z-50 grid place-items-center bg-page/80 p-gutter">
      <div className="flex w-full max-w-sm flex-col gap-sp-3 rounded-card bg-card p-gutter text-ink">
        <h2 id="egg-end-title" className="text-stat font-black uppercase">{title}</h2>
        <p className="text-lead">{line}</p>
        {board && <a href="/eggs/" className="min-h-touch font-bold underline">See the egg board</a>}
        <button type="button" onClick={onClose} className="min-h-touch rounded-card border border-rule font-bold">
          Close
        </button>
      </div>
    </div>
  );
}
