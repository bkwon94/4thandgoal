/**
 * The Suggestion chips above the ask box: "More" leads one row, then the 3 Suggestions of Your team, each with only a
 * short name of its Topic. A first tap on a chip shows the full name and the fact in a strip under the row, and a second
 * tap opens the Topic. "More" opens the list of all 14 Topics from its pill, so no Topic is ever out of reach. Until the
 * picks are in, 3 quiet placeholder chips hold their place.
 */
"use client";

import { AnimatePresence, motion, useIsPresent } from "framer-motion";
import { type ComponentProps, useId, useState } from "react";
import { ChevronDownIcon } from "lucide-react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { closeKeyboard, keepFocus } from "./keyboard-tap";
import { FAST, GLIDE, MORE_SPRING, QUICK, SMOOTH, STAGGER, fadeIn, morphId, staggerOf } from "./motion";
import { TOPICS, type Topic } from "./topics";

/* A chip keeps its place when the row changes: a chip that leaves fades out, and the others glide to their new place. */
const CHIP_GLIDE = { type: "spring", bounce: 0, duration: 0.4 } as const;

/* One Suggestion chip. A chip that leaves, such as a tapped chip while it morphs into its question, hides from a screen
   reader and takes no second tap, so a quick double tap never opens its Topic twice. */
function SuggestionChip(props: ComponentProps<typeof motion.button>) {
  const present = useIsPresent();
  return <motion.button {...props} aria-hidden={present ? undefined : true} disabled={!present || undefined} />;
}

