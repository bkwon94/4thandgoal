# 09: The hooks folder and `useRequest`

**What to build:** A hooks folder holds the motion hook and the hydration hook. One new hook, `useRequest`, holds the run id, the abort controller, and the unmounted guard. The trade form, the trade finder, and the analyzer call it instead of their own copies. The focus-on-open and the open-close states stay inline.

**Blocked by:** 06

**Status:** ready-for-agent

- [ ] The three analyzer components have no `AbortController` of their own.
- [ ] `useRequest` has a test for a stale response after a second call and for an unmount during a call.
- [ ] The existing analyzer tests pass with no change to what they read.
- [ ] `out/` has no diff against `main`.
