/**
 * The dark title page that opens each act of the midseason report: the act number and the act title on the hero surface.
 * The hero sits on the band color in both themes, so each title page stays dark in the light theme too.
 */
import { Hero } from "@cpc/design/parts/hero";

/* The act number as a roman numeral, as a book numbers its acts. The report has three acts. */
const NUMERALS = ["I", "II", "III"];

export function ActTitle({ index, title, headingId }: { index: number; title: string; headingId: string }) {
  const number = `Act ${NUMERALS[index] ?? index + 1}`;
  return (
    <Hero label={`${number}: ${title}`} className="rounded-report py-sp-6 tablet:min-h-[12rem]">
      {/* Each line sits on a plate, so the grid and the glow never sit under a letter. */}
      <div className="flex flex-col items-start gap-sp-3">
        <span className="plate font-mono text-meta leading-tight font-bold tracking-caps text-accent-text uppercase">
          {number}
        </span>
        <h2 id={headingId} className="plate m-0 text-headline leading-tight font-bold tracking-tight">
          {title}
        </h2>
      </div>
    </Hero>
  );
}
