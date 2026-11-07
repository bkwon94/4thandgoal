/**
 * The slots of an egg word for one manager: the letters the manager holds, the open slots, and the slot of a new letter.
 * The claim sheet and the claim hero card read them, so a tile sits in the same slot on both.
 */
import type { Board } from "../lib/api";

/* One slot of an egg word: a letter the manager holds, an open slot, or the slot where the new letter lands. */
export type Slot = { letter: string; kind: "held" | "open" | "new" };

/* The slots of the word. Each held letter takes the first free slot of that letter, and the new letter takes the next one.
   With no free slot for the new letter, no slot is "new". */
export function slotsOf(word: string, held: string[], letter: string | null): Slot[] {
  const slots: Slot[] = [...word].map((each) => ({ letter: each, kind: "open" }));
  const take = (each: string, kind: Slot["kind"]) => {
    const free = slots.find((slot) => slot.kind === "open" && slot.letter === each);
    if (free) free.kind = kind;
    return free !== undefined;
  };
  for (const each of held) take(each, "held");
  if (letter !== null) take(letter, "new");
  return slots;
}

/* True when the word has a free slot for the letter after the letters the manager holds. */
export function hasOpenSlot(word: string, held: string[], letter: string): boolean {
  return slotsOf(word, held, letter).some((slot) => slot.kind === "new");
}

/* The letters of the manager in each egg word of the board. */
export function heldLetters(word: Board["words"][number], rosterId: number): string[] {
  return word.managers.find((manager) => manager.roster_id === rosterId)?.letters ?? [];
}

/* The line of the leader of an egg word: the manager with the most letters, the first of a tie. */
export function leaderLine(word: Board["words"][number]): string {
  const leader = word.managers.reduce<Board["words"][number]["managers"][number] | null>(
    (best, manager) => (manager.letters.length > (best?.letters.length ?? 0) ? manager : best),
    null,
  );
  if (leader === null) return "No letters yet.";
  return `${leader.team} leads with ${leader.letters.length} of ${word.word.length}`;
}
