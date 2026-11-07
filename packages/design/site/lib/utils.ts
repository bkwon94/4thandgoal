/**
 * Builds the cn class-name helper for the shadcn components.
 * Components import it from @cpc/design/lib/utils.
 */
import { createCn } from "cn/config"

// The text scale in globals.css adds size names that cn does not know.
// Without them cn reads text-label as a color and drops it next to text-accent.
export const cn = createCn({
  extend: {
    // The spacing scale in globals.css adds names that cn does not know.
    // Without them cn keeps both mb-sp-3 and mb-sp-1 instead of the last one.
    theme: {
      spacing: ["sp-0", "sp-1", "sp-2", "sp-3", "sp-4", "sp-5", "sp-6", "gutter", "award", "logo", "divider", "avatar", "touch", "headshot", "chevron", "val-col", "standings-rank", "rankings-col"],
      // The movement colors and the page breakpoint, so cn sorts each name into its group.
      color: ["move-up", "move-down"],
      breakpoint: ["page"],
      // The radii of the look, so cn keeps only the last one, such as rounded-report over the rounded-card of a card.
      radius: ["hero", "card", "tile", "pill", "report"],
    },
    classGroups: {
      "font-size": [{ text: ["label", "meta", "row", "body", "lead", "stat", "score", "headline", "hero"] }],
    },
  },
})
