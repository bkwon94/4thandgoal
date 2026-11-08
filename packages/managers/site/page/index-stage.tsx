/**
 * The stage of the Index list: the hero of the Managers index on desktop, in the six hero slots, for the row in the stage.
 * A new row wipes in from the top over the old one. It zooms down to size, after the method of the Team Roster item (ADR 0028).
 */
"use client";

import { useEffect, useRef, useState } from "react";
import { Hero } from "@cpc/design/parts/hero";
import { Tile } from "@cpc/design/parts/tile";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { GradeDial } from "./grade-dial";
import type { IndexRow } from "./index-list";
import { RACE_WORDS } from "./race-group";

/* The milliseconds of the wipe and the zoom, the duration of the item. An old layer drops a beat after the new layer lands. */
const SWAP_MS = 1000;

/* One layer of the stage. The key grows with each swap, so React mounts a new layer and its wipe plays once. */
type Layer = { row: IndexRow; key: number };

/* The hero of one row: the race word, the team name, the facts, the four arcs, the grade letter, and the manager link. */
function StageHero({ row, teams }: { row: IndexRow; teams: number }) {
  return (
    <Hero
      label={`Stage: ${row.name}`}
      level={2}
      eyebrow={row.group === null ? undefined : RACE_WORDS[row.group]}
      // The stage is narrower than a page hero, and a long one-word name, such as Mitseeker5000, would run under the meta.
      // A break anywhere lets the name wrap inside its column.
      title={<span className="[overflow-wrap:anywhere]">{row.name}</span>}
      meta={row.facts}
      feature={row.grade ? <GradeDial parts={row.grade.parts} teams={teams} size="small" tone="hero" /> : undefined}
      stats={<Tile tone="hero" label="Grade" value={row.grade ? row.grade.letter : "—"} />}
      action={
        // A full pill and a 44px tap target in the brand color, as the manager link of the rankings hero.
        <a
          href={row.href}
          className="press inline-flex min-h-touch items-center justify-center rounded-pill bg-accent px-sp-6 text-body font-bold text-on-dark no-underline"
        >
          Manager page
          <span className="sr-only">{` of ${row.name}`}</span>
        </a>
      }
    />
  );
}

/* The layers stack in one grid cell, so the stage takes the height of its tallest layer and no layer jumps.
   The newest layer is on top. A layer under it is hidden from a screen reader and the keyboard, so the stage reads one team.
   With motion off the stage holds one layer, so a swap shows the new row at once. */
export function IndexStage({ row, teams }: { row: IndexRow; teams: number }) {
  const off = useMotionOff();
  const [layers, setLayers] = useState<Layer[]>([{ row, key: 0 }]);
  const next = useRef(0);

  // A new row adds a layer on top and keeps the two layers under it, as in the item. The old layers drop after the wipe.
  useEffect(() => {
    if (layers[layers.length - 1].row.id === row.id) return;
    next.current += 1;
    const key = next.current;
    if (off) {
      setLayers([{ row, key }]);
      return;
    }
    setLayers((now) => [...now.slice(-2), { row, key }]);
    const timer = setTimeout(() => setLayers((now) => now.filter((layer) => layer.key >= key)), SWAP_MS + 50);
    return () => clearTimeout(timer);
    // The effect runs on a new row only. The layers it reads are the layers of the render of that row.
  }, [row.id, off]);

  return (
    <div className="grid">
      {layers.map((layer, i) => {
        const top = i === layers.length - 1;
        return (
          <div
            key={layer.key}
            className="ix-layer [grid-area:1/1]"
            // The first layer of the page enters with no wipe. Each later top layer wipes in, and each layer under it sinks.
            // With motion off no layer wipes in.
            data-in={top && layer.key > 0 && !off ? "" : undefined}
            data-under={top ? undefined : ""}
            aria-hidden={top ? undefined : true}
            inert={!top}
          >
            <StageHero row={layer.row} teams={teams} />
          </div>
        );
      })}
    </div>
  );
}
