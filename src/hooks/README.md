# hooks: the React hooks that the components share

## Knows

- `useMotionOff`, the one reduced-motion switch of the site.
- `useMarkHydrated`, which marks the root once the client script runs, so Framer Motion owns each reveal.
- `useRequest`, the guard of a call from a component to the API: the run id, the abort controller, and the unmounted flag.

## Ports

None.

## Does not do

- It calls no API. The component calls `lib/api.ts`, and `useRequest` only guards the answer.
- It builds no motion props. `lib/motion.ts` holds the timings and the helpers.
- It knows no league term.
- It reads no file, no env, and no config.
