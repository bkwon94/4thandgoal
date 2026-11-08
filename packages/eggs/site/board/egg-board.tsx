/**
 * The egg board: the hero with the counts and the grid of the 54 eggs, one card per egg word, the latest claims, and
 * how the hunt works. It renders the board answer of the API, which holds no page and no spot, so it gives no hint.
 */
"use client";

import { useState, type ReactNode } from "react";
import { Card } from "@cpc/design/parts/card";
import { HeroFrame } from "@cpc/design/parts/hero";
import { Rise } from "@cpc/design/parts/rise";
import { cn } from "@cpc/design/lib/utils";
import type { Board } from "../lib/api";
import { ArtGround } from "../hunt/egg-art";

type Word = Board["words"][number];
type Slot = Board["weeks"][number]["slots"][number];

/* The top of each egg word card. A tap on "Show all 11" shows every manager who hunts. */
const TOP = 5;
/* The feed shows the newest claims only, so a long hunt keeps a short page. */
const FEED = 10;

/* The red uppercase label of a card. It is 12px, so it holds the readability floor of 11px at every tier. */
const LABEL = "m-0 text-meta leading-tight font-bold tracking-wide uppercase";

const COUNT_WORDS = ["no", "one", "two", "three", "four", "five", "six"];

/* The count as a word for a small count, such as "Three", and as digits for a larger one. */
function countWord(count: number): string {
  const word = COUNT_WORDS[count] ?? String(count);
  return word.charAt(0).toUpperCase() + word.slice(1);
}

/* The slots of the egg word with the letters of one manager: each letter fills the first open slot of that letter. */
export function placeLetters(word: string, letters: string[]): string[] {
  const slots = Array<string>(word.length).fill("");
  for (const letter of letters) {
    const index = [...word].findIndex((char, at) => char === letter && slots[at] === "");
    if (index >= 0) slots[index] = letter;
  }
  return slots;
}

/* "a C" or "an S": the article follows the sound of the name of the letter. */
function withArticle(letter: string): string {
  return `${"AEFHILMNORSX".includes(letter) ? "an" : "a"} ${letter}`;
}

/* The age of a claim in the feed, such as 30M, 3H, or 2D. */
function age(claimedAt: string, now: Date): string {
  const minutes = Math.max(0, Math.floor((now.getTime() - new Date(claimedAt).getTime()) / 60_000));
  if (minutes < 1) return "NOW";
  if (minutes < 60) return `${minutes}M`;
  if (minutes < 24 * 60) return `${Math.floor(minutes / 60)}H`;
  return `${Math.floor(minutes / (24 * 60))}D`;
}

/* One egg of the grid of the hero. A found egg is white, an egg still out is black with the red zigzag and a glow,
   and an egg still to drop is dashed. */
function Egg({ slot }: { slot: Slot }) {
  return (
    <svg data-slot={slot} viewBox="0 0 16 20" aria-hidden="true" className={cn("h-sp-5 w-sp-4", slot === "out" && "drop-shadow-egg")}>
      <path
        d="M8 1c3.6 0 7 6.4 7 10.6A7 7 0 0 1 1 11.6C1 7.4 4.4 1 8 1z"
        strokeWidth={1.4}
        strokeDasharray={slot === "future" ? "2 2" : undefined}
        className={cn(
          slot === "found" && "fill-on-dark stroke-on-dark",
          slot === "out" && "fill-card-band stroke-accent-text",
          slot === "future" && "fill-none stroke-on-dark-muted",
        )}
      />
      {slot === "out" && (
        <path d="M3 11.5l2.5-1.7 2.5 1.7 2.5-1.7 2.5 1.7" fill="none" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" className="stroke-accent" />
      )}
    </svg>
  );
}

/* The name of a week column for a screen reader, such as "Week 9: 2 found, 4 out now". */
function weekName(week: Board["weeks"][number]): string {
  const count = (slot: Slot) => week.slots.filter((each) => each === slot).length;
  const parts = [
    [count("found"), "found"],
    [count("out"), "out now"],
    [count("future"), "to drop"],
  ].filter(([n]) => n !== 0);
  return `Week ${week.week}: ${parts.map(([n, what]) => `${n} ${what}`).join(", ")}`;
}

