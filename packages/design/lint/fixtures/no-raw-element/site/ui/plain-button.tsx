/**
 * A lint fixture: a file in a copy of the ui folder that renders a raw button and a raw dialog.
 * The element rule exempts the ui folder, so the lint passes it.
 */
export function Part() {
  return (
    <dialog open>
      <button type="button">Go</button>
    </dialog>
  );
}
