# 09: The hooks folder and `useRequest`

**What to build:** A hooks folder holds the motion hook and the hydration hook. One new hook, `useRequest`, holds the run id, the abort controller, and the unmounted guard. The trade form, the trade finder, and the analyzer call it instead of their own copies. The focus-on-open and the open-close states stay inline.

**Blocked by:** 06

**Status:** done

- [ ] The three analyzer components have no `AbortController` of their own.
- [ ] `useRequest` has a test for a stale response after a second call and for an unmount during a call.
- [ ] The existing analyzer tests pass with no change to what they read.
- [ ] `out/` has no diff against `main`.

## Comments

- 2026-10-31: merged into `main` from branch `modular-09-hooks`, commits 15e288c and f78157a. 526 tests. `useRequest` gives `start()` and `drop()`; the trade form and the finder keep their own timeout text. The analyzer's refresh after a 422 now lets the last started run win, where before the last finished run won; both fetch the same rosters. Two reviewers passed it after one fix pass.
