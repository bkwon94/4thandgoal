/**
 * A lint fixture: only a variant, a layout value, and a motion value, each with brackets.
 * The value rule test expects design/no-arbitrary-value to pass it.
 */
export const Panel = () => (
  <div className="grid-cols-[1fr_auto] transition-[opacity,transform] data-[state=open]:opacity-100 grid">Panel</div>
);
