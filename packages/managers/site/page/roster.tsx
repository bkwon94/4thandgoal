/**
 * The Roster chapter of a manager page: a tile for each position slot of the roster grade, with its rank and its depth,
 * then the rank of each of the four grade parts. A roster with no grade shows one quiet line.
 */
import { Reveal } from "@cpc/design/parts/reveal";
import { Chapter } from "@cpc/design/parts/chapter";
import { Label } from "@cpc/design/parts/label";
import { Tile } from "@cpc/design/parts/tile";
import { ordinal } from "@cpc/design/format/format";
import { stagger } from "@cpc/design/lib/motion";
import type { ManagerGrade, Manager } from "../schema/manager-types";
import { PART_NAMES } from "./part-names";
import { stableId, stableKey } from "@cpc/design/lib/stable-id";

/* A tile for each slot, in the file's order. Each tile enters at its place in the stagger when the chapter reveals.
   A phone fits two tiles per row, so the rank and the depth never wrap. */
function SlotTiles({ grade, teams }: { grade: ManagerGrade; teams: number }) {
  return (
    <ul aria-label="Slot Ranks" className="m-0 grid list-none grid-cols-2 gap-sp-2 p-0 tablet:grid-cols-4">
      {grade.slots.map((slot, i) => (
        <li key={slot.position}>
          <Reveal delay={stagger(i)} className="h-full">
            <Tile
              label={slot.position}
              value={ordinal(slot.rank)}
              note={`of ${teams} · ${slot.depth}`}
              stable={stableKey("roster-slot", slot.position)}
              className="h-full"
            />
          </Reveal>
        </li>
      ))}
    </ul>
  );
}

/* One line for each part of the grade: the part name in the quiet color, and the rank as the one emphasis.
   The managers file carries no weight of a part, so the line shows the rank only. */
function GradeParts({ grade, teams }: { grade: ManagerGrade; teams: number }) {
  return (
    <ol aria-label="Grade Parts" className="m-0 mt-sp-5 flex list-none flex-col p-0 tabular-nums">
      {grade.parts.map((part) => (
        <li
          key={part.key}
          className="flex items-baseline justify-between gap-sp-3 border-t border-rule py-sp-2 first:border-t-0"
          {...stableId("roster-part", part.key)}
        >
          <span className="text-body text-ink-2">{PART_NAMES[part.key]}</span>
          <span className="font-mono text-body font-bold text-ink">
            {ordinal(part.rank)}
            <span className="text-meta font-normal text-mute">{` of ${teams}`}</span>
          </span>
        </li>
      ))}
    </ol>
  );
}

/* A slot rank and a part rank rank the teams of the league, so each reads out of the count of teams. */
export function Roster({ manager, teams }: { manager: Manager; teams: number }) {
  return (
    // The id and the heading match the roster entry of MANAGER_CHAPTERS. This file does not import the list,
    // because manager-chapters imports this file and the two must not form a loop.
    <Chapter reveal id="roster">
      {/* The meta size keeps the heading over the text floor of 11px on a phone. */}
      <Label heading className="text-meta">Roster</Label>
      {manager.grade ? (
        <>
          <SlotTiles grade={manager.grade} teams={teams} />
          <GradeParts grade={manager.grade} teams={teams} />
        </>
      ) : (
        <div className="m-0 text-body text-mute">No grade yet.</div>
      )}
    </Chapter>
  );
}
