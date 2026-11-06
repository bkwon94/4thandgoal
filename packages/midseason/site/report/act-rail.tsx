/**
 * The chapter rail of the midseason report: one link per act, in a strip that stays at the top under the top band.
 * It holds plain fragment links, so a tap jumps to its act with scripts off too.
 */
import type { Act } from "../schema/midseason-types";

/* The rail sits under the top band: a 44px row, 8px above and below, and its 1px rule at the bottom. */
const UNDER_THE_BAND = "top-[calc(var(--spacing-touch)+2*var(--spacing-sp-2)+1px)]";

export function ActRail({ acts }: { acts: Pick<Act, "key" | "title">[] }) {
  return (
    <nav aria-label="Chapters" className={`sticky z-30 border-b border-rule bg-page ${UNDER_THE_BAND}`}>
      {/* The three acts share the row. On a phone a long label wraps between its words, so the row never scrolls sideways. */}
      <ul className="mx-auto m-0 flex max-w-page list-none gap-sp-1 px-gutter py-0 tablet:px-0">
        {acts.map((act) => (
          <li key={act.key} className="flex-1">
            <a
              href={`#${act.key}`}
              className="flex h-full min-h-touch items-center justify-center px-sp-1 py-sp-1 text-center font-mono text-meta leading-tight font-bold tracking-caps text-ink-2 uppercase no-underline hover-fine:text-accent-ink"
            >
              {act.title}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
