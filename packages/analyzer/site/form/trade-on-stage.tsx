/**
 * The trade on the stage: one slim row per side, asker first, with the team avatar, the full team name, "gets", and the players that side gets.
 * Idle shows a count, the wait and the result show up to 3 headshot tokens and a "+N" token, and each row anchors the mesh under its side.
 */
"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { Avatar } from "@cpc/league/avatar";
import { AVATAR_FALLBACK } from "@cpc/league/images";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { EASE_OUT } from "@cpc/design/lib/motion";

/* One side on the stage: its team, the avatar of that team, and each player it gets with his headshot. */
export type StageSide = {
  id: number;
  team: string;
  avatar: string | null;
  players: { id: string; name: string; headshot: string }[];
};

/* A row shows up to this many headshots, then one "+N" token for the rest, so a big trade still fits the hero. */
const SHOWN = 3;

/* The token classes. The ring in the band color parts two overlapped faces, as a cut and not as a line.
   The mesh cuts a hole under each token, so no line of the mesh runs across a face. */
const TOKEN = "relative grid size-stage-token flex-none place-items-center overflow-hidden rounded-full ring-2 ring-band";
const OVERLAP = "-ml-sp-2";

/* The first letter of the first and the last name. A suffix such as III or Jr. is not a name, so Kenneth Walker III reads KW. */
export function initials(name: string): string {
  const parts = name
    .replace(/\s+(Jr|Sr|II|III|IV|V)\.?$/i, "")
    .trim()
    .split(/\s+/);
  const first = parts[0]?.[0] ?? "";
  const last = parts.length > 1 ? (parts.at(-1)?.[0] ?? "") : "";
  return (first + last).toUpperCase();
}

/* The motion of one token as the headshots go up to the stage on the tap of Grade: a short rise that sharpens out of a
   blur, as the texts reveal of transitions.dev, with a stagger by row and then by token, so the trade fills top to bottom.
   The last token of a trade of 4 sides lands in under 1 s. With motion off, a token only fades in, and nothing moves. */
function riseOf(off: boolean, row: number, index: number) {
  if (off) return { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: { duration: 0.2 } };
  return {
    initial: { opacity: 0, transform: "translateY(10px) scale(0.92)", filter: "blur(3px)" },
    animate: { opacity: 1, transform: "translateY(0px) scale(1)", filter: "blur(0px)" },
    transition: { duration: 0.4, ease: EASE_OUT, delay: 0.12 + row * 0.07 + index * 0.04 },
  };
}

/* One headshot token. A headshot that fails to load, or a player with none, shows the initials of the player, because the
   default face would make two players look the same. The title names the player for a pointer that rests on it. */
function Token({ name, src, index, row, rise }: { name: string; src: string; index: number; row: number; rise: boolean }) {
  const off = useMotionOff();
  const [failed, setFailed] = useState(src === "");
  return (
    <motion.span
      data-mesh-hole
      title={name}
      // The first token sits on top, so the faces read left to right in the order of the trade.
      style={{ zIndex: SHOWN + 1 - index }}
      className={`${TOKEN} bg-chip-dark ${index > 0 ? OVERLAP : ""}`}
      {...(rise ? riseOf(off, row, index) : {})}
    >
      {failed ? (
        <span className="font-mono text-label font-bold tracking-wide text-on-dark-2">{initials(name)}</span>
      ) : (
        <img src={src} alt="" onError={() => setFailed(true)} className="size-full max-w-none object-cover object-top" />
      )}
    </motion.span>
  );
}

/* The "+2" token of the players past the cap. It rises last in its row, after the faces. */
function More({ count, row, rise }: { count: number; row: number; rise: boolean }) {
  const off = useMotionOff();
  return (
    <motion.span
      data-mesh-hole
      className={`${TOKEN} ${OVERLAP} bg-band font-mono text-meta font-bold text-on-dark tabular-nums outline-1 -outline-offset-1 outline-rule-dark`}
      {...(rise ? riseOf(off, row, SHOWN) : {})}
    >
      +{count}
    </motion.span>
  );
}

/* A side with no player yet holds the place of a token, so the row keeps its shape and the reader sees the side waits. */
function EmptyToken() {
  return <span data-stage-empty className="size-stage-token flex-none rounded-full border border-dashed border-rule-dark" />;
}

/* The tokens of one side: up to 3 faces, overlapped, then "+N". */
function Tokens({ side, row, rise }: { side: StageSide; row: number; rise: boolean }) {
  if (side.players.length === 0) return <EmptyToken />;
  const rest = side.players.length - SHOWN;
  return (
    <span className="flex items-center">
      {side.players.slice(0, SHOWN).map((player, index) => (
        <Token key={player.id} name={player.name} src={player.headshot} index={index} row={row} rise={rise} />
      ))}
      {rest > 0 && <More count={rest} row={row} rise={rise} />}
    </span>
  );
}

/* The idle row says only how many players the side gets, because the cards of the Stack below already show each player. */
function Count({ side }: { side: StageSide }) {
  const count = side.players.length;
  if (count === 0) return <EmptyToken />;
  return (
    <span className="font-mono text-label font-bold tracking-wide text-on-dark-2 uppercase tabular-nums">
      {count} {count === 1 ? "player" : "players"}
    </span>
  );
}

/* `show` is "count" in idle and "tokens" in the wait and under a result. `rise` plays the rise of the tokens once, as the
   stage mounts, for the hand-off from idle to the wait. A result mounts its stage at rest, because the reveal has its own motion.
   The cards of the form say the same trade to a screen reader, so the stage is art and hidden from one.
   A long team name truncates, and the tokens keep their width, so a row never wraps. */
export function TradeOnStage({ sides, show, rise = false }: { sides: StageSide[]; show: "count" | "tokens"; rise?: boolean }) {
  return (
    <ul aria-hidden="true" className="m-0 flex list-none flex-col p-0 tablet:max-w-stage">
      {sides.map((side, row) => (
        // The anchor sets the place of the weight of this side, so the mesh of the wait and of the reveal dips under its row.
        <li
          key={side.id}
          data-mesh-anchor
          className={`flex min-h-touch items-center gap-sp-3 py-sp-1 ${row > 0 ? "border-t border-rule-dark" : ""}`}
        >
          <Avatar src={side.avatar ?? AVATAR_FALLBACK} size="ring" className="flex-none rounded-full bg-chip-dark object-cover" />
          <span data-stage-team className="min-w-0 flex-1 truncate text-row leading-tight font-extrabold tracking-snug text-on-dark">
            {side.team}
          </span>
          {/* "gets" is small and sits near the glow of the corner on a phone, so it takes the brighter second tone and keeps 4.5:1 in the wait. */}
          <span className="flex-none font-mono text-label font-bold tracking-wide text-on-dark-2 uppercase">gets</span>
          {/* The tokens column keeps the width of 3 faces and a count, so "gets" lines up in each row. */}
          <span className="flex min-w-stage-tokens flex-none justify-end">
            {show === "count" ? <Count side={side} /> : <Tokens side={side} row={row} rise={rise} />}
          </span>
        </li>
      ))}
    </ul>
  );
}
