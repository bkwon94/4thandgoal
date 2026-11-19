# packages/sim/site/lib: the client of the What-if route

## Knows

- The client of the What-if route in `what-if-api.ts`, and the port `WhatIfApi` that the sim page calls.
- A cancel of a call by its signal, so a new tap stops the call before it.
- A failed call as a `WhatIfError` with its status, or the status 0 when no answer came.

## Ports

- The What-if route of the API, at `<url>/clients/<slug>/sim/what-if`.

## Does not do

- It reads no env and no config. The app builds the target from its config.
- It owns no shape. The route in `apps/api/src/cornerstone_api/what_if.py` owns the answer, and `schema/what-if.ts` follows it.
