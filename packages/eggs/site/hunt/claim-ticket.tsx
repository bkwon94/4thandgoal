/**
 * The claim ticket at the foot of the claim sheet: the letter tile, the egg word or the block, the team, and the stub.
 * A tap on the stub, or Enter or Space, tears it and sends the claim. A claim stamps CLAIMED, and a late claim stamps TAKEN.
 */
"use client";

import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { cn } from "@cpc/design/lib/utils";
import { ArtGround } from "./egg-art";

/* The time from a tap on the stub to the full tear, in ms: the holes of the perforation pop from the top down. */
export const TEAR_MS = 400;

/* The time the stamp holds on the ticket before the end card shows, in ms. */
export const STAMP_MS = 900;

/* The send of the claim: no claim yet, the API answers, the claim won, or another manager was first. */
export type Send = "idle" | "sending" | "claimed" | "taken";

const HOLES = 10;

type ClaimTicketProps = {
  letter: string;
  // The egg word, or null before the manager picks one. A block shows the block in place of a word.
  word: string | null;
  block: boolean;
  team: string | null;
  // The accessible name of the stub: the next missing step, or the claim itself.
  label: string;
  // True until the team, the egg word, and the passphrase are done. A locked stub names the next missing step.
  locked: boolean;
  send: Send;
  motion: boolean;
  onTear: () => void;
};

/* The stub pose at a progress of the tear from 0 to 1: it tilts on its foot and pulls to the right. */
function poseOf(progress: number): string | undefined {
  if (progress === 0) return undefined;
  return `rotate(${(progress * 16).toFixed(1)}deg) translate(${Math.round(progress * 20)}px, ${Math.round(progress * 6)}px)`;
}

export function ClaimTicket({ letter, word, block, team, label, locked, send, motion, onTear }: ClaimTicketProps) {
  // The progress of the tear, from 0 to 1. A tap runs it to 1 by itself. A drag can set it from the pointer too.
  const [progress, setProgress] = useState(0);
  const [auto, setAuto] = useState(false);
  // The count of tears. A stub that comes back after a tear springs onto the ticket.
  const [tears, setTears] = useState(0);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const gone = send === "sending" || send === "claimed";
  const live = !locked && send === "idle" && !auto;

  useEffect(() => () => {
    if (timer.current !== null) clearTimeout(timer.current);
  }, []);

  /* The full tear: the stub leaves the ticket and the claim sends. */
  function tear() {
    setAuto(false);
    setProgress(0);
    setTears((count) => count + 1);
    onTear();
  }

  /* A tap or a key tears the stub by itself. With motion off, the tear is at once. */
  function tearByItself() {
    if (!live) return;
    if (!motion) {
      tear();
      return;
    }
    setAuto(true);
    setProgress(1);
    timer.current = setTimeout(tear, TEAR_MS);
  }

  function onKeyDown(event: KeyboardEvent<HTMLButtonElement>) {
    if (event.key !== "Enter" && event.key !== " ") return;
    // The key tears the stub here, so the browser sends no click of its own.
    event.preventDefault();
    tearByItself();
  }

  return (
    <div role="group" aria-label="Claim ticket" className="relative flex h-36 w-full">
      <div className="relative flex min-w-0 flex-1 items-center gap-sp-3 overflow-hidden rounded-l-card border border-r-0 border-rule-dark bg-band px-sp-3 text-on-dark">
        {motion && send === "sending" && <span aria-hidden="true" className="egg-ticket-sweep absolute inset-0" />}
        <span className="relative flex-none">
          {/* The ground of the hero sits only behind the tile, so no line of text sits over the grid. */}
          <ArtGround inset="-inset-y-sp-6 -left-sp-3 right-0" />
          {/* The tile is taller than the glyph box of the letter, so axe can read its contrast. */}
          <span className="relative flex size-12 items-center justify-center rounded-letter bg-accent font-mono text-score font-bold text-on-dark shadow-orb">
            {letter}
          </span>
        </span>
        <span className="relative flex min-w-0 flex-col gap-sp-1">
          <span className="font-mono text-meta tracking-caps text-on-dark-muted uppercase">Claim ticket</span>
          <span className={cn("font-mono text-body font-bold tracking-wide", word === null && !block ? "text-on-dark-muted" : "text-on-dark")}>
            {block ? "BLOCK" : (word ?? "Egg word")}
          </span>
          <span className={cn("text-body", team === null ? "text-on-dark-muted" : "text-on-dark-2")}>{team ?? "Your team"}</span>
        </span>
        {(send === "claimed" || send === "taken") && (
          <span
            className={cn(
              "egg-ticket-stamp absolute top-1/2 right-sp-3 -mt-6 flex h-12 items-center rounded-letter border-3 bg-band px-sp-3 font-mono text-stat font-bold tracking-wide",
              send === "claimed" ? "border-accent-text text-accent-text" : "border-on-dark-2 text-on-dark-2",
              motion && "egg-ticket-stamp-in",
            )}
          >
            {send === "claimed" ? "CLAIMED" : "TAKEN"}
          </span>
        )}
        {/* The perforation at the right edge of the body. Each hole pops from the top down as the tear grows. */}
        <span aria-hidden="true" className="absolute inset-y-sp-2 -right-px z-10 flex w-0.5 flex-col items-center justify-between">
          {Array.from({ length: HOLES }, (_, index) => (
            <span
              key={index}
              data-popped={progress > (index + 0.5) / HOLES}
              style={auto ? { transitionDelay: `${index * 25}ms` } : undefined}
              className="egg-hole size-1 flex-none rounded-pill bg-on-dark-muted"
            />
          ))}
        </span>
        {/* The notches where the stub joins the body take the color of the sheet. */}
        <span aria-hidden="true" className="absolute -top-2 -right-2 z-20 size-4 rounded-pill bg-page" />
        <span aria-hidden="true" className="absolute -right-2 -bottom-2 z-20 size-4 rounded-pill bg-page" />
      </div>
      <button
        type="button"
        aria-label={label}
        aria-disabled={!live}
        aria-hidden={gone || undefined}
        tabIndex={gone ? -1 : undefined}
        onClick={tearByItself}
        onKeyDown={onKeyDown}
        style={{ transform: gone ? undefined : poseOf(progress) }}
        className={cn(
          "egg-stub relative flex h-full w-24 flex-none origin-bottom-left flex-col items-center justify-center gap-sp-2 rounded-r-card px-sp-2",
          locked ? "border border-l-0 border-rule-dark bg-chip-dark text-on-dark-muted" : "bg-accent text-on-dark",
          auto && "egg-stub-pull",
          gone ? (motion ? "egg-stub-flutter" : "invisible") : motion && tears > 0 && "egg-stub-heal",
          !locked && !gone && motion && "egg-stub-ready",
        )}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className="egg-stub-arrow">
          <path d="M5 12h14M13 6l6 6-6 6" />
        </svg>
        <span className="text-center font-mono text-meta leading-tight font-bold tracking-wide uppercase">
          {locked ? label : "Tear to claim"}
        </span>
      </button>
    </div>
  );
}
