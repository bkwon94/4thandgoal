/**
 * The egg button: a 44px icon link beside the theme button in the top band of every page, which opens the egg board.
 * Its red badge is the count of eggs left to find. The egg board is no menu item, so the dock keeps its five items.
 */
"use client";

import type { EggsApi } from "../lib/api";
import { useBoard } from "./use-board";

type EggButtonProps = {
  // The count of eggs left to find, or null before the board loads. With null the button shows no badge.
  left: number | null;
  // The href of the egg board. The app layer builds it.
  href: string;
};

/* The name says the count, so a screen reader user hears the badge too. */
function nameOf(left: number | null): string {
  if (left === null) return "Egg board";
  return `Egg board, ${left} ${left === 1 ? "egg" : "eggs"} left to find`;
}

export function EggButton({ left, href }: EggButtonProps) {
  return (
    <a
      href={href}
      aria-label={nameOf(left)}
      className="press relative flex size-touch flex-none items-center justify-center text-ink no-underline hover-fine:text-accent-ink"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true" className="size-sp-5" fill="none" stroke="currentColor" strokeWidth={2} strokeLinejoin="round">
        <path d="M12 2.5c4 0 7 7.5 7 11.5a7 7 0 0 1-14 0c0-4 3-11.5 7-11.5z" />
        <path d="M7.2 13.2l2.2-1.5 2.6 1.8 2.6-1.8 2.2 1.5" strokeLinecap="round" />
      </svg>
      {left !== null && (
        <span className="absolute top-sp-0 right-0 flex h-sp-5 min-w-sp-5 items-center justify-center rounded-pill border-2 border-page bg-accent px-sp-1 font-mono text-meta leading-none font-bold text-on-dark tabular-nums">
          {left}
        </span>
      )}
    </a>
  );
}

/* The egg button of the top band: it reads the count left from the API at each visit. */
export function EggButtonScreen({ api, href }: { api: EggsApi; href: string }) {
  const board = useBoard(api);
  return <EggButton left={board === null ? null : board.counts.left} href={href} />;
}
