/**
 * The report tile of the home page: one big fact of the midseason report and a link to it, in the shape of the R3 tile.
 * The home page shows it after the takeover ends, for the rest of the season.
 */
import type { Midseason } from "../schema/midseason-types";

/* The whole card is one link, so the tap target is the card. The arrow is drawn, because axe cannot read the contrast of a glyph. */
export function ReportTile({ report, href }: { report: Midseason; href: string }) {
  const { label, value, note } = report.tile;
  return (
    <a
      href={href}
      className="press group gap-x-sp-3 rounded-card border-rule bg-card p-sp-4 text-ink grid grid-cols-[minmax(0,1fr)_auto] items-center border no-underline"
    >
      <span className="gap-sp-1 flex min-w-0 flex-col">
        <span className="text-meta tracking-caps text-accent-ink font-mono leading-tight font-bold uppercase">
          {`${report.season} Midseason Report`}
        </span>
        <span className="text-meta tracking-caps text-mute font-mono leading-tight uppercase">
          {label}
        </span>
        <b className="text-score font-mono leading-tight tabular-nums">{value}</b>
        <span className="text-lead group-hover:text-accent-ink leading-tight">{note}</span>
      </span>
      <svg
        aria-hidden="true"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="text-mute"
      >
        <path d="M5 12h14M13 6l6 6-6 6" />
      </svg>
    </a>
  );
}
