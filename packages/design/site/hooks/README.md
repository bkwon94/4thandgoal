# packages/design/site/hooks: the motion hooks that the parts and the shell share

## Knows

- `useMotionOff`, the one reduced-motion switch of the site.
- `useMarkHydrated`, which marks the root once the client script runs, so Framer Motion owns each reveal.

## Ports

None.

## Does not do

- It builds no motion props. `site/lib/motion.ts` holds the timings and the helpers.
- It knows no league term.
- It reads no file, no env, and no config.
