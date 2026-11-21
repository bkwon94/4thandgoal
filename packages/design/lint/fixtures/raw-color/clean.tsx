/**
 * A lint fixture: a file with no color literal.
 * The raw color rule test expects it to pass. The anchor "#section" is not a color.
 */
export const Part = () => (
  <a href="#section" style={{ color: "var(--color-ink)" }} className="bg-ink">
    Link
  </a>
);
