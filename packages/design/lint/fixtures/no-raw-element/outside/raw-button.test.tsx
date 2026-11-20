/**
 * A lint fixture: a test file outside the ui folder that renders a raw button.
 * The element rule exempts test files, so the lint passes it.
 */
export function Part() {
  return <button type="button">Go</button>;
}
