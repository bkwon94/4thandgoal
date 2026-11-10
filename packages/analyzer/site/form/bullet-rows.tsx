/**
 * The Bullet rows of one side: each row shows its Mark and its claim, and a tap opens the fact under it as an accordion.
 * The rows sit in For, Against, and Even bands. The analyzer result and the Finder card both render the rows from here.
 */
"use client";

import { ChevronDown } from "lucide-react";
import { useId, useState } from "react";
import type { Bullet, Mark as MarkKind } from "../lib/analyze-types";
import { cn } from "@cpc/design/lib/utils";
import { openId, stableId } from "@cpc/design/lib/stable-id";

/* The Mark of a Bullet. The glyph is decorative, so a screen reader hears the word. Each band heading takes the color of its Mark. */
const MARKS = {
  for: { symbol: "▲", band: "For", color: "text-accent-ink" },
  against: { symbol: "▼", band: "Against", color: "text-ink" },
  even: { symbol: "–", band: "Even", color: "text-mute" },
} as const;

/* The band order of decision 05: the good, then the bad, then the even, so the two reads sit apart. */
const BAND_ORDER: readonly MarkKind[] = ["for", "against", "even"];

function Mark({ mark }: { mark: MarkKind }) {
  const shown = MARKS[mark];
  return (
    <span className={cn("text-center font-black", shown.color)}>
      <span aria-hidden="true">{shown.symbol}</span>
      <span className="sr-only">{mark}</span>
    </span>
  );
}

/* One Bullet as a row. The row is the button of an accordion, so a tap opens its fact under it.
   The height grows from 0fr to 1fr, the one height method of the site, and the chevron flips with scaleY(-1).
   The open state and the close state take the same 250 ms with the brand ease-out, so a tap back feels as quick.
   The fact fades in from a 2 px blur with the height, so no half-drawn text shows. Reduced motion opens it at once.
   A closed fact is inert and hidden from a screen reader, so the reader hears only the open facts.
   index is the place of the Bullet in its side, so the stable id stays the same in any band order. */
function BulletRow({ bullet, idBase, index }: { bullet: Bullet; idBase: string | number; index: number }) {
  const [open, setOpen] = useState(false);
  const factId = useId();
  return (
    <li {...stableId("bullet", idBase, index)} data-open={open} className="group/row border-b border-rule last:border-b-0">
      <button
        type="button"
        aria-expanded={open}
        aria-controls={factId}
        onClick={() => setOpen(!open)}
        {...openId("bullet", idBase, index)}
        className="grid min-h-touch w-full cursor-pointer grid-cols-[var(--spacing-sp-4)_minmax(0,1fr)_auto] items-start gap-x-sp-1 px-sp-1 py-sp-2 text-left text-lead text-ink-2 focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-accent"
      >
        <Mark mark={bullet.mark} />{" "}
        <span data-bullet-text>{bullet.text}</span>
        <ChevronDown
          aria-hidden="true"
          className="mt-sp-0 size-sp-5 text-mute transition-transform duration-250 ease-out group-data-[open=true]/row:[transform:scaleY(-1)] motion-reduce:transition-none [&_path]:[vector-effect:non-scaling-stroke]"
        />
      </button>
      <div
        id={factId}
        aria-hidden={!open}
        inert={!open}
        className="grid grid-rows-[0fr] transition-[grid-template-rows] duration-250 ease-out group-data-[open=true]/row:grid-rows-[1fr] motion-reduce:transition-none"
      >
        <div className="min-h-0 overflow-hidden">
          {/* The padding sits on the inner box, never on the 0fr track, so the closed row keeps no strip of height. */}
          <p className="m-0 pr-sp-1 pb-sp-3 pl-sp-6 text-meta text-mute opacity-0 blur-[2px] transition-[opacity,filter] duration-250 ease-out group-data-[open=true]/row:opacity-100 group-data-[open=true]/row:blur-none motion-reduce:transition-none">
            {bullet.fact_text}
          </p>
        </div>
      </div>
    </li>
  );
}

/* One band: its heading and its rows. The heading names the group, so a screen reader hears "For" before the rows. */
function Band({ mark, rows, idBase }: { mark: MarkKind; rows: { bullet: Bullet; index: number }[]; idBase: string | number }) {
  const headingId = useId();
  return (
    <div role="group" aria-labelledby={headingId}>
      <div id={headingId} className={cn("mb-sp-1 text-label font-bold tracking-caps uppercase", MARKS[mark].color)}>
        {MARKS[mark].band}
      </div>
      <ul className="m-0 list-none border-t-2 border-ink p-0">
        {rows.map(({ bullet, index }) => (
          <BulletRow key={`${bullet.fact_id}-${index}`} bullet={bullet} idBase={idBase} index={index} />
        ))}
      </ul>
    </div>
  );
}

/* The Bullets of one side in For, Against, and Even bands. A band with no Bullet does not show.
   idBase names the side in the stable ids, such as the roster id on the analyzer or the pick on the Finder. */
export function BulletRows({ bullets, idBase }: { bullets: Bullet[]; idBase: string | number }) {
  const indexed = bullets.map((bullet, index) => ({ bullet, index }));
  return (
    <div className="flex max-w-measure flex-col gap-sp-4">
      {BAND_ORDER.map((mark) => {
        const rows = indexed.filter(({ bullet }) => bullet.mark === mark);
        return rows.length > 0 ? <Band key={mark} mark={mark} rows={rows} idBase={idBase} /> : null;
      })}
    </div>
  );
}
