# packages/design/site/hooks: the motion hooks and the clock hook that the parts and the shell share

## Knows

- `useMotionOff`, the one reduced-motion switch of the site.
- `useMarkHydrated`, which marks the root once the client script runs, so Framer Motion owns each reveal.
- `useDeadline`, the state of Deadline week and the countdown text now, from the Lock that the page gives. It ticks each second.

## Ports

None.

## Does not do

- It builds no motion props. `site/lib/motion.ts` holds the timings and the helpers.
- It knows no league term.
- It reads no file, no env, and no config.
