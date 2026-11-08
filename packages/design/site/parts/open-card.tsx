/**
 * The Open card: the one part that opens and closes a card in place, after the method of the Showcase Card item (ADR 0028).
 * The height grows on a spring, the details come into focus from a blur a beat behind it, and a chevron under the card turns.
 */
"use client";

import { ChevronDown } from "lucide-react";
import { type CSSProperties, type ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react";
import { useMotionOff } from "../hooks/use-motion-off";
import { springCurve } from "../lib/spring";
import { cn } from "../lib/utils";
import { Card } from "./card";

/* Seconds to open or close, the duration of the item. The curve, the chevron, and the rise of the details share it. */
const OPEN_CARD_DURATION = 0.45;

/* The curve is the same for every card, so the sampler runs once. */
const SPRING = springCurve();

/* The link at the foot of an open panel. The hidden label reads after the label, for a screen reader only. */
export type OpenCardAction = { href: string; label: string; hiddenLabel?: string };

/* Data attributes to spread on an element of the card. */
type Marks = Record<`data-${string}`, string>;

type OpenCardProps = {
  // The id of the panel. The toggles name it in aria-controls, and a check can open one card by it.
  panelId: string;
  // The closed card. It sits inside the toggle button, so it holds plain text and no link.
  head: ReactNode;
  // The classes of the head button, because the layout of the head is the one part that differs per card.
  headClassName?: string;
  overview?: ReactNode;
  chips?: readonly ReactNode[];
  text?: string | null;
  action?: OpenCardAction | null;
  // Extra panel content after the text and before the action, such as the Grade dial of an Index list row.
  children?: ReactNode;
  // Data attributes of the head toggle, the panel, and the text, such as the stable ids that the egg hunt names.
  // The panel takes its marks only while open, so a closed card shows no target of its panel.
  headMarks?: Marks;
  panelMarks?: Marks;
  textMarks?: Marks;
  // The element of the card. A card in a list is an li.
  as?: "li" | "div";
  // "card" draws the card frame and the chevron row. "row" is a row of a ledger: no frame and no chevron, so a closed row
  // stays one line high, and the head is the one toggle.
  look?: "card" | "row";
  // A controlled card takes open and onOpenChange. An uncontrolled card keeps its own state.
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
};

export function OpenCard({
  panelId,
  head,
  headClassName,
  overview,
  chips = [],
  text,
  action,
  children,
  headMarks,
  panelMarks,
  textMarks,
  as: Element = "li",
  look = "card",
  open: controlled,
  onOpenChange,
}: OpenCardProps) {
  const [own, setOwn] = useState(false);
  const open = controlled ?? own;
  const off = useMotionOff();
  // The panel stays hidden while the card is closed and at rest. On a close it stays shown until the height is down.
  const [shut, setShut] = useState(!open);
  const panel = useRef<HTMLDivElement>(null);

  const setOpen = (next: boolean) => {
    if (controlled === undefined) setOwn(next);
    onOpenChange?.(next);
  };

  // An open shows the panel at once. A close hides it when the close ends, or at once with motion off.
  useEffect(() => {
    if (open) {
      setShut(false);
      return;
    }
    if (off) {
      setShut(true);
      return;
    }
    const timer = setTimeout(() => setShut(true), OPEN_CARD_DURATION * 1000);
    return () => clearTimeout(timer);
  }, [open, off]);

  // React 19 writes a plain hidden attribute and drops the value "until-found", so the value goes on here, before the paint.
  // A plain hidden hides the text from find-in-page, and "until-found" keeps it findable. inert would hide it from find-in-page in Chromium.
  useLayoutEffect(() => {
    if (shut) panel.current?.setAttribute("hidden", "until-found");
  }, [shut]);

  // The browser fires beforematch on a hidden="until-found" panel before it shows a match inside it, so a find opens the card.
  // The latest setOpen sits in a ref, so the listener binds once and still calls the current state.
  const openRef = useRef(setOpen);
  openRef.current = setOpen;
  useEffect(() => {
    const element = panel.current;
    if (!element) return;
    const onMatch = () => openRef.current(true);
    element.addEventListener("beforematch", onMatch);
    return () => element.removeEventListener("beforematch", onMatch);
  }, []);

  // With motion off, every duration is 0, so the card reaches its end state at once (ADR 0028).
  const vars = { "--oc-dur": off ? "0s" : `${OPEN_CARD_DURATION}s`, "--oc-spring": SPRING } as CSSProperties;
  const row = look === "row";

  const body = (
    <>
      <button
        type="button"
        aria-expanded={open}
        aria-controls={panelId}
        {...headMarks}
        onClick={() => setOpen(!open)}
        className={cn(
          "press flex min-h-touch w-full cursor-pointer flex-col gap-sp-3 border-0 bg-transparent p-sp-4 pb-0 text-left text-inherit [-webkit-tap-highlight-color:transparent]",
          row && "p-0",
          headClassName,
        )}
      >
        {head}
      </button>
      <div className="oc-body">
        <div id={panelId} ref={panel} hidden={shut} className="oc-inner">
          <div {...(open ? panelMarks : {})} className="oc-panel mx-sp-2 mt-sp-3 flex flex-col gap-sp-3 rounded-tile bg-raised p-sp-4">
            {overview && <p className="m-0 text-lead leading-tight font-bold text-ink">{overview}</p>}
            {chips.length > 0 && (
              <ul className="m-0 flex list-none flex-wrap gap-sp-2 border-b border-rule p-0 pb-sp-3">
                {chips.map((chip, index) => (
                  <li
                    key={index}
                    className="inline-flex items-center gap-sp-2 rounded-pill bg-card px-sp-3 py-sp-1 font-mono text-meta leading-tight text-ink-2 tabular-nums"
                  >
                    {chip}
                  </li>
                ))}
              </ul>
            )}
            {text && <p className="m-0 max-w-measure text-lead leading-body text-ink-2" {...textMarks}>{text}</p>}
            {children}
            {/* The pill has a solid fill under its label, because text on the frosted blur fails the axe floor. */}
            {action && (
              <a
                href={action.href}
                className="press inline-flex min-h-touch w-fit items-center rounded-pill bg-ink px-sp-5 text-body font-bold text-page no-underline"
              >
                {/* On a fine pointer the label rolls up to a copy of itself. The copy is CSS content, so a reader hears the label once. */}
                <span className="oc-roll" data-label={action.label}>
                  <span>{action.label}</span>
                </span>
                {action.hiddenLabel && <span className="sr-only">{action.hiddenLabel}</span>}
              </a>
            )}
          </div>
        </div>
      </div>
      {!row && (
        <button
          type="button"
          aria-expanded={open}
          aria-controls={panelId}
          aria-label={open ? "Hide the details" : "Show the details"}
          onClick={() => setOpen(!open)}
          className="grid min-h-touch w-full cursor-pointer place-items-center border-0 bg-transparent p-0 text-mute [-webkit-tap-highlight-color:transparent]"
        >
          <ChevronDown aria-hidden="true" className="oc-chevron size-sp-5" strokeWidth={1.6} />
        </button>
      )}
    </>
  );

  return (
    <Element data-open={open} className="open-card list-none" style={vars}>
      {row ? (
        body
      ) : (
        <Card edge={open} className="overflow-hidden p-0">
          {body}
        </Card>
      )}
    </Element>
  );
}
