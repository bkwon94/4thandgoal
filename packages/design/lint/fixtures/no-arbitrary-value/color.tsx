/**
 * A lint fixture: an arbitrary color value in a className.
 * The value rule test expects design/no-arbitrary-value to fail it at line 6.
 */
export const Chip = () => (
  <span className="text-ink bg-[color-mix(in_srgb,var(--color-accent)_28%,var(--color-card))]">Chip</span>
);