function BoardHero({ board }: { board: Board }) {
  const total = board.words.reduce((sum, word) => sum + word.prize, 0);
  const current = board.last_drop?.week;
  const counts: [string, number, string][] = [
    ["Left to find", board.counts.left, "text-accent-text"],
    ["Found", board.counts.found, "text-on-dark"],
    ["To drop", board.counts.to_drop, "text-on-dark-muted"],
  ];
  return (
    // The class egg-hero hides the full texture of the hero, and the oval of the texture sits behind the grid of the
    // eggs only, so each line of text sits on the flat band color with no plate (the ground of globals.css).
    <HeroFrame label="Egg hunt" className="egg-hero">
      <div className="flex flex-col gap-sp-5">
        <div className="flex flex-col items-start gap-sp-1">
          <span className={cn(LABEL, "text-accent-text")}>Egg hunt</span>
          <h1 className="m-0 text-headline leading-stat font-bold tracking-tight">The Egg Board</h1>
          <p className="m-0 text-lead text-on-dark-2">
            {`$${total} in gift cards. ${countWord(board.words.length)} egg words. First to fill a word wins it.`}
          </p>
        </div>
        <dl className="m-0 grid grid-cols-3 gap-sp-2">
          {counts.map(([label, value, color]) => (
            <div key={label} className="flex flex-col-reverse items-start gap-sp-1">
              <dt className={cn(LABEL, "text-on-dark-muted")}>{label}</dt>
              <dd className={cn("m-0 font-mono text-headline leading-none font-bold tracking-grade tabular-nums", color)}>{value}</dd>
            </div>
          ))}
        </dl>
        <div className="flex flex-col gap-sp-3">
          <div className="relative">
            {/* The ground stops above the week numbers, so its box never reaches a line of text. */}
            <ArtGround inset="top-0 bottom-8 -inset-x-hero-x" />
          <ul aria-label="The eggs of each week" className="relative m-0 grid list-none grid-cols-9 gap-sp-1 p-0">
            {board.weeks.map((week) => (
              <li
                key={week.week}
                aria-label={weekName(week)}
                className={cn(
                  "flex flex-col items-center gap-sp-1 rounded-tile py-sp-2",
                  week.week === current && "bg-accent/20",
                )}
              >
                {week.slots.map((slot, index) => (
                  <Egg key={index} slot={slot} />
                ))}
                <span
                  aria-hidden="true"
                  className={cn("font-mono text-meta font-bold", week.week === current ? "text-accent-text" : "text-on-dark-muted")}
                >
                  {String(week.week).padStart(2, "0")}
                </span>
              </li>
            ))}
          </ul>
          </div>
          <div aria-hidden="true" className="flex flex-wrap gap-x-sp-4 gap-y-sp-1 text-meta text-on-dark-2">
            <span className="inline-flex items-center gap-sp-1"><Egg slot="found" />Found</span>
            <span className="inline-flex items-center gap-sp-1"><Egg slot="out" />Out now</span>
            <span className="inline-flex items-center gap-sp-1"><Egg slot="future" />Drops on a later Tuesday</span>
          </div>
        </div>
      </div>
    </HeroFrame>
  );
}

/* A row of letter tiles: one grid column per letter, each at most the tile size, as the slot row of the hunt.
   On a narrow phone each column shrinks by the same amount, so the row never wraps and never leaves its card. Each tile
   fills its column, so every tile has one width. The gap keeps two dashed borders apart, so each slot reads as its own box. */
function TileRow({ length, small, className, children }: { length: number; small: boolean; className?: string; children: ReactNode }) {
  const size = small ? "var(--spacing-letter-sm)" : "var(--spacing-letter)";
  return (
    <div className={cn("grid max-w-full gap-sp-2", className)} style={{ gridTemplateColumns: `repeat(${length}, minmax(0, ${size}))` }}>
      {children}
    </div>
  );
}

/* The letter tile: a white square with its letter, or a dashed square for an open slot. A long word takes small tiles. */
function LetterTile({ letter, small, hint }: { letter: string; small: boolean; hint?: string }) {
  return (
    <span
      data-testid="tile"
      className={cn(
        "inline-flex w-full items-center justify-center rounded-letter font-mono text-meta font-bold",
        small ? "h-letter-sm" : "h-letter",
        letter !== "" ? "bg-ink text-page" : "border border-dashed border-rule text-mute",
      )}
    >
      {letter || hint || ""}
    </span>
  );
}

function GiftPill({ prize, won }: { prize: number; won: boolean }) {
  return (
    <span
      className={cn(
        "ml-auto rounded-pill border px-sp-3 py-sp-1 font-mono text-meta font-bold tracking-caps uppercase",
        won ? "border-rule-dark text-on-dark" : "border-rule text-ink-2",
      )}
    >
      {`$${prize} gift card`}
    </span>
  );
}

