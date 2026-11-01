/**
 * The Roster chapter of a manager page: the four slot ranks of the roster grade, one line each, in the file's order.
 * Each line reads as "RB · 2nd of 12 · deep". A roster with no grade shows one quiet line.
 */
import { Reveal } from "@/components/parts/reveal";
import { Chapter } from "@/components/parts/chapter";
import { Label } from "@/components/parts/label";
import { ordinal } from "@/lib/format/format";
import { stagger } from "@/lib/motion";
import type { Manager, SlotRank } from "@/lib/manager-types";

/* One line: the position as the quiet label, the rank as the one emphasis, and the depth word in the quiet color.
   The separators sit in the quiet color, so the rank stays the one thing in ink.
   The line enters at its place in the stagger when the chapter reveals, with the reveal timing. */
function SlotLine({ slot, index, teams }: { slot: SlotRank; index: number; teams: number }) {
  return (
    <li>
      <Reveal delay={stagger(index)} className="flex items-baseline gap-sp-2 tabular-nums">
      <span className="w-sp-6 flex-none text-label font-semibold tracking-caps text-mute uppercase">{slot.position}</span>
      <span className="text-meta text-mute">{" · "}</span>
      <span>
        <span className="text-body font-extrabold text-ink">{ordinal(slot.rank)}</span>
        <span className="text-meta font-semibold text-mute">{` of ${teams}`}</span>
      </span>
      <span className="text-meta text-mute">{" · "}</span>
      <span className="text-meta text-mute">{slot.depth}</span>
      </Reveal>
    </li>
  );
}

/* A slot rank ranks the teams of the league, so each line reads out of the count of teams. */
export function Roster({ manager, teams }: { manager: Manager; teams: number }) {
  return (
    // The id and the heading match the roster entry of MANAGER_CHAPTERS. This file does not import the list,
    // because manager-chapters imports this file and the two must not form a loop.
    <Chapter reveal id="roster">
      <Label heading>Roster</Label>
      {manager.grade ? (
        // The gap gives each line air, so the four ranks read as four groups.
        <ol className="m-0 flex list-none flex-col gap-sp-3 p-0">
          {manager.grade.slots.map((slot, i) => (
            <SlotLine key={slot.position} slot={slot} index={i} teams={teams} />
          ))}
        </ol>
      ) : (
        <p className="m-0 text-body text-mute">No grade yet.</p>
      )}
    </Chapter>
  );
}
