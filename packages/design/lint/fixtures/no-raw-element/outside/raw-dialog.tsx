/**
 * A lint fixture: a file outside the ui folder that renders a raw dialog.
 * The element rule test expects design(no-raw-element) to fail it at line 6.
 */
export function Part() {
  return <dialog open>Hi</dialog>;
}
