/**
 * The dark title page that opens each act of the midseason report: the act number and the act title on the hero surface.
 * The hero sits on the band color in both themes, so each title page stays dark in the light theme too.
 */
import { Hero } from "@cpc/design/parts/hero";
import { stableId } from "@cpc/design/lib/stable-id";

/* The act number as a roman numeral, as a book numbers its acts. The report has three acts. */
const NUMERALS = ["I", "II", "III"];

export function ActTitle({ index, title, headingId }: { index: number; title: string; headingId: string }) {
  const number = `Act ${NUMERALS[index] ?? index + 1}`;
  return (
    // The act number is the eyebrow and the act title the title, at level 2 with the look of the opener title.
    // The id sits on a span in the title, so the section of the act takes its name from the act title.
    <Hero
      label={`${number}: ${title}`}
      className="rounded-report py-sp-6 tablet:min-h-[12rem]"
      eyebrow={number}
      title={<span id={headingId} {...stableId("heading", title)}>{title}</span>}
      level={2}
    />
  );
}