export function Suggestions({
  picks,
  facts,
  moreOpen,
  onMore,
  onPick,
  askFirst,
}: {
  // null until the browser reads the day, so the placeholder chips show in place of the chips.
  picks: string[] | null;
  facts: Record<string, string>;
  moreOpen: boolean;
  onMore: (open: boolean) => void;
  onPick: (key: string) => void;
  // The front door asks for the passphrase before the first tap shows a fact. It returns true when it took the tap, and
  // it runs `then` once the manager types the passphrase.
  askFirst?: (then: () => void) => boolean;
}) {
  const off = useMotionOff();
  const panelId = useId();
  const stripId = useId();
  // The key of the chip whose fact shows in the strip. The tap is the reveal, not a long press: a long press is hard to
  // find on the web, and it fights the text callout of iOS (decision 02).
  const [shown, setShown] = useState<string | null>(null);
  // A pick keeps the focus through the press, so the dock holds still until the click lands. Then the keyboard closes.
  const pick = (key: string) => {
    setShown(null);
    onPick(key);
    closeKeyboard();
  };
  // The first tap shows the fact and keeps the keyboard, as "More" does. The second tap on the same chip opens it.
  // The strip takes the place of the "More" panel, so a chip tap closes the panel.
  const reveal = (key: string) => {
    setShown(key);
    if (moreOpen) onMore(false);
  };
  const tap = (key: string) => {
    if (shown === key) return pick(key);
    if (askFirst?.(() => reveal(key))) return;
    reveal(key);
  };
  const topics = (picks ?? []).map((key) => TOPICS.find((topic) => topic.key === key)).filter((topic): topic is Topic => !!topic);
  // The strip shows only while its chip is in the row and the "More" panel is shut.
  const strip = moreOpen ? undefined : topics.find((topic) => topic.key === shown);
  return (
    // No gap here: the strip and the panel each carry their own 8px above, so a shut strip adds no height to the foot.
    <div className="flex flex-col">
      {/* The row is one line at every state of the Thread, so the Thread gets the screen (decision 02). A chip shows
          only a short name of its Topic, and each pill keeps a full 16px side pad, so the text never touches its border.
          A narrow screen may not fit "More" and 3 chips, so the row scrolls sideways and a chip may wait past the right
          edge until a swipe. A chip never shrinks and never cuts its name. The bleed keeps the last chip clear of the
          gutter. The 4px pad above and below gives the press scale and the focus ring room in the scroll box, and the negative
          margin keeps the row one 44px chip high. */}
      <div
        role="group"
        aria-label="Suggestions"
        aria-busy={picks === null || undefined}
        className="-mx-gutter -my-sp-1 flex snap-x scroll-px-gutter flex-nowrap gap-sp-2 overflow-x-auto overscroll-x-contain px-gutter py-sp-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
      >
        <button
          type="button"
          aria-expanded={moreOpen}
          aria-controls={panelId}
          onMouseDown={keepFocus}
          onClick={() => {
            setShown(null);
            onMore(!moreOpen);
          }}
          className="press door-sheen flex min-h-touch flex-none snap-start items-center gap-sp-1 rounded-pill border border-door-hair bg-card px-sp-4 text-body leading-tight font-semibold text-ink transition-colors duration-150 hover-fine:bg-raised aria-expanded:border-ink aria-expanded:bg-raised"
        >
          <span>More</span>
          <ChevronDownIcon
            aria-hidden
            className={`size-sp-4 flex-none text-mute transition-transform duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] motion-reduce:transition-none ${moreOpen ? "-scale-y-100" : ""}`}
            strokeWidth={2.25}
          />
        </button>
        {picks === null && (
          // The placeholders hold the size of a chip, with one still bar for the name. They do not pulse, so the dock
          // stays quiet for the moment until the chips land.
          <div aria-hidden className="contents">
            {[0, 1, 2].map((index) => (
              <div
                key={index}
                data-placeholder=""
                className="flex min-h-touch w-28 min-w-0 flex-initial items-center rounded-pill border border-door-hair bg-card px-sp-4 opacity-60"
              >
                <span className="h-sp-3 w-full rounded-pill bg-raised" />
              </div>
            ))}
          </div>
        )}
        <AnimatePresence initial={false} mode="popLayout">
          {topics.map((topic, index) => (
            <SuggestionChip
              key={topic.key}
              type="button"
              layout={!off}
              // The chip and the question of its Answer share one id, so a tap morphs the chip into the question.
              layoutId={off ? undefined : morphId(topic.key)}
              // The name leads the label, so a voice command by the name finds the chip, and the fact follows it.
              aria-label={`${topic.name}: ${facts[topic.key]}`}
              aria-expanded={strip?.key === topic.key}
              aria-controls={stripId}
              onMouseDown={keepFocus}
              onClick={() => tap(topic.key)}
              initial={off ? { opacity: 0 } : { opacity: 0, scale: 0.97 }}
              animate={off ? { opacity: 1 } : { opacity: 1, scale: 1 }}
              exit={off ? { opacity: 0, transition: fadeIn(QUICK) } : { opacity: 0, scale: 0.97, transition: fadeIn(QUICK) }}
              transition={off ? fadeIn(FAST, index * STAGGER) : { ...CHIP_GLIDE, layout: GLIDE, opacity: fadeIn(FAST, index * STAGGER) }}
              className="press door-sheen flex min-h-touch flex-none snap-start items-center rounded-pill border border-door-hair bg-card px-sp-4 text-left transition-colors duration-150 hover-fine:bg-raised aria-expanded:border-ink aria-expanded:bg-raised"
            >
              <span aria-hidden className="whitespace-nowrap text-body leading-tight font-semibold text-ink">
                {topic.chip}
              </span>
            </SuggestionChip>
          ))}
        </AnimatePresence>
      </div>
      <div id={stripId}>
        <AnimatePresence initial={false}>
          {strip && (
            // The strip grows the foot from 0 to its height, so the row above it rises with it and never jumps. With
            // motion off, the height jumps and only the opacity fades.
            <motion.div
              key="strip"
              className="overflow-hidden"
              initial={off ? { opacity: 0 } : { opacity: 0, height: 0 }}
              animate={off ? { opacity: 1, transition: fadeIn(FAST) } : { opacity: 1, height: "auto", transition: fadeIn(FAST) }}
              exit={off ? { opacity: 0, transition: fadeIn(QUICK) } : { opacity: 0, height: 0, transition: fadeIn(QUICK) }}
            >
              <div className="pt-sp-2">
                <motion.button
                  type="button"
                  aria-label={`Open ${strip.name}`}
                  onMouseDown={keepFocus}
                  onClick={() => pick(strip.key)}
                  // The strip drops from the row on --distance-micro with --blur-small, so it reads as the chip opening,
                  // and it leaves faster than it came. With motion off, only the opacity moves.
                  initial={off ? false : { y: -4, filter: "blur(2px)" }}
                  animate={off ? undefined : { y: 0, filter: "blur(0px)", transition: fadeIn(FAST) }}
                  exit={off ? undefined : { y: -4, filter: "blur(2px)", transition: fadeIn(QUICK) }}
                  className="press door-sheen relative flex min-h-touch w-full items-center gap-sp-3 rounded-tile border border-door-hair bg-card px-sp-4 py-sp-2 text-left transition-colors duration-150 hover-fine:bg-raised"
                >
                  {/* A tap on another chip cross-fades the fact in place with a soft blur, both at once and with no move
                      (Text swap soft). The old fact leaves the flow, so the strip never grows for the overlap. */}
                  <span className="relative min-w-0 flex-1">
                    <AnimatePresence initial={false} mode="popLayout">
                      {/* The chip shows a short name, so the strip shows the full name of the Topic over its fact. */}
                      <motion.span
                        key={strip.key}
                        initial={off ? { opacity: 0 } : { opacity: 0, filter: "blur(2px)" }}
                        animate={off ? { opacity: 1 } : { opacity: 1, filter: "blur(0px)" }}
                        exit={off ? { opacity: 0 } : { opacity: 0, filter: "blur(2px)" }}
                        transition={{ duration: QUICK, ease: "easeInOut" }}
                        className="block text-meta leading-tight text-ink"
                      >
                        <span className="font-semibold">{strip.name}</span>{" "}
                        <span className="font-mono tabular-nums">{facts[strip.key]}</span>
                      </motion.span>
                    </AnimatePresence>
                  </span>
                  <span aria-hidden className="flex-none text-meta leading-tight font-semibold text-ink">
                    Open →
                  </span>
                </motion.button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      <AnimatePresence initial={false}>
        {moreOpen && (
          <motion.div
            key="more"
            id={panelId}
            // The panel springs open from the More pill at its top left, so it reads as the pill opening (Morph Navbar).
            // It starts from --scale-large and --distance-micro up, small enough to read as the pill, and settles on a
            // hair of bounce. The fade and the blur stay on --duration-fast, so the spring never flashes the content.
            style={{ transformOrigin: "top left" }}
            initial={off ? { opacity: 0 } : { opacity: 0, scale: 0.96, y: -4, filter: "blur(2px)" }}
            animate={
              off
                ? { opacity: 1, transition: fadeIn(FAST) }
                : { opacity: 1, scale: 1, y: 0, filter: "blur(0px)", transition: { ...MORE_SPRING, opacity: fadeIn(FAST), filter: fadeIn(FAST) } }
            }
            exit={off ? { opacity: 0, transition: fadeIn(QUICK) } : { opacity: 0, scale: 0.99, filter: "blur(2px)", transition: { duration: QUICK, ease: SMOOTH } }}
            className="door-lift mt-sp-2 overflow-hidden rounded-card border border-door-hair bg-card"
          >
            <ul aria-label="All Topics" className="m-0 flex max-h-more list-none flex-col overflow-y-auto overscroll-contain p-sp-1">
              {TOPICS.map((topic, index) => {
                const fact = facts[topic.key];
                // A live Topic opens with the API. Until then its row shows, so no Topic is missing, but it takes no tap.
                const ready = fact !== undefined;
                return (
                  <motion.li
                    key={topic.key}
                    initial={off ? { opacity: 0 } : { opacity: 0, y: 4 }}
                    animate={off ? { opacity: 1 } : { opacity: 1, y: 0 }}
                    transition={fadeIn(FAST, 0.04 + staggerOf(index))}
                  >
                    <button
                      type="button"
                      disabled={!ready}
                      aria-label={ready ? `${topic.name}: ${fact}` : `${topic.name}: opens soon`}
                      onMouseDown={keepFocus}
                      onClick={() => pick(topic.key)}
                      className="press flex min-h-touch w-full flex-col items-start justify-center gap-sp-0 rounded-tile px-sp-3 py-sp-2 text-left transition-colors duration-150 hover-fine:enabled:bg-raised disabled:cursor-default"
                    >
                      {/* The name over its fact, as on a chip, so a long fact never cuts its number. */}
                      <span data-topic-name="" className={`text-body leading-tight font-semibold ${ready ? "text-ink" : "text-mute"}`}>
                        {topic.name}
                      </span>
                      <span className="max-w-full truncate font-mono text-meta leading-tight text-mute tabular-nums">{ready ? fact : "Opens soon"}</span>
                    </button>
                  </motion.li>
                );
              })}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