function WonCard({ word }: { word: Word & { winner: NonNullable<Word["winner"]> } }) {
  return (
    // The class egg-hero and the ground behind the tiles keep the text on the flat band color, as on the hero of the board.
    <HeroFrame label={word.word} className="egg-hero rounded-card">
      <div className="flex flex-col items-start gap-sp-4">
        <div className="flex w-full items-center gap-sp-2">
          <h2 className={cn(LABEL, "text-accent-text")}>{word.word}</h2>
          <GiftPill prize={word.prize} won />
        </div>
        <div className="relative self-stretch">
          <ArtGround inset="inset-y-0 -inset-x-hero-x" />
        <div className="relative flex flex-wrap gap-sp-1">
          {[...word.word].map((letter, index) => (
            <span
              key={index}
              className="inline-flex size-win-tile items-center justify-center rounded-letter bg-accent font-mono text-stat font-bold text-on-dark shadow-orb"
            >
              {letter}
            </span>
          ))}
        </div>
        </div>
        <div className="flex items-center gap-sp-3">
          <span className="text-score leading-tight font-bold">{`${word.winner.team} won it.`}</span>
          <span className="-rotate-6 rounded-letter border-2 border-on-dark bg-accent px-sp-2 py-sp-0 font-mono text-meta font-bold tracking-wide text-on-dark">
            WON
          </span>
        </div>
        <p className="m-0 text-lead text-on-dark-2">{`The $${word.prize} gift card is theirs. The race is over.`}</p>
      </div>
    </HeroFrame>
  );
}

function WordCard({ word }: { word: Word }) {
  const [all, setAll] = useState(false);
  const small = word.word.length > 8;
  // The managers with the most letters first. A tie keeps the order of the board, the order of the rosters.
  const ranked = [...word.managers].sort((a, b) => b.letters.length - a.letters.length);
  const leader = ranked[0];
  const open = leader === undefined || leader.letters.length === 0;
  const shown = all ? ranked : ranked.slice(0, TOP);
  const id = `egg-word-${word.word}`;
  return (
    <section aria-labelledby={id}>
    <Card className="flex flex-col gap-sp-2">
      <div className="flex items-center gap-sp-2">
        <h2 id={id} className={cn(LABEL, "text-accent-ink")}>{word.word}</h2>
        <GiftPill prize={word.prize} won={false} />
      </div>
      <span className="text-lead font-semibold">
        {open ? "No letters yet. The race is open." : `${leader.team} leads with ${leader.letters.length} of ${word.word.length}.`}
      </span>
      {open ? (
        <TileRow length={word.word.length} small={small} className="pt-sp-2 pb-sp-1">
          {[...word.word].map((letter, index) => (
            <LetterTile key={index} letter="" hint={letter} small={small} />
          ))}
        </TileRow>
      ) : (
        <>
          <ol className="m-0 flex list-none flex-col p-0">
            {shown.map((manager, index) => {
              const leads = index === 0;
              return (
                <li key={manager.roster_id} className="flex flex-col gap-sp-2 border-t border-rule py-sp-3">
                  <div className="flex items-center gap-sp-2">
                    <span className={cn("w-sp-6 font-mono text-row font-bold", leads ? "text-accent-ink" : "text-mute")}>
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <span className="min-w-0 truncate text-body font-semibold">{manager.team}</span>
                    {leads && (
                      <span className="rounded-pill bg-accent px-sp-2 py-sp-0 font-mono text-meta font-bold tracking-caps text-on-dark uppercase">
                        Leads
                      </span>
                    )}
                    <span className="ml-auto font-mono text-row font-bold tabular-nums">
                      {manager.letters.length}
                      <span className="text-mute">{`/${word.word.length}`}</span>
                    </span>
                  </div>
                  <TileRow length={word.word.length} small={small} className="pl-divider">
                    {placeLetters(word.word, manager.letters).map((letter, at) => (
                      <LetterTile key={at} letter={letter} small={small} />
                    ))}
                  </TileRow>
                </li>
              );
            })}
          </ol>
          <button
            type="button"
            aria-expanded={all}
            onClick={() => setAll(!all)}
            className="press mt-sp-1 min-h-touch cursor-pointer rounded-pill border border-rule bg-transparent text-body font-semibold text-ink"
          >
            {all ? `Show the top ${TOP}` : `Show all ${word.managers.length}`}
          </button>
        </>
      )}
    </Card>
    </section>
  );
}

