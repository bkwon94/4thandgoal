/**
 * The egg board: the hero with the counts and the grid of the 54 eggs, the slider of the egg words, the latest claims,
 * and how the hunt works. It renders the board answer of the API, which holds no page and no spot, so it gives no hint.
 */
"use client";

import { useRef, useState, type CSSProperties, type KeyboardEvent, type PointerEvent, type ReactNode } from "react";
import { Card } from "@cpc/design/parts/card";
import { Hero, HeroFrame } from "@cpc/design/parts/hero";
import { Rise } from "@cpc/design/parts/rise";
import { Tile } from "@cpc/design/parts/tile";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { springCurve } from "@cpc/design/lib/spring";
import { cn } from "@cpc/design/lib/utils";
import type { Board } from "../lib/api";
import { ArtGround } from "../hunt/egg-art";

type Word = Board["words"][number];
type Slot = Board["weeks"][number]["slots"][number];

/* The top of each egg word slide. A tap on "Show all 11" shows every manager who hunts. */
const TOP = 5;
/* The feed shows the newest claims only, so a long hunt keeps a short page. */
const FEED = 10;
/* Seconds for one move of the slider: the roll of the slides, the wash of the frame, and the swap of the giant word. */
const SLIDE_DURATION = 0.75;
/* The curve of the roll, a damped spring with a small overshoot (ADR 0028). It is the same for every move, so it samples once. */
const SLIDE_SPRING = springCurve({ bounce: 0.3 });
/* The pixels a finger travels to the side before a swipe moves the slide. A shorter drag is a tap or a wobble. */
const SWIPE_PX = 40;

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
    // eggs only, so each line of text sits on the flat band color (the ground of globals.css). The plate of each text
    // slot then has the band color on the band color, so it shows no box. The board gets no hero scene (ADR 0027): the
    // grid of the eggs is already a picture of the data.
    <Hero
      label="Egg hunt"
      className="egg-hero"
      eyebrow="Egg hunt"
      title="The Egg Board"
      meta={`$${total} in gift cards. ${countWord(board.words.length)} egg words. First to fill a word wins it.`}
      feature={
        <div className="flex flex-col gap-sp-3">
          <div className="relative">
            {/* The ground stops above the week numbers, so its box never reaches a line of text. */}
            <ArtGround inset="top-0 bottom-8 -inset-x-hero-x" />
            <ul aria-label="The eggs of each week" className="relative m-0 grid list-none grid-cols-9 gap-sp-1 p-0">
              {board.weeks.map((week) => (
                <li
                  key={week.week}
                  aria-label={weekName(week)}
                  aria-current={week.week === current ? "date" : undefined}
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
      }
      stats={
        <div role="group" aria-label="Egg counts" className="grid w-full grid-cols-3 gap-sp-2 tablet:w-auto">
          {counts.map(([label, value, color]) => (
            <Tile key={label} tone="hero" label={label} value={<span className={color}>{value}</span>} />
          ))}
        </div>
      }
    />
  );
}

/* A row of letter tiles: one grid column per letter, each at most the tile size, as the slot row of the hunt.
   On a narrow phone each column shrinks by the same amount, so the row never wraps and never leaves its slide. Each tile
   fills its column, so every tile has one width. The gap keeps two dashed borders apart, so each slot reads as its own box. */
function TileRow({ length, small, className, children }: { length: number; small: boolean; className?: string; children: ReactNode }) {
  const size = small ? "var(--spacing-letter-sm)" : "var(--spacing-letter)";
  return (
    <div className={cn("grid max-w-full gap-sp-2", className)} style={{ gridTemplateColumns: `repeat(${length}, minmax(0, ${size}))` }}>
      {children}
    </div>
  );
}

/* The letter tile of a row on the dark ground: a white square with its letter, or a dashed square for an open slot.
   A long word takes small tiles. */
function LetterTile({ letter, small }: { letter: string; small: boolean }) {
  return (
    <span
      data-testid="tile"
      className={cn(
        "inline-flex w-full items-center justify-center rounded-letter font-mono text-meta font-bold",
        small ? "h-letter-sm" : "h-letter",
        letter !== "" ? "bg-on-dark text-band" : "border border-dashed border-rule-dark",
      )}
    >
      {letter}
    </span>
  );
}

function GiftPill({ prize }: { prize: number }) {
  return (
    <span className="rounded-pill border border-on-dark px-sp-3 py-sp-1 font-mono text-meta font-bold tracking-caps text-on-dark uppercase">
      {`$${prize} gift card`}
    </span>
  );
}

/* The race of one egg word: the managers with the most letters first, and the managers who share the top count.
   A tie keeps the order of the board, the order of the rosters. */
type Race = { word: Word; ranked: Word["managers"]; leaders: Word["managers"]; top: number };

function raceOf(word: Word): Race {
  const ranked = [...word.managers].sort((a, b) => b.letters.length - a.letters.length);
  const top = ranked[0]?.letters.length ?? 0;
  const leaders = top === 0 ? [] : ranked.filter((manager) => manager.letters.length === top);
  return { word, ranked, leaders, top };
}

/* The slides closest race first: the open word whose leader holds the largest share of its letters. A won word goes
   last. The sort is stable, so a tie in the share keeps the fixed order of the board. */
function slideOrder(races: Race[]): Race[] {
  const rank = (race: Race) => (race.word.winner !== null ? -1 : race.top / race.word.word.length);
  return [...races].sort((a, b) => rank(b) - rank(a));
}

/* "A", "A and B", or "A, B, and C". */
function joinTeams(teams: string[]): string {
  if (teams.length < 3) return teams.join(" and ");
  return `${teams.slice(0, -1).join(", ")}, and ${teams[teams.length - 1]}`;
}

function leaderLine({ word, leaders, top }: Race): string {
  const length = word.word.length;
  if (leaders.length === 0) return "No letters yet. The race is open.";
  if (leaders.length === 1) return `${leaders[0].team} leads with ${top} of ${length}.`;
  return `${joinTeams(leaders.map((manager) => manager.team))} tie with ${top} of ${length}.`;
}

/* The text of a tab, such as "CORNERSTONE 4/11" or "EAGLES · Won". */
function tabCount({ word, top }: Race): string {
  return word.winner !== null ? "· Won" : `${top}/${word.word.length}`;
}

/* The roll of the giant word in a move. The shown word rests "in". The word that leaves rolls out up on a move to the
   next slide and down on a move back, and every other word waits on the side that the next word comes from. */
type Roll = "in" | "out-up" | "out-down" | "wait-up" | "wait-down";

/* The giant egg word of a slide. A letter the leader holds is lit in white, a letter the leader still needs is a dim
   outline, and a won word lights every letter in red. The heading reads the word, and the tiles stay out of the
   accessibility tree. Each column shrinks on a narrow phone, so CORNERSTONE fits at 390px. */
function GiantWord({ race, roll }: { race: Race; roll: Roll }) {
  const { word, ranked } = race;
  const held = placeLetters(word.word, race.top === 0 ? [] : ranked[0].letters);
  const won = word.winner !== null;
  return (
    <h2
      aria-label={word.word}
      data-roll={roll}
      className="egg-word m-0 grid max-w-full gap-sp-1"
      style={{ gridTemplateColumns: `repeat(${word.word.length}, minmax(0, var(--spacing-giant-tile)))` }}
    >
      {[...word.word].map((letter, index) => {
        const state = won ? "won" : held[index] !== "" ? "lit" : "outline";
        return (
          <span
            key={index}
            aria-hidden="true"
            data-letter={state}
            style={{ "--k": index } as CSSProperties}
            className={cn(
              "egg-letter inline-flex aspect-square w-full items-center justify-center rounded-letter font-mono text-stat font-bold tablet:text-score",
              state === "won" && "border-2 border-on-dark bg-accent text-on-dark shadow-orb",
              state === "lit" && "bg-on-dark text-band",
              state === "outline" && "border border-on-dark-muted text-on-dark-muted",
            )}
          >
            {letter}
          </span>
        );
      })}
    </h2>
  );
}

function OpenSlide({ race }: { race: Race }) {
  const [all, setAll] = useState(false);
  const { word, ranked, leaders } = race;
  const small = word.word.length > 8;
  const shown = all ? ranked : ranked.slice(0, TOP);
  return (
    <>
      <span className="text-lead font-semibold">{leaderLine(race)}</span>
      {leaders.length > 0 && (
        <>
          <ol className="m-0 flex list-none flex-col p-0">
            {shown.map((manager, index) => {
              const leads = leaders.includes(manager);
              return (
                <li key={manager.roster_id} className="flex flex-col gap-sp-2 border-t border-rule-dark py-sp-3">
                  <div className="flex items-center gap-sp-2">
                    <span className={cn("w-sp-6 font-mono text-row font-bold", leads ? "text-accent-text" : "text-on-dark-muted")}>
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <span data-team className="min-w-0 truncate text-body font-semibold">{manager.team}</span>
                    {leads && (
                      <span className="rounded-pill bg-accent px-sp-2 py-sp-0 font-mono text-meta font-bold tracking-caps text-on-dark uppercase">
                        Leads
                      </span>
                    )}
                    <span className="ml-auto font-mono text-row font-bold tabular-nums">
                      {manager.letters.length}
                      <span className="text-on-dark-muted">{`/${word.word.length}`}</span>
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
            className="press mt-sp-1 min-h-touch cursor-pointer rounded-pill border border-rule-dark bg-transparent text-body font-semibold text-on-dark"
          >
            {all ? `Show the top ${TOP}` : `Show all ${word.managers.length}`}
          </button>
        </>
      )}
    </>
  );
}

function WonSlide({ word, winner }: { word: Word; winner: NonNullable<Word["winner"]> }) {
  return (
    <>
      <div className="flex items-center gap-sp-3">
        <span className="text-score leading-tight font-bold">{`${winner.team} won it.`}</span>
        <span className="-rotate-6 rounded-letter border-2 border-on-dark bg-on-dark px-sp-2 py-sp-0 font-mono text-meta font-bold tracking-wide text-accent">
          WON
        </span>
      </div>
      <p className="m-0 text-lead text-on-dark">{`The $${word.prize} gift card is theirs. The race is over.`}</p>
    </>
  );
}

/* The offset of a slide from the slide at an index, wrapped to the nearest side, so a slide sits to the left (-1), in
   place (0), or to the right (1) of it. A move always rolls the slides the short way round. */
function offset(slide: number, at: number, count: number): number {
  const half = Math.floor(count / 2);
  return ((((slide - at + half) % count) + count) % count) - half;
}

/* The egg word slider: a tab row of the egg words in the fixed order of the board, over one slide per word. The slides
   run closest race first, and the slider opens on the first. One selected index into the slide order is the whole
   state, so a swipe or a motion between slides can move the same index. The tabs follow the WAI-ARIA tabs pattern:
   the arrow keys, Home, and End move the focus and the selection, and only the selected tab sits in the tab order.
   An open slide sits on the dark hero ground, and only a won slide washes the frame into the red accent. */
function EggWordSlider({ words }: { words: Word[] }) {
  const races = words.map(raceOf);
  const slides = slideOrder(races);
  // The selected slide, and the slide shown before the last move. The two give the way each slide and each word rolls.
  const [{ selected, from }, setMove] = useState({ selected: 0, from: 0 });
  const off = useMotionOff();
  const tabs = useRef<(HTMLButtonElement | null)[]>([]);
  const shown = slides[selected] ?? slides[0];
  const wonShown = shown !== undefined && shown.word.winner !== null;

  function select(tabIndex: number) {
    const count = races.length;
    const next = (tabIndex + count) % count;
    go(slides.indexOf(races[next]));
    tabs.current[next]?.focus();
  }

  /* A swipe moves to the next or the last slide in the slide order, and wraps at each end, as the arrow keys do. */
  function step(by: number) {
    go((selected + by + slides.length) % slides.length);
  }

  function go(next: number) {
    setMove((move) => (move.selected === next ? move : { selected: next, from: move.selected }));
  }

  // The way of the last move: 1 to the next slide, -1 back. Before any move, the words wait as for a move to the next.
  const way = selected === from ? 1 : Math.sign(offset(selected, from, slides.length));

  function rollOf(index: number): Roll {
    if (index === selected) return "in";
    if (index === from) return way > 0 ? "out-up" : "out-down";
    return way > 0 ? "wait-down" : "wait-up";
  }

  // With motion off, every duration and every delay is 0, so each move is an instant change (ADR 0028).
  const motion = { "--es-dur": off ? "0s" : `${SLIDE_DURATION}s`, "--es-on": off ? "0" : "1", "--es-spring": SLIDE_SPRING } as CSSProperties;

  // The start of a touch on the slider. A vertical swipe stays a page scroll: the slider allows only pan-y, so the
  // browser scrolls the page and cancels the pointer, and a drag that moves more up than to the side moves no slide.
  const swipeStart = useRef<{ x: number; y: number } | null>(null);

  function onPointerDown(event: PointerEvent<HTMLDivElement>) {
    if (!event.isPrimary) return;
    swipeStart.current = { x: event.clientX, y: event.clientY };
  }

  function onPointerUp(event: PointerEvent<HTMLDivElement>) {
    const start = swipeStart.current;
    swipeStart.current = null;
    if (start === null) return;
    const dx = event.clientX - start.x;
    const dy = event.clientY - start.y;
    if (Math.abs(dx) < SWIPE_PX || Math.abs(dx) <= Math.abs(dy)) return;
    // A swipe to the left brings the next slide in from the right.
    step(dx < 0 ? 1 : -1);
  }

  function onKeyDown(event: KeyboardEvent<HTMLButtonElement>, tabIndex: number) {
    const moves: Record<string, number> = { ArrowRight: tabIndex + 1, ArrowLeft: tabIndex - 1, Home: 0, End: races.length - 1 };
    if (!(event.key in moves)) return;
    event.preventDefault();
    select(moves[event.key]);
  }

  return (
    <div data-slider style={motion} className="egg-slider flex flex-col gap-sp-3">
      <div role="tablist" aria-label="Egg words" className="grid grid-cols-3 gap-sp-2">
        {races.map((race, tabIndex) => {
          const on = race === shown;
          return (
            <button
              key={race.word.word}
              ref={(element) => {
                tabs.current[tabIndex] = element;
              }}
              type="button"
              role="tab"
              id={`egg-tab-${race.word.word}`}
              aria-selected={on}
              aria-controls={`egg-slide-${race.word.word}`}
              tabIndex={on ? 0 : -1}
              onClick={() => select(tabIndex)}
              onKeyDown={(event) => onKeyDown(event, tabIndex)}
              className={cn(
                "press flex min-h-touch min-w-0 cursor-pointer flex-col items-center justify-center rounded-tile border px-sp-2 py-sp-1 font-mono text-meta font-bold tracking-wide",
                on ? "border-rule-dark bg-band text-on-dark" : "border-rule bg-transparent text-ink",
              )}
            >
              <span>{race.word.word}</span>{" "}
              <span className={cn("tabular-nums", on ? "text-on-dark-2" : "text-mute")}>{tabCount(race)}</span>
            </button>
          );
        })}
      </div>
      <div
        data-swipe
        onPointerDown={onPointerDown}
        onPointerUp={onPointerUp}
        onPointerCancel={() => {
          swipeStart.current = null;
        }}
        className="touch-pan-y"
      >
        {/* The class egg-hero hides the texture of the frame, so each line of text sits on the flat band color or the
            flat accent, and axe can read its contrast. */}
        <HeroFrame label="Egg word" className={cn("egg-hero egg-wash", wonShown && "border-accent bg-accent")}>
          {slides.map((race, index) => {
            const rel = offset(index, selected, slides.length);
            // A slide that wraps from one side to the other passes behind the frame, so it jumps with no roll.
            const jump = Math.abs(rel - offset(index, from, slides.length)) > 1;
            const on = race === shown;
            // The shown slide holds the height of the frame. The neighbors sit on top of it, to the side, blurred and faded,
            // and only the roll of a move shows them.
            return (
              <div
                key={race.word.word}
                role="tabpanel"
                id={`egg-slide-${race.word.word}`}
                aria-labelledby={`egg-tab-${race.word.word}`}
                aria-hidden={on ? undefined : true}
                inert={!on}
                data-rel={Math.max(-1, Math.min(1, rel))}
                data-jump={jump}
                className={cn("egg-slide flex flex-col items-start gap-sp-4", on ? "relative" : "absolute inset-x-0 top-0")}
              >
                <GiantWord race={race} roll={rollOf(index)} />
                <GiftPill prize={race.word.prize} />
                {race.word.winner !== null ? <WonSlide word={race.word} winner={race.word.winner} /> : <OpenSlide race={race} />}
              </div>
            );
          })}
        </HeroFrame>
      </div>
    </div>
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
      <Rise step={1}>
        <EggWordSlider words={board.words} />
      </Rise>
      <LatestClaims board={board} now={now} />
      <HowItWorks board={board} />
    </div>
  );
}
