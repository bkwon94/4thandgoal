/**
 * A lint fixture: a parts file that exports a constant, a helper, and a type, but no component.
 * The doc rule reads only a file that exports a component, so it passes this file with no use lines.
 */
export const PART_GAP = "gap-sp-2";

export function partLabel(name: string): string {
  return `The ${name} part`;
}

export type PartTone = "win" | "loss";
