/**
 * A lint fixture: an arbitrary spacing value in a plain string, outside a className, a cn(...) call, and a template.
 * The value rule reads only class strings, so it passes this file.
 */
const NOTE = "p-[3px] is the old pad of the note";

export const Note = () => <p title={NOTE}>Note</p>;
