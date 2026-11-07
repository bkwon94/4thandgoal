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
      className="press group grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-sp-3 rounded-card border border-rule bg-card p-sp-4 text-ink no-underline"
    >
      <span className="flex min-w-0 flex-col gap-sp-1">
        <span className="font-mono text-meta leading-tight font-bold tracking-caps text-accent-ink uppercase">
          {`${report.season} Midseason Report`}
        </span>
        <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">{label}</span>
        <b className="font-mono text-score leading-tight tabular-nums">{value}</b>
        <span className="text-lead leading-tight group-hover:text-accent-ink">{note}</span>
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
