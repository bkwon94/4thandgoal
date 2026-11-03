/**
 * The big week line of the masthead: a label and an optional number in the red accent.
 * It lives apart from the masthead, so a client component can render it without the build-time file reads of the masthead.
 */

/* The big week line in the masthead. The number, when given, takes the red accent. */
export function WeekLine({ label, number }: { label: string; number?: number }) {
  return (
    <div className="text-headline leading-none font-black tracking-tight">
      {number === undefined ? (
        label
      ) : (
        <>
          {/* One string, so React writes one text node and the browser kerns the label as one run. */}
          {`${label} `}
          <span className="text-red">{number}</span>
        </>
      )}
    </div>
  );
}
