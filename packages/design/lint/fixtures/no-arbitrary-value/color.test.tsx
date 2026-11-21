/**
 * A lint fixture: a test file that renders the arbitrary color value of color.tsx.
 * The value rule exempts test files, so the lint passes it.
 */
export const Chip = () => (
  <span className="text-ink bg-[color-mix(in_srgb,var(--color-accent)_28%,var(--color-card))]">Chip</span>
);
