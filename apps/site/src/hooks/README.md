# src/hooks: the React hooks of the API calls

## Knows

- `useRequest`, the guard of a call from a component to the API: the run id, the abort controller, and the unmounted flag.

## Ports

None.

## Does not do

- It calls no API. The component calls `src/lib/api.ts`, and `useRequest` only guards the answer.
- It holds no motion hook. `packages/design/site/hooks/` holds `useMotionOff` and `useMarkHydrated`.
- It knows no league term.
- It reads no file, no env, and no config.
