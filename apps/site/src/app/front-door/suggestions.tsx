/**
 * The Suggestion chips above the ask box: "More" leads the row, then the 3 Suggestions of Your team, each with its Topic
 * name and one fact. "More" opens the list of all 13 Topics from its pill, so no Topic is ever out of reach. Until the
 * picks are in, 3 quiet placeholder chips hold their place.
 */
"use client";

import { AnimatePresence, motion, useIsPresent } from "framer-motion";
import { type ComponentProps, useId } from "react";
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
  wrap,
  onMore,
  onPick,
}: {
  // null until the browser reads the day, so the placeholder chips show in place of the chips.
  picks: string[] | null;
  facts: Record<string, string>;
  moreOpen: boolean;
  wrap: boolean;
  onMore: (open: boolean) => void;
  onPick: (key: string) => void;
}) {
  const off = useMotionOff();
  const panelId = useId();
  // A pick keeps the focus through the press, so the dock holds still until the click lands. Then the keyboard closes.
  const pick = (key: string) => {
    onPick(key);
    closeKeyboard();
  };
  const topics = (picks ?? []).map((key) => TOPICS.find((topic) => topic.key === key)).filter((topic): topic is Topic => !!topic);
  return (
    <div className="flex flex-col gap-sp-2">
      {/* With an empty Thread the row wraps, so all 3 chips show whole at each width and none hides past the edge (AT-4).
          On a phone "More" and the first chip share the first line, and the other two chips share the second. With
          Answers in the Thread the row sits in the dock at the foot, and two lines of chips would hide the Answers, so
          it stays one row that scrolls sideways (the PRD). The bleed keeps the last chip clear of the gutter. A chip
          grows from a base of 9rem up to its cap, and a long fact cuts with an ellipsis after its number. */}
      <div
        role="group"
        aria-label="Suggestions"
        aria-busy={picks === null || undefined}
        className={
          wrap
            ? "flex flex-wrap gap-sp-2"
            : "-mx-gutter flex snap-x scroll-px-gutter flex-nowrap gap-sp-2 overflow-x-auto overscroll-x-contain px-gutter pb-sp-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
        }
      >
        <button
          type="button"
          aria-expanded={moreOpen}
          aria-controls={panelId}
          onMouseDown={keepFocus}
          onClick={() => onMore(!moreOpen)}
          className={`press door-sheen flex min-h-touch flex-none ${wrap ? "" : "snap-start"} items-center gap-sp-1 rounded-pill border border-door-hair bg-card px-sp-4 text-body leading-tight font-semibold text-ink transition-colors duration-150 hover-fine:bg-raised aria-expanded:border-ink aria-expanded:bg-raised`}
        >
          <span>More</span>
          <ChevronDownIcon
            aria-hidden
            className={`size-sp-4 flex-none text-mute transition-transform duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] motion-reduce:transition-none ${moreOpen ? "-scale-y-100" : ""}`}
            strokeWidth={2.25}
          />
        </button>
        {picks === null && (
          // The placeholders hold the size of a chip, with two still bars for the name and the fact. They do not pulse,
          // so the dock stays quiet for the moment until the chips land.
          <div aria-hidden className="contents">
            {[0, 1, 2].map((index) => (
              <div
                key={index}
                data-placeholder=""
                className={`flex min-h-touch max-w-chip ${wrap ? "min-w-0 flex-[1_1_9rem]" : "w-36 flex-none"} flex-col justify-center gap-sp-1 rounded-tile border border-door-hair bg-card px-sp-4 py-sp-2 opacity-60`}
              >
                <span className="h-sp-3 w-3/4 rounded-pill bg-raised" />
                <span className="h-sp-2 w-1/2 rounded-pill bg-raised" />
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
              aria-label={`${topic.name}: ${facts[topic.key]}`}
              onMouseDown={keepFocus}
              onClick={() => pick(topic.key)}
              initial={off ? { opacity: 0 } : { opacity: 0, scale: 0.97 }}
              animate={off ? { opacity: 1 } : { opacity: 1, scale: 1 }}
              exit={off ? { opacity: 0, transition: fadeIn(QUICK) } : { opacity: 0, scale: 0.97, transition: fadeIn(QUICK) }}
              transition={off ? fadeIn(FAST, index * STAGGER) : { ...CHIP_GLIDE, layout: GLIDE, opacity: fadeIn(FAST, index * STAGGER) }}
              className={`press door-sheen flex min-h-touch max-w-chip ${wrap ? "min-w-0 flex-[1_1_9rem]" : "flex-none snap-start"} flex-col items-start justify-center gap-sp-0 rounded-tile border border-door-hair bg-card px-sp-4 py-sp-2 text-left transition-colors duration-150 hover-fine:bg-raised`}
            >
              <span aria-hidden className="max-w-full truncate text-body leading-tight font-semibold text-ink">
                {topic.name}
              </span>
              <span aria-hidden className="max-w-full truncate font-mono text-meta leading-tight text-mute tabular-nums">
                {facts[topic.key]}
              </span>
            </SuggestionChip>
          ))}
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
            className="door-lift overflow-hidden rounded-card border border-door-hair bg-card"
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
