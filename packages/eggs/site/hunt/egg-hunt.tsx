/**
 * The egg hunt of a page: the listener, the find card after a match, the claim sheet, and the hero card at the end of each path.
 * The app mounts it once on every page of a client of the eggs package.
 */
"use client";

import { useEffect, useState } from "react";
import { EggsError, type CheckAnswer, type EggCheck, type EggsApi } from "../lib/api";
import { listenForEggs } from "../listener/listener";
import { ClaimSheet } from "./claim-sheet";
import { EndCard, minutesOf, type End } from "./end-card";
import { FindCard, type Origin } from "./find-card";

type HuntState =
  | { step: "idle" }
  | { step: "found"; letter: string; token: string; origin: Origin | null }
  | { step: "sheet"; letter: string; token: string }
  | { step: "end"; end: End };

/* The middle of the element of the check on the screen, so the ring of the find ripples out from it. */
function originOf(check: EggCheck): Origin | null {
  // A match on the attribute needs no escape of the id in a selector.
  const element = [...document.querySelectorAll("[data-stable-id]")].find(
    (each) => each.getAttribute("data-stable-id") === check.target,
  );
  if (element === undefined) return null;
  const box = element.getBoundingClientRect();
  return { x: box.left + box.width / 2, y: box.top + box.height / 2 };
}

/* The state that a check answer opens. No match keeps the page as it is. */
function afterCheck(answer: CheckAnswer, origin: Origin | null): HuntState {
  if (!answer.match) return { step: "idle" };
  if (answer.claimed) return { step: "end", end: { kind: "claimed-first", letter: answer.letter } };
  return { step: "found", letter: answer.letter, token: answer.token, origin };
}

export function EggHunt({ api }: { api: EggsApi }) {
  const [state, setState] = useState<HuntState>({ step: "idle" });

  useEffect(() => {
    return listenForEggs(document, {
      page: () => window.location.pathname,
      send: (check) => {
        const origin = originOf(check);
        api.check(check).then(
          (answer) => setState(afterCheck(answer, origin)),
          (failure) => {
            // The limit of the check has its own card. Any other failure shows nothing, so a stranger learns nothing from an error.
            if (failure instanceof EggsError && failure.status === 429) {
              setState({ step: "end", end: { kind: "limit", minutes: minutesOf(failure.retryAfter) } });
            }
          },
        );
      },
    });
  }, [api]);

  const close = () => setState({ step: "idle" });
  if (state.step === "found") {
    return (
      <FindCard
        letter={state.letter}
        origin={state.origin}
        onClaim={() => setState({ step: "sheet", letter: state.letter, token: state.token })}
        onClose={close}
      />
    );
  }
  if (state.step === "sheet") {
    const { letter } = state;
    return (
      <ClaimSheet
        api={api}
        letter={letter}
        token={state.token}
        onClaimed={(answer, prize, team) => setState({ step: "end", end: { kind: "claimed", answer, prize, team } })}
        onClaimedFirst={() => setState({ step: "end", end: { kind: "claimed-first", letter } })}
        onClose={close}
      />
    );
  }
  if (state.step === "end") return <EndCard end={state.end} onClose={close} />;
  return null;
}
