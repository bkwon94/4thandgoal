/**
 * A lint fixture: an arbitrary padding value on the second line of a template literal, after a variant.
 * The value rule test expects design/no-arbitrary-value to fail it at line 7.
 */
const BASE = "flex";
const SHEET = `${BASE} gap-sp-2
  md:pb-[calc(var(--spacing-sp-4)+env(safe-area-inset-bottom))]`;

export const Sheet = () => <div className={SHEET} />;
