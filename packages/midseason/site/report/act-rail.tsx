/**
 * The chapter rail of the midseason report: one link per act, in a strip that stays at the top under the top band.
 * It holds plain fragment links, so a tap jumps to its act with scripts off too.
 */
import type { Act } from "../schema/midseason-types";

/* The rail sits under the top band: a 44px row, 8px above and below, and its 1px rule at the bottom. */
const UNDER_THE_BAND = "top-[calc(var(--spacing-touch)+2*var(--spacing-sp-2)+1px)]";

export function ActRail({ acts }: { acts: Pick<Act, "key" | "title">[] }) {
  return (
    <nav
      aria-label="Chapters"
      className={`border-rule bg-page sticky z-30 border-b ${UNDER_THE_BAND}`}
    >
      {/* The three acts share the row. On a phone a long label wraps between its words, so the row never scrolls sideways. */}
      <ul className="max-w-page gap-sp-1 px-gutter tablet:px-0 m-0 mx-auto flex list-none py-0">
        {acts.map((act) => (
          <li key={act.key} className="flex-1">
            <a
              href={`#${act.key}`}
              className="min-h-touch px-sp-1 py-sp-1 text-meta tracking-caps text-ink-2 hover-fine:text-accent-ink flex h-full items-center justify-center text-center font-mono leading-tight font-bold uppercase no-underline"
            >
              {act.title}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
