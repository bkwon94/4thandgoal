/**
 * The byte budget of the two font files of the look (AT-36). The font test holds the source files to it, and the
 * export check holds the built files to it, so one value sets both.
 */

/* The cap of each font file, in bytes, by its folder name. A new weight or the full range of an axis breaks a cap. */
export const FONT_CAPS: Record<string, number> = { "space-grotesk": 24_000, "jetbrains-mono": 33_000 };

/* The cap of the sum of the font files, in bytes. The two files of the decision cost 53,660. */
export const FONT_TOTAL = 56_000;
