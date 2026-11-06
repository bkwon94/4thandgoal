/**
 * The big week line of a page with no hero: a label and an optional number in the red accent.
 * It takes no file read, so a client component can render it.
 */

/* The big week line under the top band. The number, when given, takes the red accent. */
export function WeekLine({ label, number }: { label: string; number?: number }) {
  return (
    <div className="text-headline leading-none font-black tracking-tight">
      {number === undefined ? (
        label
      ) : (
        <>
          {/* One string, so React writes one text node and the browser kerns the label as one run. */}
          {`${label} `}
          <span className="text-accent">{number}</span>
        </>
      )}
    </div>
  );
}
