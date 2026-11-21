/**
 * A lint fixture: a hex color in a style object, an rgb() color in a class string, an oklch() color in a template.
 * The raw color rule test expects one failure at each of lines 6, 7, and 8, and none elsewhere.
 */
export const Part = () => (
  <div style={{ color: "#ff0000" }}>
    <span className="bg-[rgb(0_0_0)]" />
    <span title={`oklch(0.5 0.1 20)`} />
  </div>
);
