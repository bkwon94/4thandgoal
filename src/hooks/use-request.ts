/**
 * The guard of a call from a component to the API: the run id, the abort controller, and the unmounted flag.
 * A late answer from an old run or from a gone component must not set state.
 */
import { useEffect, useRef } from "react";

export type Run = {
  // The caller passes the signal to the call, and it aborts the controller on its own timeout.
  controller: AbortController;
  // False once a later run starts, a drop happens, or the component unmounts.
  isCurrent: () => boolean;
};

export function useRequest() {
  // A late answer from an old run must not overwrite the state of a new one.
  const runId = useRef(0);
  // The unmount effect aborts the call in flight, so a closed page does not wait on the API.
  const controllerRef = useRef<AbortController | null>(null);
  const unmounted = useRef(false);

  useEffect(() => {
    // React strict mode runs the cleanup and the effect again on mount, so the effect resets the flag.
    unmounted.current = false;
    return () => {
      unmounted.current = true;
      controllerRef.current?.abort();
    };
  }, []);

  /* Starts a run. The run before it stays in flight, but its answer is stale. */
  function start(): Run {
    const id = ++runId.current;
    const controller = new AbortController();
    controllerRef.current = controller;
    return { controller, isCurrent: () => id === runId.current && !unmounted.current };
  }

  /* Makes the run in flight stale with no new run, for a change of input that clears the old answer. */
  function drop() {
    runId.current += 1;
  }

  return { start, drop };
}
