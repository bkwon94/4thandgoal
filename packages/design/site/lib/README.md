# packages/design/site/lib: the theme, the motion timings, the usage count, the stable ids, and the cn helper

## Knows

- The theme store and the boot script that sets the stored theme before the first paint, in `theme.ts`.
- The first paint of a brand from its set count, in `theme.ts`: a two-set brand paints light and runs the boot script.
- The motion timings and the helpers of Framer Motion, in `motion.ts`.
- The count URL and the event call of GoatCounter, in `usage.ts`.
- The `cn` class-name helper of the shadcn primitives, in `utils.ts`.
- The stable id of an element that the egg hunt can name, and the marks of the state that an egg check reads, in `stable-id.ts`. Each content package tags its elements with them, so no content package imports the eggs package.

## Ports

- Local storage, through `theme.ts`.
- GoatCounter, through `usage.ts`.

## Does not do

- It holds no component and returns no markup.
- It holds no React hook. `site/hooks/` holds the hooks.
- It reads no file and no env.
