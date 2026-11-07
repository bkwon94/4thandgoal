/**
 * The egg banner: a strip under the top band of the home page after each egg drop, with a link to the egg board.
 * It names the day of the drop, so it is true on any day, and a hide stays in this browser until the next drop.
 */
"use client";

import { useState } from "react";
import { Rise } from "@cpc/design/parts/rise";
import type { Board, EggsApi } from "../lib/api";
import { dropKey, hideBanner, isBannerHidden } from "../lib/banner-store";
import { useBoard } from "./use-board";

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

/* The offset of an ISO time, such as -04:00, in minutes. The API clock runs in the timezone of the client, so the time
   of the drop carries the offset of the client. Near a change of the clock, the offset of today can differ by one hour
   from the offset of the drop, so a time within an hour of midnight can read the day before or after. */
function offsetMinutes(iso: string): number {
  const match = /([+-])(\d\d):(\d\d)$/.exec(iso);
  if (match === null) return 0;
  const minutes = Number(match[2]) * 60 + Number(match[3]);
  return match[1] === "-" ? -minutes : minutes;
}

/* The calendar day of a time, in the timezone of the drop. */
function dayAt(time: Date, offset: number): Date {
  return new Date(time.getTime() + offset * 60_000);
}

/* The line of the banner: "6 eggs dropped today · 6 left" on the day of the drop, then "6 eggs dropped Tue · 5 left".
   The count left is the count of the whole hunt. */
export function dropLine(drop: NonNullable<Board["last_drop"]>, left: number, now: Date) {
  const offset = offsetMinutes(drop.dropped_at);
  const dropped = dayAt(new Date(drop.dropped_at), offset);
  const today = dayAt(now, offset);
  const sameDay = dropped.toISOString().slice(0, 10) === today.toISOString().slice(0, 10);
  return {
    count: drop.count,
    what: `${drop.count === 1 ? "egg" : "eggs"} dropped ${sameDay ? "today" : WEEKDAYS[dropped.getUTCDay()]}`,
    left,
  };
}

/* The small egg of the banner: the black shell with the red zigzag of the CPC egg. */
function EggMark() {
  return (
    <svg viewBox="0 0 22 28" aria-hidden="true" className="relative h-sp-5 w-sp-4 flex-none">
      <path d="M11 1.5c5 0 9.5 9 9.5 15a9.5 9.5 0 0 1-19 0c0-6 4.5-15 9.5-15z" className="fill-card-band stroke-accent-text" strokeWidth={1.8} />
      <path d="M4 16l3.5-2.4 3.5 2.4 3.5-2.4 3.5 2.4" fill="none" className="stroke-accent" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

type EggBannerProps = {
  board: Board;
  // The href of the egg board. The app layer builds it.
  href: string;
  // The time of the visit. The test passes a fixed time.
  now?: Date;
};

export function EggBanner({ board, href, now = new Date() }: EggBannerProps) {
  const drop = board.last_drop;
  const key = drop === null ? null : dropKey(drop);
  const [hidden, setHidden] = useState(() => key !== null && isBannerHidden(key));
  if (drop === null || key === null || hidden) return null;
  const line = dropLine(drop, board.counts.left, now);
  const hide = () => {
    hideBanner(key);
    setHidden(true);
  };
  return (
    <Rise>
      <section
        aria-label="Egg drop"
        className="hero-texture relative flex h-banner items-center gap-sp-2 overflow-hidden border-b border-rule-dark bg-band pl-gutter text-on-dark"
      >
        <div aria-hidden="true" className="hero-scan" />
        <EggMark />
        {/* The line sits on a plate, so the grid and the glow never sit under a letter. */}
        <span data-banner-line className="plate relative min-w-0 flex-1 truncate text-body">
          <b className="font-mono font-bold text-accent-text">{line.count}</b> <b className="font-bold">{line.what}</b>
          <span className="text-on-dark-muted"> · </span>
          <b className="font-mono font-bold">{line.left}</b> left
        </span>
        <a
          href={href}
          className="press plate relative flex min-h-touch flex-none items-center gap-sp-1 text-body font-bold text-on-dark no-underline"
        >
          Egg board
          <svg viewBox="0 0 24 24" aria-hidden="true" className="size-sp-4" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 12h14M13 6l6 6-6 6" />
          </svg>
        </a>
        <button
          type="button"
          aria-label="Hide the banner"
          onClick={hide}
          className="press relative flex size-touch flex-none cursor-pointer items-center justify-center border-0 bg-transparent text-on-dark-muted"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true" className="size-sp-4" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>
      </section>
    </Rise>
  );
}

/* The banner of the home page: it reads the board from the API at each visit, and shows nothing until the board loads
   or when the call fails, so a failed call never pushes the page. */
export function EggBannerScreen({ api, href }: { api: EggsApi; href: string }) {
  const board = useBoard(api);
  return board === null ? null : <EggBanner board={board} href={href} />;
}