function LatestClaims({ board, now }: { board: Board; now: Date }) {
  // The newest claim of the winner in its egg word is the claim that filled the word. The feed is newest first.
  const filled = new Set(
    board.words.flatMap((word) => {
      if (word.winner === null) return [];
      const index = board.latest.findIndex((claim) => claim.word === word.word && claim.roster_id === word.winner!.roster_id);
      return index < 0 ? [] : [index];
    }),
  );
  const left = board.counts.left;
  return (
    <section aria-labelledby="egg-latest">
    <Card className="flex flex-col">
      <h2 id="egg-latest" className={cn(LABEL, "mb-sp-3 text-accent-ink")}>Latest claims</h2>
      {board.latest.length === 0 ? (
        <span className="py-sp-2 text-body text-mute">
          {left > 0 ? `No claims yet. ${left} ${left === 1 ? "egg is" : "eggs are"} out there.` : "No claims yet."}
        </span>
      ) : (
        <ol className="m-0 flex list-none flex-col p-0">
          {board.latest.slice(0, FEED).map((claim, index) => {
            const fills = filled.has(index);
            return (
              <li key={`${claim.claimed_at}-${claim.roster_id}-${claim.letter}`} className="flex items-center gap-sp-3 border-t border-rule py-sp-2">
                <span
                  aria-hidden="true"
                  className={cn(
                    "inline-flex size-feed-tile flex-none items-center justify-center rounded-letter font-mono text-lead font-bold",
                    fills ? "bg-accent text-on-dark" : "bg-ink text-page",
                  )}
                >
                  {claim.letter}
                </span>
                <span data-claim className="flex-1 text-body leading-tight">
                  <b className="font-bold">{claim.team}</b>
                  {` claimed ${withArticle(claim.letter)} ${fills ? "and filled" : "for"} ${claim.word}.`}
                </span>
                <time dateTime={claim.claimed_at} className="font-mono text-meta font-bold text-mute">
                  {age(claim.claimed_at, now)}
                </time>
              </li>
            );
          })}
        </ol>
      )}
    </Card>
    </section>
  );
}

function HowItWorks({ board }: { board: Board }) {
  const first = board.weeks[0]?.week;
  const last = board.weeks[board.weeks.length - 1]?.week;
  const perDrop = board.weeks[0]?.slots.length ?? 0;
  const prizes = board.words.map((word) => `${word.word} $${word.prize}`);
  const prizeList = prizes.length > 1 ? `${prizes.slice(0, -1).join(", ")}, and ${prizes[prizes.length - 1]}` : prizes.join("");
  const rules = [
    `${perDrop} new eggs drop each Tuesday from week ${first} through week ${last}.`,
    "Eggs hide across the site. Tap or press the right spot to find one.",
    "The first manager to claim an egg gets its letter. Then the egg is gone.",
    "Put each letter in one of your egg words. A letter that fits none of them can block: the egg is gone, and the letter counts for no word.",
    "Each egg holds the letter that the most managers still need. A tie goes to the earlier letter. No letter repeats in one drop.",
    "No egg holds the last letter that a leader needs. If that rules out every letter, the egg holds the next letter by need.",
    `The first manager to fill an egg word wins its gift card: ${prizeList}.`,
    "The commissioner places every egg, so the commissioner cannot hunt.",
  ];
  return (
    <section aria-labelledby="egg-rules">
    <Card className="flex flex-col gap-sp-3">
      <h2 id="egg-rules" className={cn(LABEL, "text-accent-ink")}>How the hunt works</h2>
      <ol className="m-0 flex list-none flex-col gap-sp-3 p-0">
        {rules.map((rule, index) => (
          <li key={index} className="flex items-baseline gap-sp-3">
            <span className="font-mono text-meta font-bold text-accent-ink">{String(index + 1).padStart(2, "0")}</span>
            <span className="text-body text-ink-2">{rule}</span>
          </li>
        ))}
      </ol>
    </Card>
    </section>
  );
}

type EggBoardProps = {
  board: Board;
  // The time of the visit, for the age of each claim. The test passes a fixed time.
  now?: Date;
};

export function EggBoard({ board, now = new Date() }: EggBoardProps) {
  return (
    <div className="flex flex-col gap-sp-4">
      <Rise step={0}>
        <BoardHero board={board} />
      </Rise>
      {board.words.map((word, index) => (
        <Rise key={word.word} step={index + 1}>
          {word.winner !== null ? <WonCard word={{ ...word, winner: word.winner }} /> : <WordCard word={word} />}
        </Rise>
      ))}
      <LatestClaims board={board} now={now} />
      <HowItWorks board={board} />
    </div>
  );
}
